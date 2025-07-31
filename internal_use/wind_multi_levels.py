import earthkit.data as ekd
import time

from config import real_fdb_config

# Request to retrieve the two wind parameters U and V at model levels 74 to 80 on the 2nd of january 2012 hourly
req = {
    "date": "20120102",
    "time": "0000",
    "stream": "enfo",
    "class": "od",
    "expver": "0001",
    "model": "icon-ch1-eps",
    "type": "cf",
    "levtype": "ml",
    "levelist": "74/to/80",
    "param": "500028/500030",
    "step": "0/to/24/by/1",
}

# Time data extraction
start = time.time()

# Load data as a stream, otherwise it might be too much data
fs = ekd.from_source("fdb", req, config=real_fdb_config, stream=True)

# Convert each field to a xarray.Dataset and print it variables and the date
for f in fs.group_by("date"):
    ds = f.to_xarray()
    print(ds.data_vars)
    print(f"Model levels: {(ds.coords['level']).values}")
    print(f"Date : {ds.date}")
end = time.time()

# Print total extraction time
print(f"Total extraction time (s): {end-start}")
