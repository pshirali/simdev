# BACnet/IP Device Simulator


## About

This is a prototype BACnet/IP device simulator designed to expose a
BACnet/IP device as well as an HTTP server. This simulator enables
BACnet devices to communicate with it over a local network, while also
allowing an HTTP client to know the status of the simulator's points.

This prototype is aimed at making it easy to verify IO operations which
take place on BACnet/IP device, typically from another such device such
as an IoT Gateway or other BACnet/IP based controllers.

This project is in `alpha`. There may be breaking changes introduced to the 
interfaces.


## Usage Instructions

To use the device simulator, you'll require either a Python3 virtual 
environment, docker (preferred).

The _Makefile_ provides handy commands to build a docker image, launch 
containers, exec into these containers, teardown etc.

For ease of use, three containers are launched from the make file (lets call 
these `a`, `b` and `c`). The containers themselves are called `simdev-a`, 
`simdev-b` and `simdev-c`.

1. Run `make dc-build` to build the docker image from the root of this 
repo. The image will be called `simdev`.
1. Run `make dc-up`. This will launch all three containers `simdev-a`, 
`simdev-b` and `simdev-c`.
1. Run `make run-a`, `make run-b`, or `make run-c` to exec/shell into the 
respective containers.
1. Run `make dc-rm` to remove all containers. `make dc-rmi` to remove the image.

The containers run _sleep infinity_ in their entrypoint as these commands 
are meant for interactive exploration of the tool.

### Demo

To execute the `simdev` process, you should exec into one or more of the 
containers and launch `sd` either as a server (using `sd serv`), or as a
BACnet device with an interactive command line (using `sd cmd`).

The image also has [httpie](https://httpie.io/), a user-friendy HTTP CLI 
client. This can be used to make HTTP requests from any container to any 
container running the simulator. The containers share the same default 
network.

### Address resolution

The BACnet/IP stack requires information of both IPv4 address and CIDR. This 
can be passed using the CLI arugment `sd serv -a <IPv4/CIDR>`. Example: if 
your network mask is 255.255.255.0, and your IP address is 192.168.0.2, then 
the CLI argument will have the value _192.168.0.2/24_.

Another option is to invoke `sd serv -i <interface-name>`. When this is passed 
simdev will automatically fetch the IPv2, netmask and calculate the IPv4/CIDR 
for use by the BACnet device. This option is convenient in scenarios where 
you know the name of the interface is known, or is same/similar across your 
setup, while you IP addresses might vary from time to time.

When neither is passed, simdev will attempt reading IPv4/CIDR from interface 
`eth0` and `en0`. The `eth0` interface-name will be available on docker, hence 
there's no need to pass these arguments in the `a|b|c` demo containers.


## Typical Usage Examples

The BACnet/IP simulator initialises itself with 5 points (BACnet Objects) of 
type `AnalogOutput`. These are named `AO-0`, `AO-1`, through `AO-4`. The 
initial _presentValue_ for the objects is 0.

### Reading, writing values from another BACnet device

In order to communicate with the simulated BACnet/IP device over BACnet, one 
requires another BACnet device to do so. The two BACnet devices will 
bind themselves to a commonly agreed port (BACnet default: 47808), but 
require separate IPv4 addresses to bind to. Thus, in order to read, write one 
needs to launch `sd cmd` from a different container.

The `cmd` is an interactive command interface which instructs its local 
BACnet/IP device to send read/write instructions to the simulator's BACnet/IP 
device.

### Command usage

To read, write: you need to do the following.

1. Run `set addr=<IPv4>`; where <IPv4> is the address of the target BACnet/IP 
device you wish to talk to. Example: `set addr=192.168.0.2`. Once set, all 
subsequent read, write commands will send packets to this device.
1. Run `read <objId`>, or `write <objId> <value>` to read or write. Here, the 
<objId> is `ao-0`, `ao-1`, .. `ao-4`. Note the `ao` in lower case when used in 
commands.


### HTTP Routes

* `GET /point/{objId}/value`: returns the presentValue of the object: Ex: objId could be `ao-0`
* `PUT /point/{objId}/value/{value}`: write the supplied {value} as the presentValue. Real number expected
* `GET /point/{objId}/logs`: returns the read+write logs for the point since it was last cleared
* `DEL /point/{objId}/logs`: clears the I/O history for the objId


## Development Setup

simdev has been developed in Python3. You'll require Python 3.11+ (preferred) 
and preferably a virtualenv.

To install dependencies and entrypoint, run `make install-all`

Dependencies are defined in the `setup.cfg` file. The above command installs 
the code from the current repo as an editable package (i.e `pip install -e .`). 
This allows for code changes in simdev to reflect live.


### License

Copyright (c) Praveen G Shirali.
Released under Apache 2.0 License
