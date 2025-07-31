import earthkit.data as ekd

from config import real_fdb_config

req = {
    "date": "20120101/to/20121231",
    "time": "0000",
    "stream": "enfo",
    "class": "od",
    "expver": "0001",
    "model": "icon-ch1-eps",
    "type": "cf",
    "levtype": "sfc",
    "param": "500011",
    "step": ["0/to/24/by/1"],
}

req2 = {
    "date": "20120101",
    "time": "0000",
    "stream": "enfo",
    "class": "od",
    "expver": "0001",
    "model": "icon-ch1-eps",
    "type": "cf",
    "levtype": "sfc",
    "param": "500027",
    "step": ["0/to/24/by/1"],
}

import time


start = time.time()
fs = ekd.from_source("fdb", req, config=real_fdb_config, stream=True)
for f in fs.group_by("date"):
    ds = f.to_xarray()
    print(ds.date)
end = time.time()

print(f"Total time: {end-start}")
