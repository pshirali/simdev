#
#   List of commonly found interfaces
#

from netifaces import ifaddresses, AF_INET
import iptools.ipv4 as ipv4


_IFCS = ["eth0", "en0"]


def autofetch_address(ifc_list=[]):

    if not len(ifc_list):
        ifc_list = _IFCS

    props = set(["addr", "netmask", "broadcast"])

    for ifc in ifc_list:
        addr_fly = ifaddresses(ifc)

        if AF_INET in addr_fly.keys():
            addrs = addr_fly[AF_INET]

            for addr in addrs:
                if props & set(addr.keys()) == props:
                    address = addr["addr"]
                    netmask = addr["netmask"]
                    cidr = ipv4.netmask2prefix(netmask)
                    return f"{address}/{cidr}"
