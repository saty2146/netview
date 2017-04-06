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

def df_arp_table():

    columns = ['host', 'ip', 'age', 'mac', 'iface','date']

    df = pd.DataFrame(index=None, columns=columns)
    for host in devices:
        print ('Processing arp table for %s' % host)
        header = 1 if devices[host]['device_type'] == 'cisco_ios' else 9 
    #for host in hosts: 
        with open(host + '_arp_table.txt', 'r') as open_file:
            lines = open_file.readlines()

            for line in lines[header:]:
                line = line.rstrip("\n")
                line_list = line.split(" ")
                line_list = filter(lambda name: name.lower() != "internet", line_list)
                line_list = filter(lambda name: name.lower() != "arpa", line_list)
                line_list = filter(lambda name: name.lower() != "incomplete", line_list)
                line_list = filter(None, line_list)
                
                if len(line_list) < 4 or len(line_list) > 6:
                    #print line_list
                    continue

                line_list = line_list[0:4]
                line_list.insert(0, host)
                line_list.append(date_time)

                df2 = pd.DataFrame([line_list], columns=columns)
                df = df.append(df2)


    return (df)

def main():
    
    os.chdir('./rawfiles')
    df = df_arp_table()
    df = df.set_index('host')
    #df.sort_index(inplace=True)
    filename = 'arp_' + date_time + '.csv'
    os.chdir('../files')
    df.to_csv(filename)
    #print(df.to_string())

if __name__ == "__main__":
    main()
