#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program tries to determine which interface is the best one to use.
Basically, it tries to eliminate loopback interfaces and disconnected VPNs and such.
"""

import ipaddress
import socket
import time

import netifaces

# https://stackoverflow.com/questions/73688089/is-there-a-way-to-select-the-correct-network-interface-using-netifaces-or-socket
start_time = time.perf_counter()

ip_addr = 0
netmask = 0
interfaces = netifaces.interfaces()
# interfaces is a list of strings.
print( f"Interfaces: {interfaces}" )
for interface in interfaces:
  # Each interface is a string.
  print( f"\n  Interface: {interface}" )
  addresses = netifaces.ifaddresses( interface )
  gateways = netifaces.gateways()
  for i in gateways:
    print( "            <address>, <interface>, <is_default>" )
    print( f"    {i}: {gateways[i]}" )
    print( f"      type: {type(gateways[i])}" )
    for j in gateways[i]:
      print( f"      element: {gateways[i][j]}" )
      if type( gateways[i][j] ) is dict:
        for item in gateways[i][j]:
          print( f"        item: {item}" )
  # addresses is a dictionary.
  print( f"    Addresses: {addresses}" )
  print( f"Addresses keys: {addresses.keys()}" )
  print( f"Gateway keys: {gateways.keys()}" )
  for address in addresses:
    # Each address is an integer.
    if address == netifaces.AF_LINK:
      print( f"      ID {address} is a link layer interface." )
    elif address == netifaces.AF_INET:
      print( f"      ID {address} is an IPv4 interface." )
      print( f"        Info: {addresses[netifaces.AF_INET]}" )
      asdf = addresses[netifaces.AF_INET]
      if ip_addr == 0:
        ip_addr = asdf[0]['addr']
        netmask = asdf[0]['netmask']
    elif address == netifaces.AF_INET6:
      print( f"      ID {address} is an IPv6 interface." )
    else:
      print( f"      ID {address} is an unknown interface type." )
gateways = netifaces.gateways()
print( f"Gateways: {gateways}" )
print( f"IPv4 gateways: {gateways['default'][netifaces.AF_INET]}" )

print( "\n" )

hostname = socket.gethostname()
print( f"Your computer hostname is: {hostname}" )
print( f"Your computer IP address is: {ip_addr}" )
print( f"Your computer network mask is: {netmask}" )
subnet = list( ipaddress.ip_network( ip_addr ).subnets() )
for network in subnet:
  print( f"Network: {network}" )
  print( f"  Private: {network.is_private}" )
  print( f"  Loopback: {network.is_loopback}" )
  network.hosts()

print( f"\nScanning took {round( time.perf_counter() - start_time, 2 )} seconds.\n" )
