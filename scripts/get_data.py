#!/usr/bin/python
"""
Get useful vlan info from Cisco devices:

show vlan brief
show vlan counters
show mac address-table 

and write its to files for futher processing

"""

import os
from myfiles.devices import devices
from netmiko import ConnectHandler

def main():

    if os.path.exists('./rawfiles'):
        pass
    else:
        os.makedirs('./rawfiles')

    os.chdir('./rawfiles')

    for host in devices:
    
        net_connect = ConnectHandler(**devices[host])

        print ('Getting "show vlan brief" from %s' % host)
        output= net_connect.send_command_expect('show vlan brief | in active')
        with open(host + '_vlan_list.txt', 'w') as open_file:
            open_file.write(output)

        print ('Getting "show mac address-table" from %s' % host)
        output= net_connect.send_command_expect('show mac address-table')
        with open(host + '_mac_table.txt', 'w') as open_file:
            open_file.write(output)
 
        print ('Getting "show ip arp" from %s' % host)
        output= net_connect.send_command_expect('show ip arp')
        with open(host + '_arp_table.txt', 'w') as open_file:
            open_file.write(output)
  
    net_connect.disconnect()

if __name__ == "__main__":
    main()
