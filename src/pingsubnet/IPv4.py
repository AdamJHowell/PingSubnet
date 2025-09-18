import ipaddress


class IPv4:
  """
  A class to represent and manage an IPv4 network.

  This class encapsulates an IPv4 address and its corresponding netmask,
  providing easy access to network properties such as the network address,
  broadcast address, and a list of all host addresses within the subnet.
  """

  def __init__( self, address: str, netmask: str ):
    """
    Initializes the IPv4 object.

    :param address: The IPv4 address of the local machine.
    :param netmask: The IPv4 netmask of the local network.
    """
    self.address = address
    self.netmask = netmask
    self.network = ipaddress.IPv4Network( f"{address}/{netmask}", strict = False )

  @property
  def network_address( self ) -> str:
    """
    The network address of the IPv4 network.
    """
    return str( self.network.network_address )

  @property
  def broadcast_address( self ) -> str:
    """
    The broadcast address of the IPv4 network.
    """
    return str( self.network.broadcast_address )

  @property
  def hosts( self ) -> list[str]:
    """
    A list of all host addresses in the network, excluding the network and broadcast addresses.
    """
    return [str( host ) for host in self.network.hosts()]

  @property
  def num_hosts( self ) -> int:
    """
    The number of usable host addresses in the network.

    This calculation excludes the network address and broadcast address.
    """
    return self.network.num_addresses - 2 if self.network.num_addresses > 2 else 0

  def contains( self, ip: str ) -> bool:
    """
    Checks if a given IPv4 address is within this network.

    :param ip: The IPv4 address to check.
    :returns: True if the address is in the network, False otherwise.
    """
    return ipaddress.IPv4Address( ip ) in self.network
