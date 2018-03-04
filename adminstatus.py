#testing admin status
from easysnmp import Session, snmp_get, snmp_walk
import time
from netmiko import ConnectHandler

ips = {'R1':'192.168.122.11','R2':'192.168.122.12','R3':'192.168.122.13','R4':'192.168.122.14','R5':'192.168.122.15'}

session = Session(hostname='192.168.122.11', community='public', version=2)



def checklinkstatus():
    intindex=[] #list of interface index
    intnamedict={} #dictionary where key is interface index and value is interface name.
    item1=[] #status value
    intname=[] #list of interface names
    walkitems = session.walk('1.3.6.1.2.1.2.2.1.7')
    walkitems1 = session.walk('1.3.6.1.2.1.31.1.1.1.1')
    for item in walkitems1:
        intname.append(str.replace(str(item).split()[1].split("=")[1], "'", ""))
        intindex.append(str.replace(str.replace(str(item).split()[2].split(".")[11], "'", ""), ",", ""))
    for x in range(0, int(len(walkitems1)-1)):
        intnamedict[intindex[x]] = intname[x]
    for x in range(0, int(len(walkitems)-1)):
        item1.append(str.replace(str(walkitems[x]).split()[1].split("=")[1], "'", ""))
    return intnamedict, item1;
def sshsession():
        net_connect = ConnectHandler(device_type='cisco_ios', ip='192.168.122.11',username='router', password='cisco', secret='cisco')
        print(net_connect.find_prompt())
        print(net_connect.enable())
        return net_connect;
while 1:

        indexname, statusvalue = checklinkstatus()
        print(statusvalue)
        print(indexname)
        for i in range(0,int(len(statusvalue))):
                if int(statusvalue[i]) != 1:
                        print("Interface down detected. please check interface  "+ indexname[str(i+1)])
                        net_connect = sshsession()
                        net_connect.enable()
                        net_connect.config_mode()
                        command = ["int "+indexname[str(i+1)], "no shut"]
                        output = net_connect.send_config_set(command)
                        print(output)
                        indexname, statusvalue = checklinkstatus()
                        print(statusvalue)
                        print(indexname)
                        if int(statusvalue[i]) != 1:
                                print("Interface down detected. please check interface  "+ indexname[str(i+1)]+" Interface still down. unable to bring it up. Human intervention required")
                        else:
                                print("Interface "+ indexname[str(i+1)]+ " was brought back up. It is up and running again!!. ")
                else:
                        print("Interface "+ indexname[str(i+1)]+ " is up and running. No link down detected yet")
        time.sleep(5)

