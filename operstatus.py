#testing line protocol using ifoperstatus
from easysnmp import Session, snmp_get, snmp_walk
import time
from netmiko import ConnectHandler

ips = {'R1':'192.168.122.11','R2':'192.168.122.12','R3':'192.168.122.13','R4':'192.168.122.14','R5':'192.168.122.15'}
neighbors = {'R1-fa0/0':'R2-fa0/0', 'R1-fa2/0':'R3-fa2/0', 'R1-fa3/0':'R5:fa3/0'}

session = Session(hostname='192.168.122.11', community='public', version=2)

def checklinkstatus():
    intindex=[] #list of interface index
    intnamedict={} #dictionary where key is interface index and value is interface name.
    item1=[] #status value
    intname=[] #list of interface names
    walkitems = session.walk('1.3.6.1.2.1.2.2.1.8')
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

while 1:

	indexname, statusvalue = checklinkstatus()
	print(statusvalue)
	print(indexname)
	for i in range(0,int(len(statusvalue))):
		if int(statusvalue[i]) != 1:
			print("Interface down detected. please check interface  "+ indexname[str(i+1)])
			sshsession()
			net_connect.enable()
			net_connect.config_mode()
			command = ["int "+intnamedict[str(i+1)], "shut", "no shut"]
			net_connect.send_config_set(command)
			indexname, statusvalue = checklinkstatus()
				if int(statusvalue[i]) != 1:
					print("Interface down detected. please check interface  "+ indexname[str(i+1)])
					oidnum1 = '1.3.6.1.2.1.2.2.1.5.'+str(i+1)
					speed1 = str(session.get(oidnum)).split()[1].split("=")[1]
					print(speed1)
					oidnum11 = '1.3.6.1.2.1.10.7.2.1.19.'+str(i+1)
					duplex1 = str(session.get(oidnum11)).split()[1].split("=")[1]
					neighborint = neighbors['R1-'+indexname[str(i+1)]].split('-')[1]
					neighborrouter = neighbors['R1-'+indexname[str(i+1)]].split('-')[0]
					session2 = Session(hostname=ips[neighborrouter], community='public', version=2)
					intindexvalue = session2.walk('1.3.6.1.2.1.31.1.1.1.1')
					intname1=[]
					intindex1=[]
					intnamedict={}
					for item in intindexvalue:
						intname1.append(str.replace(str(item).split()[1].split("=")[1], "'", ""))
						intindex1.append(str.replace(str.replace(str(item).split()[2].split(".")[11], "'", ""), ",", ""))
					for x in range(0, int(len(intindexvalue)-1)):
						intnamedict1[intindex1[x]] = intname1[x]
					for ind, int in intnamedict1.iteritems():
						if int == neighborint:
							oidnum2='1.3.6.1.2.1.2.2.1.5.'+str(ind)	
							oidnum22='1.3.6.1.2.1.10.7.2.1.19.'+str(ind)
					speed2 = str(session.get(oidnum2)).split()[1].split("=")[1]
					duplex2 = str(session.get(oidnum11)).split()[1].split("=")[1]
					if speed1 != speed2:
						net_connect2 = ConnectHandler(device_type='cisco_ios', ip=ips[neighborrouter],username='router', password='cisco', secret='cisco')
						net_connect.config_mode()
						commands = ['int f0/0', 'speed 100']
						net_connect.send_config_set(commands)
						net_connect2.config_mode()
						commands2 = ['int '+neighborint, 'speed 100']
						net_connect.send_config_set(commands2)
					if duplex1 != duplex2:
						net_connect2 = ConnectHandler(device_type='cisco_ios', ip=ips[neighborrouter],username='router', password='cisco', secret='cisco')
						net_connect.config_mode()
						commands = ['int f0/0', 'duplex full']
						net_connect.send_config_set(commands)
						net_connect2.config_mode()
						commands2 = ['int '+neighborint, 'duplex full']
						net_connect.send_config_set(commands2)
					indexname, statusvalue = checklinkstatus()
					if int(statusvalue[i]) != 1:
						print("Interface down detected. please check interface  "+ indexname[str(i+1)])
						print(net_connect.find_prompt())
						net_connect.enable()
						net_connect.config_mode()
						commands = ['int loopback100', 'ip address 100.100.100.100 255.255.255.255']
						output = net_connect.send_config_set(commands)					
						commands = ['do ping 100.100.100.100']
						output = net_connect.send_config_set(commands)
						result = output.splitlines()[6].split()[3]
						print(result)
						if result == 100:
							print("Please try replacing the cables and SFP. The following steps have been tried.\n Tried shutting and unshutting interfaces. \n Verified the speed and duplex on both ends to be the same. \n Verified the Routers ASIC to be fine.")
						else:
							print("Something is wrong with the router ASIC. Please look into it")						
					else:
						print("Interface "+ indexname[str(i+1)]+ " is up and running. Line protocol is up")
					
				else:
					print("Interface "+ indexname[str(i+1)]+ " is up and running. Line protocol is up")
		else:
			print(""Interface "+ indexname[str(i+1)]+ " is up and running. Line protocol is up")
	time.sleep(5)



