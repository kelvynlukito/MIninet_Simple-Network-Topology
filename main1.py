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
		hostA = self.addHost('hostA', ip='192.0.0.1/30', defaultRoute='via 192.0.0.2')
		#hostA.cmd('ifconfig hostA-eth0 0')
		#hostA.cmd('ifconfig hostA-eth0 192.0.0.1 255.255.255.252')
		
		#hostA.cmd('ifconfig hostA-eth1 1')
		#hostA.cmd('ifconfig hostA-eth0 192.0.0.21 255.255.255.252')
		
		hostB = self.addHost('hostB', ip='192.0.0.10/30', defaultRoute='via 192.0.0.9')
		#hostB.cmd('ifconfig hostB-eth0 0')
		#hostB.cmd('ifconfig hostB-eth0 192.0.0.10 255.255.255.252')
		
		#hostB.cmd('ifconfig hostB-eth1 1')
		#hostB.cmd('ifconfig hostB-eth0 192.0.0.13 255.255.255.252')
		
		r1 = self.addNode('r1', cls=LinuxRouter, ip='192.0.0.2/30')
		#r1.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
		
		r2 = self.addNode('r2', cls=LinuxRouter, ip='192.0.0.21/30')
		#r2.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
		
		r3 = self.addNode('r3', cls=LinuxRouter, ip='192.0.0.9/30')
		#r4.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
		
		r4 = self.addNode('r4', cls=LinuxRouter, ip='192.0.0.14/30')
		#r4.cmd("echo 1 > /proc/sys/net/ipv4/ip_forward")
		
		
		linkopts0 = dict(bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		linkopts1 = dict(bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True)
		
		# Add links
		
		# Router <--> Router
		
		self.addLink(r1, r3, cls=TCLink, bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r1-eth1', intfName2='r3-eth0', params1={'ip': '192.0.0.5/30'}, params2={'ip': '192.0.0.6/30'})
		
	        self.addLink(r2, r4, cls=TCLink, bw=0.5, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r2-eth1', intfName2='r4-eth0', params1={'ip': '192.0.0.18/30'}, params2={'ip': '192.0.0.17/30'})
		             
	        self.addLink(r1, r4, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r1-eth2', intfName2='r4-eth2', params1={'ip': '192.0.0.25/30'}, params2={'ip': '192.0.0.26/30'})
		             
	        self.addLink(r2, r3, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName1='r2-eth2', intfName2='r3-eth2', params1={'ip': '192.0.0.29/30'}, params2={'ip': '192.0.0.30/30'})
		
		# Router <--> Host

	        self.addLink(hostA, r1, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName2='r1-eth0', params1={'ip': '192.0.0.1/30'}, params2={'ip': '192.0.0.2/30'})
		             
	        self.addLink(hostA, r2, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName2='r2-eth0', params1={'ip': '192.0.0.22/30'}, params2={'ip': '192.0.0.21/30'})
		             
	        self.addLink(hostB, r3, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName2='r3-eth1', params1={'ip': '192.0.0.10/30'}, params2={'ip': '192.0.0.9/30'})
		             
	        self.addLink(hostB, r4, cls=TCLink, bw=1, delay='1ms', loss=0, max_queue_size=20, use_tbf=True, intfName2='r4-eth1', params1={'ip': '192.0.0.13/30'}, params2={'ip': '192.0.0.14/30'})
		             
		          
                     


                     
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
                     
                     
             
