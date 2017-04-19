#!/usr/bin/python
"""
Get vlan_list and mac_table downloaded by get_vlan_info.py and create DataFrame
vlan information through all devices in one table
"""
import argparse
import re
import os
import sys
import pandas as pd
#from devices import devices
from myfiles.devices import devices

from time import gmtime, strftime, localtime
date_time = strftime("%d-%m-%Y_%H:%M:%S", localtime())

filepath = '/home/tibor/Dropbox/tibi/python/netview/scripts/files/'

def df_mac_table():

    columns = ['host','vlan','mac','type','age','iface','date']

    df = pd.DataFrame(index=None, columns=columns)

    for host in devices: 
        print ('Processing mac-address-table for %s' % host)
        header = True
        with open(host + '_mac_table.txt', 'r') as open_file:
            #lines = open_file.readlines()
            for line in open_file:
                line = line.rstrip("\n")
                if header:
                    if re.search(r'--------',line):
                        header = False
                    else:
                        continue
                else:
                    if re.search(r'Legend',line):
                        header = True
                        continue
                    line_list = line.split(" ")
                    line_list = filter(None, line_list)
                    if len(line_list) < 4:
                        continue
                    else:
                        line_list = filter(lambda name: name[:] != "*", line_list)
                        line_list = filter(lambda name: name[:] != "+", line_list)
                        line_list = filter(lambda name: name[:] != "R", line_list)
                        
                        if 'N/A' not in line and '---' not in line and 'igmp' not in line:
                            if devices[host]['device_type'] == 'cisco_ios':
                                line_list = line_list[0:3] + line_list[4:6]
                            else:
                                line_list = line_list[0:4] + line_list[6:7]

                            line_list.insert(0, host)
                            line_list.append(date_time)
                            df2 = pd.DataFrame([line_list], columns=columns)
                            df = df.append(df2)

                        else:
                            pass


    return (df)

def main():

    os.chdir('./rawfiles')
    df = df_mac_table()
    df = df.set_index('host')
    filename = 'mac_' + date_time + '.csv'
    os.chdir(filepath)
    df.to_csv(filename)
    #print(df.to_string())

if __name__ == "__main__":
    main()
