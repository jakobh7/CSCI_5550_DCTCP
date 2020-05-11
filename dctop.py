from mininet.topo import Topo
from mininet.util import irange

class MyTOPO( Topo ):
	"Datacenter Topology"
	
	def build( self ):
		self.racks = []
		rootSwitch = self.addSwitch( 's1' )
		for i in irange( 1, 4 ):
			rack = self.buildRack( i )
			self.racks.append( rack )
			for switch in rack:
				self.addLink( rootSwitch, switch )
	def buildRack( self, loc ):
		dpid = ( loc * 16 ) + 1
		switch = self.addSwitch( 's1r%s' % loc, dpid = '%x' % dpid )
		for n in irange( 1, 4 ):
			host = self.addHost( 'h%sr%s' % ( n, loc ) )
			self.addLink( switch, host )
		return [switch]
topos = { 'datacenter' : MyTOPO }
