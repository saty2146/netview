#!flask/bin/python 
# -*- coding: utf-8 -*- 

from flask import *
from forms import VlanForm, ArpForm, UpdateForm, MacForm
from flask import request
from datetime import datetime
import pandas as pd
import numpy as np
import re, glob, os, subprocess, time
import csv, pygal

ip_whitelist = ['81.89.63.129', '81.89.63.130', '81.89.63.131', '81.89.63.132', '81.89.63.133', '81.89.63.134', '81.89.63.135', '81.89.63.136', '81.89.63.137', '81.89.63.138', '81.89.63.139', '81.89.63.140', '81.89.63.141', '81.89.63.142', '81.89.63.143', '81.89.63.144', '81.89.63.145', '81.89.63.146', '81.89.63.147', '81.89.63.148', '81.89.63.149', '81.89.63.150', '127.0.0.1']

app = Flask(__name__)
app.config.from_object('config')
filespath = os.path.realpath('files')

def valid_ip(): 
    client = request.remote_addr 
    if client in ip_whitelist: 
        return True 
    else: 
        return False

def get_data():

    p = subprocess.Popen(["python", "./run.py"], stdout=subprocess.PIPE)
    out, err = p.communicate()

    return out

def last_update():
    newest = max(glob.glob(os.path.join(filespath,'*.csv')), key=os.path.getmtime)
    result = str(time.ctime(os.path.getmtime(newest)))
    return result

def num_of_rows(filename):
    with open(filename, 'r') as f:
        row_count = sum(1 for row in f)
    return (row_count - 1)

@app.route("/run")
def run():
    return render_template('run.html', subprocess_output=get_data())

@app.route("/macs", methods=['GET', 'POST'])
def show_mac():
    update = last_update()
    form = MacForm()
    files = glob.glob(os.path.join(filespath,'mac*.csv'))
    files.sort(key=os.path.getmtime, reverse = True)
    filename = [os.path.basename(i) for i in (files)]
    ids = [i for i in range(len(filename))]
    form.file_option.choices = list(zip(ids, filename))

    if form.validate_on_submit():
        find_item = form.find_item.data.strip()
        file_id = form.file_option.data
        selected_file = [f[1] for f in form.file_option.choices if f[0] == file_id]
        data = pd.read_csv(os.path.join(filespath, selected_file[0]), dtype={'vlan': str})
    else:
        find_item = None
        newest = max(glob.glob(os.path.join(filespath,'mac*.csv')), key=os.path.getmtime)
    
        data = pd.read_csv(newest, dtype={'vlan': str})

    machost = request.args.get('host', default = 'six1')
    hosts = set(list(data['host']))

    if find_item:

        columns = ['host', 'vlan', 'type', 'mac', 'iface']
        mask = np.column_stack([data[col].str.contains(find_item, flags=re.IGNORECASE, na=False) for col in columns])
        data = data.loc[mask.any(axis=1)]
    else:
        data = data[data.host == machost]
    return render_template('macs.html',table=data.to_html(index=False,
        classes='table table-hover'), title = 'MACs', form = form, hosts = hosts, find_item = find_item, update = update )

@app.route("/vlans", methods=['GET', 'POST'])
def show_vlans():
    update = last_update()
    form = VlanForm()
    if form.validate_on_submit():
        post = form.post.data.strip()
        unused_vlans = False

    else:
        post = None

    unused_vlans = request.args.get('unused_vlans', default = False)
    l2_circuit = request.args.get('l2_circuit', default = False)
    newest = max(glob.glob(os.path.join(filespath,'vlan*.csv')), key=os.path.getmtime)
    data = pd.read_csv(newest, dtype={'vlan': str})
    data.info()

    print unused_vlans
    unused_list = ['0','-']
    l2_circuit_list = ['°','-']
    if unused_vlans:
        data = data[data.six1d.isin(unused_list) & data.six2d.isin(unused_list)
                & data.sit1d.isin(unused_list) & data.sit2d.isin(unused_list) &
                data.shc31d.isin(unused_list) & data.shc32d.isin(unused_list) &
                data.n31d.isin(unused_list) & data.n32d.isin(unused_list) &
                data.n41d.isin(unused_list) & data.n42d.isin(unused_list)]
    elif l2_circuit:
        data = data[data.six1.isin(l2_circuit_list) & data.six2.isin(l2_circuit_list)
                & data.sit1.isin(l2_circuit_list) & data.sit2.isin(l2_circuit_list) &
                data.shc31.isin(unused_list) & data.shc32.isin(unused_list) &
                data.n31.isin(l2_circuit_list) & data.n32.isin(l2_circuit_list) &
                data.n41.isin(l2_circuit_list) & data.n42.isin(l2_circuit_list)]

    if post:
        columns = ['vlan', 'name', 'six1', 'six2', 'sit1', 'sit2', 'shc31', 'shc32', 'n31', 'n32', 'n41', 'n42']
        mask = np.column_stack([data[col].str.contains(post, flags=re.IGNORECASE, na=False) for col in columns])
        data = data.loc[mask.any(axis=1)]
    else:
        pass
    return render_template('vlans.html',table=data.to_html(index=False, classes='table table-hover'), title = 'Vlans', form=form, post = post, update = update, unused = 'unused', circuit = 'circuit')

@app.route("/arps", methods=['GET', 'POST'])
def show_arp():
    update = last_update()
    form = ArpForm()
    files = glob.glob(os.path.join(filespath,'arp*.csv'))
    files.sort(key=os.path.getmtime, reverse = True)
    filename = [os.path.basename(i) for i in (files)]
    ids = [i for i in range(len(filename))]
    form.file_option.choices = list(zip(ids, filename))

    if form.validate_on_submit():
        find_item = form.find_item.data.strip()
        file_id = form.file_option.data
        print find_item, file_id
        selected_file = [f[1] for f in form.file_option.choices if f[0] == file_id]
        print selected_file
        data = pd.read_csv(os.path.join(filespath, selected_file[0]))
    else:
        find_item = None
        newest = max(glob.glob(os.path.join(filespath, 'arp*.csv')), key=os.path.getmtime)
        data = pd.read_csv(newest)

    arphost = request.args.get('host', default = 'six1')
    hosts = set(list(data['host']))

    if find_item:

        columns = ['host', 'ip', 'mac', 'iface']
        mask = np.column_stack([data[col].str.contains(find_item, flags=re.IGNORECASE, na=False) for col in columns])
        data = data.loc[mask.any(axis=1)]

    else:
        data = data[data.host == arphost]

    return render_template('arps.html',table=data.to_html(index=False,
        classes='table table-hover'), title = 'ARPs', form = form, hosts = hosts, find_item = find_item, update = update)

@app.route("/", methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def show_index():

    newest_vlan = max(glob.glob(os.path.join(filespath, 'vlan*.csv')), key=os.path.getmtime)
    newest_arp = max(glob.glob(os.path.join(filespath, 'arp*.csv')), key=os.path.getmtime)
    newest_mac = max(glob.glob(os.path.join(filespath, 'mac*.csv')), key=os.path.getmtime)

    update = last_update()
    num_of_vlans = num_of_rows(newest_vlan)
    num_of_arps = num_of_rows(newest_arp)
    num_of_macs = num_of_rows(newest_mac)

    files = glob.glob(os.path.join(filespath, 'vlan*.csv'))
    files.sort(key=lambda x: os.path.getmtime(x))
    every_ten_file = files[::15] + files[-1:]
    
    line_chart = pygal.Line(x_label_rotation = 20, show_x_labels=False)
    line_chart.title = "Vlan usage evolution"
    chart_values = [num_of_rows(x) for x in every_ten_file]

    date_values = [time.ctime(os.path.getmtime(x)) for x in every_ten_file]
    line_chart.x_labels = map(str, date_values)
    line_chart.add('Vlans', chart_values)
    chart = line_chart.render_data_uri()

    if valid_ip():
        return render_template('index.html', title = 'Home', update = update, num_of_vlans = num_of_vlans, num_of_arps = num_of_arps, num_of_macs = num_of_macs, chart=chart)
    else:
        return render_template('404.html', title = 'Not Found')

if __name__ == "__main__":
    app.run(debug=True, host='81.89.63.131')
