import earthkit.data as ekd
import time

from config import real_fdb_config

# Request to retrieve ASWDIFD_S and ASWDIR_S at surface level between the 1st and 10th of January 2010, hourly
req = {
    "date": "20100101/to/20100110",
    "time": "0000",
    "stream": "reanl",
    "class": "rd",
    "expver": "r001",
    "model": "icon-rea-l-ch1",
    "type": "cf",
    "levtype": "sfc",
    "param": "500480/500481",
    "step": "0/to/24/by/1",
}

# Time data extraction
start = time.time()

# Load data as a stream, otherwise it might not fit in memory
fs = ekd.from_source("fdb", req, stream=True)

# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
for f in fs.group_by("date"):
    ds = f.to_xarray()
    print(ds.data_vars)
    print(f"Date : {ds.date}")
end = time.time()

# Print total extraction time
print(f"Total extraction time (s): {end-start}")
