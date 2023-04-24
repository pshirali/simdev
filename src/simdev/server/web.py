from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route

import uvicorn
from threading import Thread


class _SimulatorStore:
    def __init__(self):
        self._sim = None

    def set_simulator(self, sim):
        self._sim = sim

    def get_simulator(self):
        return self._sim

SIMULATOR_STORE = _SimulatorStore()

def sim():
    _sim = SIMULATOR_STORE.get_simulator()
    if not _sim:
        raise ValueError("No simulator configured for web based I/O")
    return _sim


def get_value(request):
    objName = request.path_params["objName"]
    objName = objName.upper()        
    response = dict()
    status_code = 200
    try:
        result = sim().read(objName, ioSrc="web")
        if result is None:
            raise ValueError("No value found")
        response["result"] = result
    except KeyError as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 404
    except Exception as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 500
    return JSONResponse(response, status_code=status_code)


def get_logs(request):
    objName = request.path_params["objName"]
    objName = objName.upper()        
    response = dict()
    status_code = 200
    try:
        result = list(sim().pvr_for(objName).logs())
        response["result"] = result
    except KeyError as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 404
    except Exception as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 500
    return JSONResponse(response, status_code=status_code)


def del_logs(request):
    objName = request.path_params["objName"]
    objName = objName.upper()        
    response = dict()
    status_code = 200
    try:
        sim().pvr_for(objName).clear()
    except KeyError as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 404
    except Exception as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 500
    return JSONResponse(response, status_code=status_code)


def put_value(request):
    objName = request.path_params["objName"]
    value = request.path_params["value"]
    objName = objName.upper()        
    response = dict()
    status_code = 200
    try:
        result = sim().write(objName, value, ioSrc="web")
        if result is None:
            raise ValueError("No value found")
        response["result"] = result
    except KeyError as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 404
    except Exception as e:
        eType = e.__class__.__name__
        response["error"] = f"{eType}: {str(e)}"
        status_code = 500
    return JSONResponse(response, status_code=status_code)


routes = [
    Route("/point/{objName}/value", get_value),
    Route("/point/{objName}/value/{value}", put_value, methods=["PUT"]),
    Route("/point/{objName}/logs", get_logs),
    Route("/point/{objName}/logs", del_logs, methods=["DELETE"]),
]


def webserver():
    app = Starlette(debug=False, routes=routes)
    uvicorn.run(app, host="0.0.0.0", port=8000)
