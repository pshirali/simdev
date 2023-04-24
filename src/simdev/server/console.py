from bacpypes.consolecmd import ConsoleCmd
# from bacpypes.iocb import IOCB
# from bacpypes.pdu import Address
# from bacpypes.apdu import ReadPropertyRequest, ReadPropertyACK
# from bacpypes.constructeddata import Array
# from bacpypes.core import deferred

from simdev.server.bac import BACNET_OBJECT_MAP
import BAC0


class InteractiveConsole(ConsoleCmd):

    def __init__(self, addr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._env = {}
        self._app = BAC0.lite(addr)

    def do_set(self, args):
        """Set local variables in this cmd.
        ~> set key=123 val=456
        """
        args = args.split()
        setvals = []
        for arg in args:
            k_eq_v = arg.split("=")
            if len(k_eq_v) != 2:
                print(f"ERROR: skipping invalid: {arg}")
            key = k_eq_v[0].strip()
            val = k_eq_v[1].strip()
            self._env[key] = val
            setvals.append(key)
        if len(setvals):
            print("Done:", ",".join(setvals))

    def do_env(self, args):
        for k, v in self._env.items():
            print(f"{k}={v}")

    def do_unset(self, args):
        unsetvals = []
        args = args.split()
        for arg in args:
            arg = arg.strip()
            if arg in self._env:
                self._env.pop(arg)
                unsetvals.append(arg)
        if len(unsetvals):
            print("Unset:", ",".join(unsetvals))

    def do_read(self, args):
        args = args.strip().split("-")
        if len(args) != 2:
            print("Error: Expected format: AO-1")
            return
        otype = args[0].upper()
        if otype not in BACNET_OBJECT_MAP:
            print(f"Error: unknown type: {otype}")
            return
        if not args[1].isdigit():
            print(f"Error: expected {otype}-<value> as digit. Got {args[1]}")
        if not "addr" in self._env:
            print("Missing 'addr' in env. Use set addr=<IP> for requests")
            return
        instance = int(args[1])

        # -------- [bacpypes code : ignore] ---------------------------------
        #

        # request = ReadPropertyRequest(
        #     objectIdentifier=otype,
        #     propertyIdentifier=int(args[1])
        # )
        # request.pduDestination = Address(self._env["addr"])

        # iocb = IOCB(request)
        # deferred(self._sim.app.request_io, iocb)
        # iocb.wait()

        # if iocb.ioError:
        #     print("iocb.Error: request errored/rejected/aborted")
        #     return
        # elif iocb.ioResponse:
        #     if not isinstance(apdu, ReadPropertyACK):
        #         print("Error: Didn't receive ReadPropertyACK.")
        #         return
        #     datatype = get_datatype(
        #         apdu.objectIdentifier[0], apdu.propertyIdentifier
        #     )
        #     if not datatype:
        #         print("Error: unknown datatype for ReadPropertyACK :(")
        #         return
            
        #     if issubclass(datatype, Array) and (
        #         apdu.propertyArrayIndex is not None
        #     ):
        #         if apdu.propertyArrayIndex == 0:
        #             value = apdu.propertyValue.cast_out(Unsigned)
        #         else:
        #             value = apdu.propertyValue.cast_out(datatype.subtype)
        #     else:
        #         value = apdu.propertyValue.cast_out(datatype)

        #     print(f"Value: {value}")
        #     if hasattr(value, "debug_contents"):
        #         print(value.debug_contents())
        # else:
        #     print("edgeCase: Unkown response!")
        #     return
        #
        # -------------------------------------------------------------------

        target_ip = self._env["addr"]
        objType = BACNET_OBJECT_MAP[otype]["objType"]
        request = f"{target_ip} {objType} {instance} presentValue"
        value = self._app.read(request)
        print(f"Result: {value}")

    def do_write(self, args):
        args = args.strip().split()
        args = [a.strip() for a in args]
        if len(args) != 2:
            print("Error: Expected format: AO-1 <value>")
            return
        targetVal = args[1]
        args = args[0].split("-")
        if len(args) != 2:
            print("Error: Expected objType in AO-1 format. Got {args[0]}")
            return
        otype = args[0].upper()
        if otype not in BACNET_OBJECT_MAP:
            print(f"Error: unknown type: {otype}")
            return
        if not args[1].isdigit():
            print(f"Error: expected {otype}-<value> as digit. Got {args[1]}")
        if not "addr" in self._env:
            print("Missing 'addr' in env. Use set addr=<IP> for requests")
            return
        instance = int(args[1])

        target_ip = self._env["addr"]
        objType = BACNET_OBJECT_MAP[otype]["objType"]
        request = f"{target_ip} {objType} {instance} presentValue {targetVal}"
        value = self._app.write(request)
        print("Done")
