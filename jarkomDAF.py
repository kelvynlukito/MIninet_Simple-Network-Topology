from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, UserSwitch, OVSKernelSwitch
from mininet.node import OVSController, CPULimitedHost
from mininet.cli import CLI
from mininet.link import TCLink, Link, Intf
from mininet.log import setLogLevel, info
from datetime import datetime
from mininet.util import pmonitor
from subprocess import *
from signal import SIGINT

import os
import time

class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

def Topologi():
	# Konfigurasi mininet
	Link = TCLink
	host = CPULimitedHost
	net = Mininet(link=Link, host = host)
	key = "net.mptcp.mptcp_enabled"

	# Konfigurasi host
	hostA = net.addHost('hostA') 


	hostB = net.addHost('hostB') 

	# Konfigurasi Router
	r1 = net.addHost('r1', cls=LinuxRouter) 
	r2 = net.addHost('r2', cls=LinuxRouter) 
	r3 = net.addHost('r3', cls=LinuxRouter) 
	r4 = net.addHost('r4', cls=LinuxRouter) 


	# Connection specification
	linkopts0 = dict(bw=0.5, delay='1ms', loss=0, max_queue_size=100, use_tbf=True)
	linkopts1 = dict(bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True)

	# Configuration network
	# Router <--> Router

	net.addLink(r1, r3, cls=TCLink, bw=0.5, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='r1-eth1', intfName2='r3-eth0') 
	net.addLink(r2, r4, cls=TCLink, bw=0.5, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='r2-eth0', intfName2='r4-eth1') 
	net.addLink(r1, r4, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='r1-eth2', intfName2='r4-eth2')
	net.addLink(r2, r3, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='r2-eth2', intfName2='r3-eth2')
	
	# Router <--> Host

	net.addLink(hostA, r1, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='hostA-eth0', intfName2='r1-eth0') 
	net.addLink(hostA, r2, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='hostA-eth1', intfName2='r2-eth1') 
	net.addLink(hostB, r3, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='hostB-eth0', intfName2='r3-eth1') 
	net.addLink(hostB, r4, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=100, use_tbf=True, intfName1='hostB-eth1', intfName2='r4-eth0') 
	net.build()
	'''
	print("* Setup quagga")
	for router in net.hosts:
		if router.name[0] == 'r':
			# config zebra and ripd
			router.cmd("zebra -f config/zebra/{0}zebra.conf -d -i /tmp/{0}zebra.pid > logs/{0}-zebra-stdout 2>&1".format(router.name))
			router.waitOutput()
			router.cmd("ripd -f config/rip/{0}ripd.conf -d -i /tmp/{0}ripd.pid > logs/{0}-ripd-stdout 2>&1".format(router.name), shell=True)
			router.waitOutput()
			#print(f"Starting zebra and rip on {router.name}")
	'''
	r1.cmd("sysctl net.ipv4.ip_forward=1")
	r2.cmd("sysctl net.ipv4.ip_forward=1")
	r3.cmd("sysctl net.ipv4.ip_forward=1")
	r4.cmd("sysctl net.ipv4.ip_forward=1")

	hostA.cmd('ifconfig hostA-eth0 0')
	hostA.cmd('ifconfig hostA-eth0 100.1.1.1 netmask 255.255.255.128')

	hostA.cmd('ifconfig hostA-eth1 1')
	hostA.cmd('ifconfig hostA-eth1 100.1.3.6 netmask 255.255.255.128')

	hostB.cmd('ifconfig hostB-eth0 0')
	hostB.cmd('ifconfig hostB-eth0 100.1.2.126 netmask 255.255.255.128')
		
	hostB.cmd('ifconfig hostB-eth1 1')
	hostB.cmd('ifconfig hostB-eth1 100.1.2.254 netmask 255.255.255.128')

	r1.cmd('ifconfig r1-eth0 0')
	r1.cmd('ifconfig r1-eth0 100.1.1.126 netmask 255.255.255.128')
	r1.cmd('ifconfig r1-eth1 0')
	r1.cmd('ifconfig r1-eth1 100.1.1.254 netmask 255.255.255.128')
	r1.cmd('ifconfig r1-eth2 0')
	r1.cmd('ifconfig r1-eth2 100.1.3.9 netmask 255.255.255.252')

	r2.cmd('ifconfig r2-eth0 0')
	r2.cmd('ifconfig r2-eth0 100.1.3.2 netmask 255.255.255.252')
	r2.cmd('ifconfig r2-eth1 0')
	r2.cmd('ifconfig r2-eth1 100.1.3.5 netmask 255.255.255.252')
	r2.cmd('ifconfig r2-eth2 0')
	r2.cmd('ifconfig r2-eth2 100.1.3.14 netmask 255.255.255.252')

	r3.cmd('ifconfig r3-eth0 0')
	r3.cmd('ifconfig r3-eth0 100.1.1.129 netmask 255.255.255.128')	
	r3.cmd('ifconfig r3-eth1 0')
	r3.cmd('ifconfig r3-eth1 100.1.2.1 netmask 255.255.255.128')
	r3.cmd('ifconfig r3-eth2 0')
	r3.cmd('ifconfig r3-eth2 100.1.3.13 netmask 255.255.255.252')

	r4.cmd('ifconfig r4-eth0 0')
	r4.cmd('ifconfig r4-eth0 100.1.2.129 netmask 255.255.255.128')	
	r4.cmd('ifconfig r4-eth1 0')
	r4.cmd('ifconfig r4-eth1 100.1.3.1 netmask 255.255.255.252')
	r4.cmd('ifconfig r4-eth2 0')
	r4.cmd('ifconfig r4-eth2 100.1.3.10 netmask 255.255.255.252')


	#Routing pada Host 1
	hostA.cmd("ip rule add from 100.1.1.1 table 1")
	hostA.cmd("ip rule add from 100.1.3.6 table 2")
	hostA.cmd("ip route add 100.1.1.0/25 dev hostA-eth0 scope link table 1")
	hostA.cmd("ip route add default via 100.1.1.126 dev hostA-eth0 table 1")
	hostA.cmd("ip route add 100.1.3.4/25 dev hostA-eth1 scope link table 2")
	hostA.cmd("ip route add default via 100.1.3.5 dev hostA-eth1 table 2")
	hostA.cmd("ip route add default scope global nexthop via 100.1.3.5 dev hostA-eth1")
	hostA.cmd("ip route add default scope global nexthop via 100.1.1.126 dev hostA-eth0")

	#Routing pada Host 2
	hostB.cmd("ip rule add from 100.1.2.126 table 1")
	hostB.cmd("ip rule add from 100.1.1.254 table 2")
	hostB.cmd("ip route add 100.1.2.0/25 dev hostB-eth0 scope link table 1")
	hostB.cmd("ip route add default via 100.1.2.1 dev hostB-eth0 table 1")
	hostB.cmd("ip route add 100.1.2.128/25 dev hostB-eth1 scope link table 2")
	hostB.cmd("ip route add default via 100.1.2.129 dev hostB-eth1 table 2")
	hostB.cmd("ip route add default scope global nexthop via 100.1.2.129 dev hostB-eth1")
	hostB.cmd("ip route add default scope global nexthop via 100.1.2.1 dev hostB-eth0")




	#Routing Router1
	r1.cmd("ip rule add from 100.1.1.126 table 1")
	r1.cmd("ip rule add from 100.1.1.254 table 2")
	r1.cmd("ip rule add from 100.1.3.9 table 3")
	r1.cmd("ip route add 100.1.1.0/25 dev r1-eth0 scope link table 1")
	r1.cmd("ip route add default via 100.1.1.1 dev r1-eth0 table 1")
	r1.cmd("ip route add 100.1.1.128/25 dev r1-eth1 scope link table 2")
	r1.cmd("ip route add default via 100.1.1.129 dev r1-eth1 table 2")
	r1.cmd("ip route add 100.1.3.8/30 dev r1-eth2 scope link table 3")
	r1.cmd("ip route add default via 100.1.3.10 dev r1-eth2 table 3")
	r1.cmd("ip route add default scope global nexthop via 100.1.1.1 dev r1-eth0")
	r1.cmd("ip route add default scope global nexthop via 100.1.1.129 dev r1-eth1")
	r1.cmd("ip route add default scope global nexthop via 100.1.3.10 dev r1-eth2")

	#Routing Router2
	r2.cmd("ip rule add from 100.1.3.1 table 1")
	r2.cmd("ip rule add from 100.1.3.5 table 2")
	r2.cmd("ip rule add from 100.1.3.14 table 3")
	r2.cmd("ip route add 100.1.3.0/30 dev r2-eth0 scope link table 1")
	r2.cmd("ip route add default via 100.1.3.1 dev r2-eth0 table 1")
	r2.cmd("ip route add 100.1.3.4/30 dev r2-eth1 scope link table 2")
	r2.cmd("ip route add default via 100.1.3.6 dev r2-eth1 table 2")
	r2.cmd("ip route add 100.1.3.12/30 dev r2-eth2 scope link table 3")
	r2.cmd("ip route add default via 100.1.3.13 dev r2-eth2 table 3")
	r2.cmd("ip route add default scope global nexthop via 100.1.3.1 dev r2-eth0")
	r2.cmd("ip route add default scope global nexthop via 100.1.3.6 dev r2-eth1")
	r2.cmd("ip route add default scope global nexthop via 100.1.3.13dev r2-eth2")

	#Routing Router3
	r3.cmd("ip rule add from 100.1.1.129 table 1")
	r3.cmd("ip rule add from 100.1.2.1 table 2")
	r3.cmd("ip rule add from 100.1.3.13 table 3")
	r3.cmd("ip route add 100.1.1.128/25 dev r3-eth0 scope link table 1")
	r3.cmd("ip route add default via 100.1.1.254 dev r3-eth0 table 1")
	r3.cmd("ip route add 100.1.2.0/25 dev r3-eth1 scope link table 2")
	r3.cmd("ip route add default via 100.1.2.126 dev r3-eth1 table 2")
	r3.cmd("ip route add 100.1.3.12/30 dev r3-eth2 scope link table 3")
	r3.cmd("ip route add default via 100.1.3.14 dev r3-eth2 table 3")
	r3.cmd("ip route add default scope global nexthop via 100.1.2.126 dev r3-eth1")
	r3.cmd("ip route add default scope global nexthop via 100.1.1.254 dev r3-eth0")
	r3.cmd("ip route add default scope global nexthop via 100.1.3.14 dev r3-eth2")

	#Routing Router4
	r4.cmd("ip rule add from 100.1.2.129 table 1")
	r4.cmd("ip rule add from 100.1.3.1 table 2")
	r4.cmd("ip rule add from 100.1.3.10 table 3")
	r4.cmd("ip route add 100.1.2.128/25 dev r4-eth0 scope link table 1")
	r4.cmd("ip route add default via 100.1.2.254 dev r4-eth0 table 1")
	r4.cmd("ip route add 100.1.3.0/30 dev r4-eth1 scope link table 2")
	r4.cmd("ip route add default via 100.1.3.2 dev r4-eth1 table 2")
	r4.cmd("ip route add 100.1.3.8/30 dev r4-eth2 scope link table 3")
	r4.cmd("ip route add default via 100.1.3.9 dev r4-eth2 table 3")
	r4.cmd("ip route add default scope global nexthop via 100.1.2.254 dev r4-eth1")
	r4.cmd("ip route add default scope global nexthop via 100.1.3.2 dev r4-eth0")
	r4.cmd("ip route add default scope global nexthop via 100.1.3.9 dev r4-eth2")

	r1.cmd("route add -net 100.1.2.0/25 gw 100.1.1.129")
	r1.cmd("route add -net 100.1.2.128/30 gw 100.1.3.10")
	r1.cmd("route add -net 100.1.3.0/30 gw 100.1.3.10")
	r1.cmd("route add -net 100.1.3.12/30 gw 100.1.129")

	r2.cmd("route add -net 100.1.3.8/30 gw 100.1.3.1")
	r2.cmd("route add -net 100.1.1.128/25 gw 100.1.3.13")
	r2.cmd("route add -net 100.1.2.0/25 gw 100.1.3.13")
	r2.cmd("route add -net 100.1.2.128/25 gw 100.1.3.1")

	r3.cmd("route add -net 100.3.0.0/30 gw 100.1.3.14")
	r3.cmd("route add -net 100.1.3.4/30 gw 100.1.3.14")
	r3.cmd("route add -net 100.1.1.0/25 gw 100.1.1.254")
	r3.cmd("route add -net 100.1.3.8/30 gw 100.1.1.254")

	r4.cmd("route add -net 100.1.1.0/25 gw 100.1.3.9")
	r4.cmd("route add -net 100.1.1.128/25 gw 100.1.3.9")
	r4.cmd("route add -net 100.1.3.12/30 gw 100.1.3.2")
	r4.cmd("route add -net 100.1.3.4/30 gw 100.1.3.2")

	'''
	# Setting up traffic
	hostB.cmd("iperf -s &")
	hostA.cmd("iperf -t 30 -B 100.1.1.126 -c 100.1.1.129 &")
	hostA.cmd("iperf -t 30 -B 100.1.1.1 -c 100.1.2.1 &")
	'''
	CLI(net)
	net.stop()
	os.system("killall -9 zebra ripd")
	os.system("rm -f /tmp/.log /tmp/.pid logs/*")
	os.system("rm -f /tmp/.log /tmp/.pid logs/*")
	os.system("mn -cc")
	os.system("clear")
	
if _name_ == '_main_':
    setLogLevel( 'info' )
    Topologi()