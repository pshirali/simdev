import logging
import json
import collections

from datetime import datetime
from collections import deque
from functools import wraps

# from bacpypes.core import run as run_bacpypes
from bacpypes import core
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject

from bacpypes.object import (AnalogInputObject, AnalogOutputObject,
                             AnalogValueObject)
from bacpypes.primitivedata import Real


log = logging.getLogger(__name__)


# The list below clubs the short-code that's used by simdev, and its
# associated BACnet object types.
#
# Each type of object in BACnet has a `BACnet Object Type` and an
# associated `BACnet Object Type ID` (number) associated with it
#
# BACNET_OBJECT_MAP = {
#     "AI": dict(objType="analogInput", objClass=AnalogInputObject),
#     "AO": dict(objType="analogOutput", objClass=AnalogOutputObject),
#     "AV": dict(objType="analogValue", objClass=AnalogValueObject),
# }
BACNET_OBJECT_MAP = {
    "AI": {
        "objType": "analogInput",
        "objClass": AnalogInputObject,
        "datatype": Real,
    },
    "AO": {
        "objType": "analogOutput",
        "objClass": AnalogOutputObject,
        "datatype": Real,
    },
    "AV": {
        "objType": "analogValue",
        "objClass": AnalogValueObject,
        "datatype": Real,
    }
}


def patch_method(method, pvr, operation, objName):
    @wraps(method)
    def wrapper(*args, **kwargs):
        record = dict(ts=datetime.now().isoformat(), op=operation)
        record["obj"] = objName
        record["ioSrc"] = kwargs.pop("ioSrc", "bac")
        record["direct"] = kwargs.get("direct", False)
        result = None
        try:
            result = method(*args, **kwargs)
        except Exception as e:
            log.error(e)
            record["err"] = str(e)
        if operation == "write":
            value = args[1]
            result = value
        else:
            value = result
        record["value"] = value
        pvr.record(**record)
        record_line = " ".join([f"{k}={v}" for (k, v) in record.items()])
        print(record_line)
        return result
    return wrapper


class PresentValueRecorder:
    def __init__(self, limit=100):
        self._log = deque(maxlen=limit)

    def clear(self):
        self._log.clear()

    def record(self, **kwargs):
        self._log.appendleft(kwargs)

    def logs(self):
        return self._log


class BACnetIPSimulator:

    def __init__(self, name, identifier, address):
        self._pvr_map = {}
        self._device = LocalDeviceObject(
            objectName=name,
            objectIdentifier=identifier,
            maxApduLengthAccepted=1024,
            segmentationSupported="segmentedBoth",
            vendorName="SimDev",
            vendorIdentifier=999
        )
        self._app = BIPSimpleApplication(self._device, address)

    @property
    def app(self):
        return self._app

    @property
    def device(self):
        return self._device
    
    def pvr_for(self, objName):
        return self._pvr_map[objName]

    def _init_points_by_type(self, otype, count):
        _type = BACNET_OBJECT_MAP[otype]["objType"]
        _class = BACNET_OBJECT_MAP[otype]["objClass"]
        for i in range(count):
            objectName = f"{otype}-{i}"

            point = _class(
                objectIdentifier=(_type, i),
                objectName=objectName,
                presentValue=0.0
            )

            pvr = PresentValueRecorder()

            if hasattr(point, "ReadProperty"):
                patched = patch_method(
                    point.ReadProperty, pvr, "read", objectName
                )
                point.ReadProperty = patched

            if hasattr(point, "WriteProperty"):
                patched = patch_method(
                    point.WriteProperty, pvr, "write", objectName
                )
                point.WriteProperty = patched
            self._app.add_object(point)

            self._pvr_map[objectName] = pvr

    def _get_obj(self, objName):
        short, num = objName.split("-")
        objType = BACNET_OBJECT_MAP[short.upper()]["objType"]
        num = int(num)
        objId = (objType, num)
        return self._app.objectIdentifier[objId]

    def configure(self, config):
        self.reset()
        for otype, count in config.items():
            otype = otype.upper()
            if otype not in BACNET_OBJECT_MAP:
                raise ValueError(f"Unknown Object Type: {otype}")
            self._init_points_by_type(otype, count)

    def reset(self):
        for o_ident in list(self._app.objectIdentifier.keys()):
            if o_ident[0] == "device":
                continue
            obj = self._app.objectIdentifier[o_ident]
            self._app.delete_object(obj)
        self._pvr_map.clear()

    def read(self, objName, ioSrc="sim"):
        obj = self._get_obj(objName)
        if hasattr(obj, "ReadProperty"):
            value = obj.ReadProperty('presentValue', ioSrc=ioSrc)
            print(value)
            return value

    def write(self, objName, value, ioSrc="sim"):
        # obj = self._obj_map[objName]
        print(objName)
        obj = self._get_obj(objName)
        if hasattr(obj, "WriteProperty"):
            typedValue = float(value)
            return obj.WriteProperty('presentValue', typedValue, ioSrc=ioSrc)
            
    def run(self):
        core.SPIN = 0.1
        core.enable_sleeping()
        core.run()
