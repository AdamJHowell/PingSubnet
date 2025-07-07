import ipaddress


class IPv4:
  def __init__( self, address: str, netmask: str ):
    self.address = address
    self.netmask = netmask
    self.network = ipaddress.IPv4Network( f"{address}/{netmask}", strict = False )

  @property
  def network_address( self ):
    return str( self.network.network_address )

  @property
  def broadcast_address( self ):
    return str( self.network.broadcast_address )

  @property
  def hosts( self ):
    return [str( host ) for host in self.network.hosts()]

  @property
  def num_hosts( self ):
    return self.network.num_addresses - 2 if self.network.num_addresses > 2 else 0

  def contains( self, ip: str ) -> bool:
    return ipaddress.IPv4Address( ip ) in self.network
