#!flask/bin/python 

from flask import *
from forms import VlanForm, ArpForm, UpdateForm, MacForm
from flask import request
from datetime import datetime
import pandas as pd
import numpy as np
import re, glob, os, subprocess, time
import csv

ip_whitelist = ['81.89.63.129', '81.89.63.131', '127.0.0.1']

app = Flask(__name__)
app.config.from_object('config')

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
    newest = max(glob.glob('./scripts/files/*.csv'), key=os.path.getmtime)
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
    files = glob.glob('./scripts/files/mac*.csv')
    files.sort(key=os.path.getmtime, reverse = True)
    filename = [os.path.basename(i) for i in (files)]
    ids = [i for i in range(len(filename))]
    form.file_option.choices = list(zip(ids, filename))

    if form.validate_on_submit():
        find_item = form.find_item.data.strip()
        file_id = form.file_option.data
        selected_file = [f[1] for f in form.file_option.choices if f[0] == file_id]
        data = pd.read_csv('./scripts/files/' + selected_file[0], dtype={'vlan': str})
    else:
        find_item = None
        newest = max(glob.glob('./scripts/files/mac*.csv'), key=os.path.getmtime)
    
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

    else:
        post = None

    newest = max(glob.glob('./scripts/files/vlan*.csv'), key=os.path.getmtime)
    data = pd.read_csv(newest, dtype={'vlan': str})
    data.info()

    if post:
        columns = ['vlan', 'name', 'six1', 'six2', 'sit1', 'sit2', 'shc31', 'shc32', 'n31', 'n32', 'n41', 'n42']
        mask = np.column_stack([data[col].str.contains(post, flags=re.IGNORECASE, na=False) for col in columns])
        data = data.loc[mask.any(axis=1)]
    else:
        pass
    return render_template('vlans.html',table=data.to_html(index=False,
        classes='table table-hover'), title = 'Vlans', form=form, post = post, update = update)

@app.route("/arps", methods=['GET', 'POST'])
def show_arp():
    update = last_update()
    form = ArpForm()
    files = glob.glob('./scripts/files/arp*.csv')
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
        data = pd.read_csv('./scripts/files/' + selected_file[0])
    else:
        find_item = None
        newest = max(glob.glob('./scripts/files/arp*.csv'), key=os.path.getmtime)
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

    newest_vlan = max(glob.glob('./scripts/files/vlan*.csv'), key=os.path.getmtime)
    newest_arp = max(glob.glob('./scripts/files/arp*.csv'), key=os.path.getmtime)
    newest_mac = max(glob.glob('./scripts/files/mac*.csv'), key=os.path.getmtime)

    update = last_update()
    num_of_vlans = num_of_rows(newest_vlan)
    num_of_arps = num_of_rows(newest_arp)
    num_of_macs = num_of_rows(newest_mac)

    if valid_ip():
        return render_template('index.html', title = 'Home', update = update, num_of_vlans = num_of_vlans, num_of_arps = num_of_arps, num_of_macs = num_of_macs)
    else:
        return render_template('404.html', title = 'Not Found')

if __name__ == "__main__":
    app.run(debug=True, host='81.89.63.131')
