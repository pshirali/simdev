# BACnet/IP Device Simulator


### About

This is a prototype BACnet/IP device simulator designed to expose a
BACnet/IP device as well as an HTTP server. This simulator enables
BACnet devices to communicate with it over a local network, while also
allowing an HTTP client to know the status of the simulator's points.

This prototype is aimed at making it easy to verify IO operations which
take place on BACnet/IP device, typically from another such device such
as an IoT Gateway or other BACnet/IP based controllers.


### Stage of development

This is an `alpha` and is under active development. There maybe breaking 
changes introduced at this stage.


### Installation

This project has been developed in Python3.

* You'll require `docker` on your machine if you only intend to try/use
* You'll require a Python3 virtual environment if you intend to develop/tinker

Steps to deploy:

1. Clone this repo to a folder.
1. Switch your current working directory to the root of this repo
1. Run `make` to view a list of commands


#### Usage using Docker

You can use the `make dc-*` commands to easily setup a docker image and 
execute containers.

`make build`: Will build a `simdev` image with the simulator

`make dc-up`: Will bring up three containers named `simdev-a`, `simdev-b` and `simdev-c`

`make run-x`: Replace `x` with `a`, `b` or `c` to shell into the above containers

Once inside the container, run:

* `sd serv` to start the simulation server
* `sd cmd` to start another BACnet server in CLI mode


#### Development

You must install Python3 and setup a virtual environment for development.

Run `make install-all` to install all dependencies required for development.

The above command also installs an entrypoint called `sd` (for simdev) through
which the tool can be invoked.


### License

Copyright (c) Praveen G Shirali.
Released under Apache 2.0 License
