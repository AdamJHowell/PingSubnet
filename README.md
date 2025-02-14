# PingSubnet
A Python script that will detect network adapters and ping every potential IPv4 address in the subnet.

If more than one network adapter is present, it will attempt to determine if any are invalid (posessing a loopback or self-assigned address) and present the user with a list of adapters to choose from.
