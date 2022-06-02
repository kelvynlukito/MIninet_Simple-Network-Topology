from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.node import OVSController
from mininet.cli import CLI
from mininet.link import TCLink
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

             
class MyTopo( Topo ):

	def __init__( self, **opts ):

		# Initialize topology
		Topo.__init__( self, **opts )
	
		# Add hosts and router
		net = Mininet(link = TCLink)
		
		net.addHost('hostA', ip='192.0.0.1/30', defaultRoute='via 192.0.0.2')
		net.addHost('hostB', ip='192.0.0.10/30', defaultRoute='via 192.0.0.9')
		
		net.addHost('r1', ip='192.0.0.2/30')
		net.addHost('r2', ip='192.0.0.21/30')
		net.addHost('r3', ip='192.0.0.9/30')
		net.addHost('r4', ip='192.0.0.14/30')
		
		
		linkopts0 = dict(bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		linkopts1 = dict(bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		# Add ip address for Host and Router
	        
	        net['hostA'].cmd('ip addr add 192.0.0.1/30 brd + dev hostA-eth0')
	        net['hostA'].cmd('ip addr add 192.0.0.22/30 brd + dev hostA-eth1')
	        
	        net['hostB'].cmd('ip addr add 192.0.0.10/30 brd + dev hostB-eth0')
	        net['hostB'].cmd('ip addr add 192.0.0.13/30 brd + dev hostB-eth1')
	        
	        net['r1'].cmd('ip addr add 192.0.0.2/30 brd + dev r1-eth0')
	        net['r1'].cmd('ip addr add 192.0.0.5/30 brd + dev r1-eth1')
	        net['r1'].cmd('ip addr add 192.0.0.25/30 brd + dev r1-eth2')
	        
	        net['r2'].cmd('ip addr add 192.0.0.21/30 brd + dev r2-eth0')
	        net['r2'].cmd('ip addr add 192.0.0.18/30 brd + dev r2-eth1')
	        net['r2'].cmd('ip addr add 192.0.0.29/30 brd + dev r2-eth2')
	        
	        net['r3'].cmd('ip addr add 192.0.0.6/30 brd + dev r3-eth0')
	        net['r3'].cmd('ip addr add 192.0.0.9/30 brd + dev r3-eth1')
	        net['r3'].cmd('ip addr add 192.0.0.30/30 brd + dev r3-eth2')
	        
	        net['r4'].cmd('ip addr add 192.0.0.17/30 brd + dev r4-eth0')
	        net['r4'].cmd('ip addr add 192.0.0.14/30 brd + dev r4-eth1')
	        net['r4'].cmd('ip addr add 192.0.0.26/30 brd + dev r4-eth2')
		             
		# ip forward
		net['r1'].cmd('sysctl net.ipv4.ip_forward=1')
		net['r2'].cmd('sysctl net.ipv4.ip_forward=1')
		net['r3'].cmd('sysctl net.ipv4.ip_forward=1')
		net['r4'].cmd('sysctl net.ipv4.ip_forward=1') 
		
	
		# Add links
		# Host <--> Router
		
		net.addLink( net['hostA'], net['r1'], intfName1='hostA-eth0', intfName2='r1-eth0', bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		net.addLink( net['hostA'], net['r2'], intfName1='hostA-eth1', intfName2='r2-eth0', bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		net.addLink( net['hostB'], net['r3'], intfName1='hostB-eth0', intfName2='r3-eth1', bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		net.addLink( net['hostB'], net['r4'], intfName1='hostB-eth1', intfName2='r4-eth1', bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		# Router <--> Router
		
		net.addLink( net['r1'], net['r3'], intfName1='r1-eth1', intfName2='r3-eth0', bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		net.addLink( net['r2'], net['r4'], intfName1='r2-eth1', intfName2='r4-eth0', bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		net.addLink( net['r1'], net['r4'], intfName1='r1-eth2', intfName2='r4-eth2', bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		net.addLink( net['r3'], net['r2'], intfName1='r3-eth2', intfName2='r2-eth2', bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)

	        
	                 
                     
def run():
    net = Mininet(topo=MyTopo())
    net.start()
    CLI(net)
    
    
    time_start = datetime.now()

    print("*** Setup quagga")
    for router in net.hosts:
        if router.name[0] == 'r':

            # config zebra and ripd
            router.cmd("zebra -f config/zebra/{0}zebra.conf -d -i /tmp/{0}zebra.pid > logs/{0}-zebra-stdout 2>&1".format(router.name))
            router.waitOutput()
            
            router.cmd("ripd -f config/rip/{0}ripd.conf -d -i /tmp/{0}ripd.pid > logs/{0}-ripd-stdout 2>&1".format(router.name), shell=True)
            router.waitOutput()
            
            #print(f"Starting zebra and rip on {router.name}")
            
     #time.sleep(5)
    print("\n*** Connection test")
    
    loss = 100
    while(loss > 0):
        loss = net.pingAll()

    time_end = datetime.now() - time_start
    #print(f'Percentage Loss : {loss}')
    #print(f'Convergence Time: {time_end.total_seconds()}s')
    

    print("\n*** Bandwidth test")
    time.sleep(5)

    net['hostB'].cmd('iperf -s -i 1 &')
    time.sleep(1)

    net['hostA'].cmdPrint('iperf -c 192.0.0.13 -i 1')
    CLI(net)

    net.stop()
    os.system("killall -9 zebra ripd")
    os.system("rm -f /tmp/*.log /tmp/*.pid logs/*")


os.system("rm -f /tmp/*.log /tmp/*.pid logs/*")
os.system("mn -cc")
os.system("clear")

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()                     
                     
                     
             
