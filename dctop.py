from mininet.topo import Topo
from mininet.util import irange

class MyTOPO( Topo ):
	"Datacenter Topology"
	
	def __init__(self):

		Topo.__init__(self)

		#switches
		
		s1 = self.addSwitch('s1')
		s11 = self.addSwitch('s11')
		s12 = self.addSwitch('s12')
		s111 = self.addSwitch('s111')
		s112 = self.addSwitch('s112')
		s121 = self.addSwitch('s121')
		s122 = self.addSwitch('s122')

		#hosts
		h1 = self.addHost('h1')
		h2 = self.addHost('h2')
		h3 = self.addHost('h3')
		h4 = self.addHost('h4')
		

		#links
		self.addLink( s1 , s11 )
		self.addLink( s1 , s12 )
		self.addLink( s11 , s111 )
		self.addLink( s11 , s112 )
		self.addLink( s12 , s121 )
		self.addLink( s12 , s122 )
		
		self.addLink( s111 , h1 )
		self.addLink( s112 , h2 )
		self.addLink( s121 , h3 )
		self.addLink( s122 , h4 )

topos = { 'datacenter' : MyTOPO }
