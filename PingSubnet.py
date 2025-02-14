#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This program uses threading to ping every address on the current subnet.
Performance: because of threading, this program can typically ping 254 addresses in under 10 seconds.
Increasing timeout_ms or pings_per_host will increase the scan time.
To automatically install all required packages:
  pip install -r requirements.txt

An IPv4 blacklist has been added to allow the user to ignore specific interfaces.
Use the IP address blacklist to ignore local interfaces (e.g. "VirtualBox Host-Only Ethernet Adapter")
If a host does not appear in the list of online hosts, check the blacklist!
There is a chance that the wrong interface will be selected, and the results will not be valid.
If that happens, disable that interface, add its IPv4 address to the blacklist, or improve the logic in the 'for interface in interfaces:' block.
"""

import datetime
import ipaddress
import json
import platform
import socket
import sys
import threading
import time
from datetime import datetime
from typing import NoReturn

import psutil
from ping3 import ping


# OS detection, because Windows uses a different ping and arp arguments.
operating_system = platform.system()


def get_mac_from_ip( ip_address: str = "127.0.0.1" ) -> str:
  """
  This function will attempt to get the MAC address from the provided IP address using the arp table.

  :param ip_address: the IPv4 address to query for a MAC address.
  :return: the MAC address as a colon-delimited string, or None if not found.
  """
  import subprocess
  import re

  if ip_address == selected_interface_ipv4:
    return selected_interface_mac.replace( "-", ":" )
  # The -n option sets the timeout.
  first_option = "-n"
  if operating_system == "Windows":
    # The -a option reads from the current arp table.
    first_option = "-a"

  std_out = subprocess.Popen( ["arp", first_option, ip_address], stdout = subprocess.PIPE ).communicate()[0]

  regex = r"(([a-f\d]{1,2}[:-]){5}[a-f\d]{1,2})".encode( "utf-8" )
  match = re.search( regex, std_out )

  if match:
    mac_binary = match.groups()[0]
    mac_with_colons = mac_binary.replace( b"-", b":" )
    return mac_with_colons.decode( "utf-8" ).upper()
  else:
    # Handle case when no MAC address is found.
    return " (MAC not found) "


def get_hostname_from_ip( ip_address: str = "127.0.0.1" ) -> str:
  """
  This function will attempt to get the hostname from the provided IP address using the arp table.

  :param ip_address: the IPv4 address to query for a hostname.
  :return: the hostname.
  """
  try:
    new_hostname, _, _ = socket.gethostbyaddr( ip_address )
    return new_hostname
  except socket.herror:
    return ""


def ping3( dest_address: str, ping_count: int = 1, time_unit: str = "ms", src_address: str = "", timeout: int = 5000 ) -> None:
  """
  Ping the destination address with the source address.

  :param dest_address: the target IP address or hostname to ping.
  :param ping_count: how many times to ping.
  :param time_unit: the unit of time to ping.
  :param src_address: the IP address to ping from.
  :param timeout: how long to wait for a response.
  The output is a tuple containing the ip address, the hostname, the ping time, and the MAC address which is stored in online_host_list.
  """
  delay_sum = 0
  counter = 0
  for _ in range( ping_count ):
    delay = ping( dest_address, timeout, time_unit, src_address )  # Returns the delay in seconds or None if no response.
    if delay:
      counter += 1
      delay_sum += delay
  if counter > 0:
    address_mac_time_tuple = dest_address, get_mac_from_ip( dest_address ), delay_sum / counter
    online_host_list.append( address_mac_time_tuple + (get_hostname_from_ip( dest_address ),) )


def detect_network_interfaces() -> list:
  """
  Get all interfaces.
  Exclude any which have a loopback or self-assigned IP.

  :return: a list of viable interfaces as tuples.
  """
  # Get all network interfaces.
  interfaces = psutil.net_if_addrs()
  if debug:
    print( f" Debug: {json.dumps( interfaces )}" )
  valid_interfaces = []
  for i_face_name, interface_addresses in interfaces.items():
    # Iterate over all address info for this interface.
    for address_info in interface_addresses:
      # Check if the address is IPv4.
      if address_info.family == socket.AF_INET:
        if not address_info.address.startswith( "127.0.0.1" ) and not address_info.address.startswith( "169.254" ):
          valid_interfaces.append( (i_face_name, address_info, interface_addresses[0].address) )
        break
  return valid_interfaces


def get_range( network ) -> tuple:
  """
  Use the network to determine the starting and ending IP addresses.

  :param network: an IPv4Network class instance.
  :return: the network address and broadcast address as a tuple.
  """
  # Calculate the network address (starting address).
  network_address = network.network_address

  # Calculate the broadcast address (ending address).
  broadcast_address = network.broadcast_address

  # Return the network range.
  return network_address, broadcast_address


def exiting( exit_code: int = 0, exit_text: str = "" ) -> NoReturn:
  """
  post-conditions: The program will be terminated.

  :param exit_code: the return value to pass to the OS.
  :param exit_text: the text to print before exiting.
  :rtype: NoReturn
  :raises SystemExit: under all circumstances.
  """
  exit_timestamp = datetime.now().replace( microsecond = 0 ).isoformat( sep = " " )
  print( "" )
  if exit_text != "":
    print( f"{exit_text}" )
  print( f"  Exiting with code {exit_code} at {exit_timestamp}" )
  raise SystemExit( exit_code )


def prompt_for_list_item( max_value: int ) -> int:
  """
  Prompt the user to select one element from selection_list.

  :param max_value: the list of items to select from.
  :return: the selected list item.
  """
  temp_number = -1
  while temp_number < 0:
    temp_answer = input( "Enter the number to the left of your selection (or 'x' to exit): " )
    if temp_answer == "x":
      exiting( 1, "User aborted." )
    try:
      if max_value > int( temp_answer ) >= 0:
        temp_number = int( temp_answer )
      else:
        print( "  That is not a valid selection!" )
    except ValueError:
      print( "That is not a valid number!" )
  return temp_number


if __name__ == "__main__":
  program_name = "PingSubnet"
  debug = False
  timeout_ms = 5000
  pings_per_host = 3
  ping_unit = "ms"
  hostname = socket.gethostname()
  selected_index = 0
  start_time = time.perf_counter()
  current_time = datetime.now().replace( microsecond = 0 ).isoformat( sep = " " )
  print( f"Starting {program_name} at {current_time}" )

  interface_list = detect_network_interfaces()
  if not interface_list:
    exiting( 2, "No viable interfaces discovered!" )
  elif len( interface_list ) > 1:
    print()
    # Print the list of network interfaces.
    print( "Network Interfaces Detected:" )
    # Print all valid interfaces.
    for index, (interface_name, interface_object, _) in enumerate( interface_list ):
      print( f"  {index} - {interface_name} - {interface_object.address}" )
    # Prompt the user for the interface to use.
    selected_index = prompt_for_list_item( len( interface_list ) )
    if debug:
      print( f" Debug: Detailed network info: {interface_list[selected_index]}" )
  else:
    print( f"Using the interface named '{interface_list[selected_index][0]}'" )

  # Get the selected IPv4 data and save to the global.
  selected_interface_name = interface_list[selected_index][0]
  selected_interface_ipv4 = interface_list[selected_index][1].address
  selected_interface_netmask = interface_list[selected_index][1].netmask
  selected_interface_mac = interface_list[selected_index][2].replace( "-", ":" )

  if debug:
    print( f" Debug: {selected_interface_ipv4}/{selected_interface_netmask}" )
  # Get the network from the IP address and subnet mask.
  v4_network = ipaddress.IPv4Network( f"{selected_interface_ipv4}/{selected_interface_netmask}", strict = False )
  # Get all hosts on the network.
  all_hosts = list( v4_network.hosts() )
  start_address, end_address = get_range( v4_network )

  ping_count_argument = "-c"
  ping_wait_argument = "-W"
  if operating_system == "Windows":
    ping_count_argument = "-n"
    ping_wait_argument = "-w"

  print()
  print( "Detected properties:" )
  print( f"  {operating_system} operating system" )
  print( f"  interface name: {selected_interface_name}" )
  print( f"  local hostname: {hostname}" )
  print( f"  local IP address: {selected_interface_ipv4}" )
  print( f"  local network mask: {selected_interface_netmask}" )
  print( f"  local MAC address: {selected_interface_mac}" )
  print()
  print( f"Pinging addresses from {start_address} to {end_address}" )

  try:
    online_host_list = []
    thread_list = []
    subnet_size = len( all_hosts )
    if subnet_size > 4096:
      print( f"\n\nThere were {subnet_size} possible hosts detected." )
      print( "This is likely an incorrectly detected subnet mask or an unused network adapter." )
      print( "If you would like to continue, enter 1: " )
      answer = input( "" )
      if int( answer ) != 1:
        print( "Exiting..." )
        sys.exit( -1 )

    suffix = "s"
    if pings_per_host == 1:
      suffix = ""
    print( f"\nThreading {subnet_size} pings, pinging each host {pings_per_host} time{suffix}, and using a timeout of {timeout_ms} milliseconds..." )
    # For each IP address in the subnet, run the ping command with subprocess.popen interface.
    for i in range( subnet_size ):
      thread_list.append( threading.Thread( target = ping3, args = (str( all_hosts[i] ), pings_per_host, ping_unit, selected_interface_ipv4, timeout_ms) ) )

    print( "Starting all threads..." )
    # Start all threads.
    for thread in thread_list:
      thread.start()

    print( "Waiting for all threads to finish..." )
    # Join all threads.
    for thread in thread_list:
      # Wait until all threads terminate using a timeout appropriate for the number of hosts.
      thread.join( timeout_ms / 1000 * pings_per_host )

    print( "\nAll online host IP and MAC addresses:" )
    print( "IP\tMAC\tHostname\tPing\tping unit" )
    sorted_ip_mac = sorted( online_host_list, key = lambda x: list( map( int, x[0].split( "." ) ) ) )
    for online_host in sorted_ip_mac:
      # Note that the results are displayed out of order.
      print( f"{online_host[0]}\t{online_host[1]}\t{online_host[3]}\t{online_host[2]:.1f}\t{ping_unit}" )
    print( "" )
    print( f"{len( sorted_ip_mac )} out of {subnet_size} hosts responded to a ping within {timeout_ms / 1000} seconds." )

  except KeyboardInterrupt:
    print( "Execution interrupted." )

  print( f"Scanning took {round( time.perf_counter() - start_time, 2 )} seconds.\n" )
  print( f"Goodbye from {program_name}" )
