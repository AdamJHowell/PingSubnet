# PingSubnet

A Python script that will detect network adapters and ping every potential IPv4 address in the subnet.

If more than one network adapter is present, it will attempt to determine if any are invalid (possessing a loopback or self-assigned address) and present the user with a list of adapters to choose from.

The output is printed to the screen in tab-separated format (TSV) with a header row.

Here is a (partially sanitized) example run:

```
Starting PingSubnet at 2025-02-14 11:55:22

Network Interfaces Detected:
  0 - Ethernet - 192.168.55.200
  1 - Ethernet 2 - 192.168.56.1
Enter the number to the left of your selection (or 'x' to exit): 0

Detected properties:
  Windows operating system
  interface name: Ethernet
  local hostname: NunYa
  local IP address: 192.168.55.200
  local network mask: 255.255.255.0
  local MAC address: 00:01:02:AA:BB:CC

Pinging addresses from 192.168.55.0 to 192.168.55.255

Threading 254 pings, pinging each host 3 times, and using a timeout of 5000 milliseconds...
Starting all threads...
Waiting for all threads to finish...

All online host IP and MAC addresses:
IP	MAC	Hostname	Ping	ping unit
192.168.55.1	00:01:02:AA:BB:CC		1.6	ms
192.168.55.55	00:01:02:AA:BB:CC		5.5	ms
192.168.55.55	00:01:02:AA:BB:CC	homeassistant	1.6	ms
192.168.55.55	00:01:02:AA:BB:CC	pi.hole	1.1	ms
(truncated for brevity)
192.168.55.200	00:01:02:AA:BB:CC	NunYa	12.5	ms

44 out of 254 hosts responded to a ping within 5.0 seconds.
Scanning took 12.22 seconds.

Goodbye from PingSubnet
```

In that example you will see the first two devices did not return a hostname.  I still haven't figured out why the socket library can sometimes detect the hostname and sometimes cannot.  If anyone knows, tell me, so I can update this code or update my DHCP server to better handle hostnames.

[![CodeFactor](https://www.codefactor.io/repository/github/adamjhowell/PingSubnet/badge)](https://www.codefactor.io/repository/github/adamjhowell/PingSubnet)
![Last commit](https://img.shields.io/github/last-commit/adamjhowell/PingSubnet?logo=github)
