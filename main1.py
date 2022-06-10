from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.link import TCLink, Link, Intf
from mininet.log import setLogLevel
from datetime import datetime

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
	
	# Konfigurasi host
	hostA = net.addHost('hostA', ip='192.0.0.1/30', defaultRoute='via 192.0.0.2')
	hostA.cmd('ifconfig hostA-eth0 0')
	hostA.cmd('ifconfig hostA-eth0 192.0.0.1 255.255.255.252')
		
	hostA.cmd('ifconfig hostA-eth1 1')
	hostA.cmd('ifconfig hostA-eth1 192.0.0.22 255.255.255.252')
	
	hostB = net.addHost('hostB', ip='192.0.0.10/30', defaultRoute='via 192.0.0.9')
	hostB.cmd('ifconfig hostB-eth0 0')
	hostB.cmd('ifconfig hostB-eth0 192.0.0.10 255.255.255.252')
		
	hostB.cmd('ifconfig hostB-eth1 1')
	hostB.cmd('ifconfig hostB-eth1 192.0.0.13 255.255.255.252')
	
	# Konfigurasi Router
	r1 = net.addHost('r1', ip='192.0.0.2/30')
	r1.cmd('ifconfig r1-eth0 0')
	r1.cmd('ifconfig r1-eth0 192.0.0.2 255.255.255.252')
		
	r1.cmd('ifconfig r1-eth1 1')
	r1.cmd('ifconfig r1-eth0 192.0.0.5 255.255.255.252')
	
	r2 = net.addHost('r2', ip='192.0.0.21/30')
	r2.cmd('ifconfig r2-eth0 0')
	r2.cmd('ifconfig r2-eth0 192.0.0.21 255.255.255.252')
		
	r2.cmd('ifconfig r2-eth1 1')
	r2.cmd('ifconfig r2-eth0 192.0.0.18 255.255.255.252')
	
	r3 = net.addHost('r3', ip='192.0.0.9/30')
	r3.cmd('ifconfig r3-eth0 0')
	r3.cmd('ifconfig r3-eth0 192.0.0.6 255.255.255.252')
		
	r3.cmd('ifconfig r3-eth1 1')
	r3.cmd('ifconfig r3-eth0 192.0.0.9 255.255.255.252')
	
	r4 = net.addHost('r4', ip='192.0.0.14/30')
	r4.cmd('ifconfig r4-eth0 0')
	r4.cmd('ifconfig r4-eth0 192.0.0.17 255.255.255.252')
		
	r4.cmd('ifconfig r4-eth1 1')
	r4.cmd('ifconfig r4-eth0 192.0.0.14 255.255.255.252')
	
	# Connection specification
	linkopts0 = dict(bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
	linkopts1 = dict(bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
	
	# Configuration network
	# Router <--> Router
		
	self.addLink(r1, r3, cls=TCLink, bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r1-eth1', intfName2='r3-eth0', params1={'ip': '192.0.0.5/30'}, params2={'ip': '192.0.0.6/30'})
		
	self.addLink(r2, r4, cls=TCLink, bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r2-eth1', intfName2='r4-eth0', params1={'ip': '192.0.0.18/30'}, params2={'ip': '192.0.0.17/30'})
		             
	self.addLink(r1, r4, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r1-eth2', intfName2='r4-eth2', params1={'ip': '192.0.0.25/30'}, params2={'ip': '192.0.0.26/30'})
		             
	self.addLink(r2, r3, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r2-eth2', intfName2='r3-eth2', params1={'ip': '192.0.0.29/30'}, params2={'ip': '192.0.0.30/30'})
		
	# Router <--> Host

	self.addLink(hostA, r1, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='hostA-eth0', intfName2='r1-eth0', params1={'ip': '192.0.0.1/30'}, params2={'ip': '192.0.0.2/30'})
		             
	self.addLink(hostA, r2, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='hostA-eth1', intfName2='r2-eth0', params1={'ip': '192.0.0.22/30'}, params2={'ip': '192.0.0.21/30'})
		             
	self.addLink(hostB, r3, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='hostB-eth0', intfName2='r3-eth1', params1={'ip': '192.0.0.10/30'}, params2={'ip': '192.0.0.9/30'})
		             
	self.addLink(hostB, r4, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='hostB-eth1', intfName2='r4-eth1', params1={'ip': '192.0.0.13/30'}, params2={'ip': '192.0.0.14/30'})
		            
	net.start()
    	CLI(net)
	
	
	
	
	
	
	net.stop()
	
    	os.system("killall -9 zebra ripd")
    	os.system("rm -f /tmp/*.log /tmp/*.pid logs/*")
	os.system("rm -f /tmp/*.log /tmp/*.pid logs/*")
	os.system("mn -cc")
	os.system("clear")


if __name__ == '__main__':
    setLogLevel( 'info' )
    topologi()                 
                     
                     
             
