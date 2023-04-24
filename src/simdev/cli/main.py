# import click

from click_extra import command, group, option, pass_context, echo
from simdev.server.bac import BACnetIPSimulator
from simdev.util.net import autofetch_address

from simdev.server.console import InteractiveConsole
from simdev.server.web import webserver, SIMULATOR_STORE

from bacpypes.core import enable_sleeping, run

# import BAC0
from time import time
import threading


@group()
@option('-d', '--debug/--no-debug', default=False)
@pass_context
def main(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug


def init_simulator(ctx, address, interface, name, identifier):
    echo(f"Debug is {'on' if ctx.obj['DEBUG'] else 'off'}")

    if not address:
        address = autofetch_address()
    if not address:
        echo("No address supplied. Couldn't autofetch either.")
        echo("Please supply an IPaddr/CIDR with -a switch")
        exit(1)
    
    if identifier == 0:
        identifier = int(time()) % 10000
    if name == "simdev":
        name += f"-{hex(identifier)[2:]}"

    echo(f"Address    : {address}")
    echo(f"Name       : {name}")
    echo(f"Identifier : {identifier}")

    return BACnetIPSimulator(name, identifier, address)



@main.command()
@option('-a', '--address')
@option('-i', '--interface')
@option('-n', '--name', default='simdev')
@option('--identifier', type=int, default=0)
@pass_context
def serv(ctx, address, interface, name, identifier):
    sim = init_simulator(ctx, address, interface, name, identifier)
    sim.configure(dict(ao=5))
    SIMULATOR_STORE.set_simulator(sim)

    web_thread = threading.Thread(target=webserver, daemon=True)
    web_thread.start()
    sim.run()


@main.command()
@option('-a', '--address')
@option('-i', '--interface')
@option('-n', '--name', default='simdev')
@option('--identifier', type=int, default=0)
@pass_context
def cmd(ctx, address, interface, name, identifier):
    # sim = init_simulator(ctx, address, interface, name, identifier)
    InteractiveConsole(address, prompt="~> ")
    # enable_sleeping()
    # run()


if __name__ == "__main__":
    main(obj=dict())
