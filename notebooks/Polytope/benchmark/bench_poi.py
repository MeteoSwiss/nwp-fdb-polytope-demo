import os
import yaml
import time


def load_config(path="config.yml"):
    if not os.path.exists(path):
        raise FileNotFoundError(
            "Missing config.yml. Please create one based on config_example.yml."
        )
    with open(path, "r") as f:
        return yaml.safe_load(f)


import json

with open(
    "/scratch/mch/cosuna/nwp-fdb-polytope-demo/notebooks/Polytope/poi_definition_production.geojson",
    "r",
    encoding="utf-8",
) as f:
    data = json.load(f)

    coord = [x["geometry"]["coordinates"] for x in data["features"]]

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
ttime = rounded_time.strftime("%H%M")

# date = "20251027"
# ttime = "1200"
# print("DDD", date, time)

import earthkit.geo.cartography

shapes = earthkit.geo.cartography.country_polygons("Switzerland", resolution=50e6)
print("COORD", coord)

import cartopy.crs as ccrs

# South pole rotation of lon=10, latitude=-43
rotated_crs = ccrs.RotatedPole(pole_longitude=190, pole_latitude=43)

# Convert a point from geographic to rotated coordinates
geo_crs = ccrs.PlateCarree()
rotated_points = [rotated_crs.transform_point(lon, lat, geo_crs) for lon, lat in coord]
rotated_points = [[float(y), float(x)] for (y, x) in rotated_points]

times = []
xvals = [2**i for i in range(10)]
for cnt in xvals:
    feature = {
        "type": "timeseries",
        "time_axis": "step",
        "range": {"start": 0, "end": 33},
        "points": rotated_points[0:cnt],
        "axes": ["longitude", "latitude"],  # first longitude, then latitude
    }

    from meteodatalab import mars

    request = mars.Request(
        param="T_2M",
        date=date,
        time=ttime,
        model=mars.Model.ICON_CH1_EPS,
        levtype=mars.LevType.SURFACE,
        type="pf",
        number=1,
        feature=feature,
    )

    import earthkit.data as ekd

    start = time.time()

    ds = ekd.from_source("polytope", "mchgj", request.to_polytope(), stream=False)
    # print(ds.to_xarray())
    # print(ds._json())

    end = time.time()
    times.append(end - start)

print("Execution :", times)

import matplotlib.pyplot as plt

# Plot the data
plt.plot(xvals, times, marker="o")
plt.title("Simple Plot of Powers of 2")
plt.xlabel("Index")
plt.ylabel("Value")
plt.grid(True)
plt.savefig("plot.png")
plt.show()
