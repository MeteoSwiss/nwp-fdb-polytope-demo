import os
import yaml


def load_config(path="config.yml"):
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Missing config.yml. Please create one based on config_example.yml."
        )
    with open(path, "r") as f:
        return yaml.safe_load(f)


config = load_config()

# ICON-CSCS Polytope credentials
os.environ["POLYTOPE_USER_KEY"] = config["meteoswiss"]["key"]
os.environ["POLYTOPE_ADDRESS"] = "https://polytope-depl.mchml.cscs.ch"


from datetime import datetime, timedelta

# Current time
now = datetime.now()

# Subtract 12 hours
past_time = now - timedelta(hours=12)

# Round down to the nearest multiple of 6
rounded_hour = (past_time.hour // 6) * 6
rounded_time = past_time.replace(hour=rounded_hour, minute=0, second=0, microsecond=0)

# Format as YYYYMMDD and HHMM
date = rounded_time.strftime("%Y%m%d")
time = rounded_time.strftime("%H%M")

from meteodatalab import mars

request = mars.Request(
    param="T_2M",
    date=date,
    time=time,
    model=mars.Model.ICON_CH1_EPS,
    levtype=mars.LevType.SURFACE,
    type="pf",
    number=range(1, 11),
    step=range(1, 34),
)

import earthkit.data as ekd

import time

start = time.time()

ds = ekd.from_source("polytope", "mch", request.to_polytope(), stream=False)

end = time.time()
print(ds)
# print("Execution :", end - start)
print(f"Execution time: {end - start} seconds")
