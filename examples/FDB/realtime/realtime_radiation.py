import eccodes  # workaround to make fdb use the correct shared libraries (https://meteoswiss.atlassian.net/browse/APNRZ-998)
import earthkit.data as ekd
import time
from datetime import datetime, timedelta

# Request to retrieve ASWDIFD_S and ASWDIR_S at surface level on the current day, hourly

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

# Note: At the moment, for those parameters (500480 & 500481), the timespan keyword means:
#  "none" : only step 0
#  "1h"   : only step 1
#  no timespan keyword : *only steps* >= 2
req = {
    "date": req_date ,
    "time": req_time,
    "stream": "enfo",
    "class": "od",
    "expver": "0001",
    "model": "icon-ch1-eps",
    "type": "cf",
    "levtype": "sfc",
    "param": "500480/500481",
    "step": "2/to/24/by/1",
    #"timespan": "None",
}

# Time data extraction
start = time.time()

# Load data as a stream, otherwise it might not fit in memory
fs = ekd.from_source("fdb", req, stream=True).to_fieldlist()

# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
for f in fs.group_by("date"):
    ds = f.to_xarray()
    print(ds.data_vars)
    print(f"Date : {f[0].metadata('date')}")
end = time.time()

# Print total extraction time
print(f"Total extraction time : {end-start}")
