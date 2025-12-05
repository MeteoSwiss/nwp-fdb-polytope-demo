import earthkit.data as ekd
import time

request = {
    "stream": "reanl",
    "class": "rd",
    "expver": "r001",
    "model": "icon-rea-l-ch1",
    "type": "cf",
    "levelist": "1/2",
    "levtype": "ml",
    "param": [500014, 500028], # T and U
    "date": ["20200701/to/20200801"],
    "time": "0000",
    "step": [2,3,4,5]
}

fl = ekd.from_source("fdb", request, lazy=True)
for f in fl.group_by("param"):
    print(f.metadata("param","levelist","step"))
    ds = f.to_xarray(profile="grib")
    start = time.time()
    ds.load()
    end = time.time()
    print(f"load time: {end-start}")
