import earthkit.data as ekd
import time
from datetime import datetime, timedelta

# Request to retrieve horizontal wind parameters U and V at model levels 74 to 80 on the current day, hourly

# Current time
now = datetime.now()

# Subtract 12 hours
past_time = now - timedelta(hours=12)

# Round down to the nearest multiple of 6
rounded_hour = (past_time.hour // 6) * 6
rounded_time = past_time.replace(hour=rounded_hour, minute=0, second=0, microsecond=0)

# Format as YYYYMMDD and HHMM
req_date = rounded_time.strftime('%Y%m%d')
req_time = rounded_time.strftime('%H%M')

print(f"date: {req_date}, time: {req_time}")

req = {
    "date": req_date ,
    "time": req_time,
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

# Load data as a stream, otherwise it might not fit in memory
fs = ekd.from_source("fdb", req, stream=True)

# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
for f in fs.group_by("date"):
    ds = f.to_xarray()
    print(ds.data_vars)
    print(f"Date : {ds.date}")
end = time.time()

# Print total extraction time
print(f"Total extraction time : {end-start}")
