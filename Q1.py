from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class CustomTopo(Topo):

    def build(self, **_opts):

        Ra = self.addNode('Ra', cls=LinuxRouter, ip='192.168.1.1/24')
        Rb = self.addNode('Rb', cls=LinuxRouter, ip='192.168.2.1/24')
        Rc = self.addNode('Rc', cls=LinuxRouter, ip='192.168.3.1/24')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')

        self.addLink(s1, Ra, intfName2='Ra-eth1', params2={'ip': '192.168.1.1/24'})
        self.addLink(s2, Rb, intfName2='Rb-eth2', params2={'ip': '192.168.2.1/24'})
        self.addLink(s3, Rc, intfName2='Rc-eth3', params2={'ip': '192.168.3.1/24'})

        # Linking hosts h1, h2 to switch s1
        self.addLink(self.addHost('h1', ip='192.168.1.2/24', defaultRoute='via 192.168.1.1'), s1)
        self.addLink(self.addHost('h2', ip='192.168.1.3/24', defaultRoute='via 192.168.1.1'), s1)

        # Linking hosts h3, h4 to switch s2
        self.addLink(self.addHost('h3', ip='192.168.2.2/24', defaultRoute='via 192.168.2.1'), s2)
        self.addLink(self.addHost('h4', ip='192.168.2.3/24', defaultRoute='via 192.168.2.1'), s2)

        # Linking hosts h5, h6 to switch s3
        self.addLink(self.addHost('h5', ip='192.168.3.2/24', defaultRoute='via 192.168.3.1'), s3)
        self.addLink(self.addHost('h6', ip='192.168.3.3/24', defaultRoute='via 192.168.3.1'), s3)

        # Links between routers using switches 
        self.addLink(s4, Ra, intfName2='Ra-eth4', params2={'ip': '192.168.4.7/24'})
        self.addLink(s4, Rb, intfName2='Ra-eth4', params2={'ip': '192.168.4.8/24'})
        self.addLink(s5, Rb, intfName2='Rb-eth5', params2={'ip': '192.168.5.7/24'})
        self.addLink(s5, Rc, intfName2='Rc-eth5', params2={'ip': '192.168.5.8/24'})
        self.addLink(s6, Ra, intfName2='Ra-eth6', params2={'ip': '192.168.6.7/24'})
        self.addLink(s6, Rc, intfName2='Rc-eth6', params2={'ip': '192.168.6.8/24'})


def run():
    topo = CustomTopo()
    net = Mininet(topo=topo, waitConnected=True)
    net.start()
    # Adding routes for inter-subnet communication
    net['Ra'].cmd('ip route add 192.168.2.0/24 via 192.168.4.8')
    net['Ra'].cmd('ip route add 192.168.3.0/24 via 192.168.6.8')

    net['Rb'].cmd('ip route add 192.168.1.0/24 via 192.168.4.7')
    net['Rb'].cmd('ip route add 192.168.3.0/24 via 192.168.5.8')

    net['Rc'].cmd('ip route add 192.168.1.0/24 via 192.168.6.7')
    net['Rc'].cmd('ip route add 192.168.2.0/24 via 192.168.5.7')
    # the below is changing the path of routing for option c 
    #net['h1'].cmd('ip route add default via 192.168.1.1 nexthop via 192.168.4.2 nexthop via 192.168.5.2 nexthop via 192.168.6.2')

    info('* Routing Table on Routers:\n')
    print("         Routing Table for Router 1           ")
    info(net['Ra'].cmd('route'))
    print("         Routing Table for Router 2           ")
    info(net['Rb'].cmd('route'))
    print("         Routing Table for Router 3           ")
    info(net['Rc'].cmd('route'))
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
