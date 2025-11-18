from pathlib import Path
from uuid import UUID

import earthkit.data as ekd
import xarray as xr
import yaml
from rasterio.crs import CRS

from meteodatalab import icon_grid
from meteodatalab.operators import regrid
from uenv_param_map import shortname_to_paramid



script_dir = Path(__file__).parent
# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
with open(script_dir / "profile.yaml", "r") as file:
    profile = yaml.safe_load(file)

# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
with open(script_dir / "profile_2d.yaml", "r") as file:
    profile_2d = yaml.safe_load(file)


def regrid_dataset(ds, grid_params):

    crs_str, *grid_params = grid_params.split(",")
    crs = CRS.from_string(crs_str)
    xmin, ymin, xmax, ymax, dx, dy = map(int, grid_params)
    nx = (xmax - xmin) / dx + 1
    ny = (ymax - ymin) / dy + 1

    target_grid = regrid.RegularGrid(crs, int(nx), int(ny), xmin, xmax, ymin, ymax)

    regridded_ds = xr.Dataset(
        {var: regrid.iconremap(ds[var], target_grid) for var in ds.data_vars}
    )

    # Add x/y as coordinates
    regridded_ds = regridded_ds.assign_coords(x=target_grid.x, y=target_grid.y)

    return regridded_ds


def add_icon_grid(array):
    hcoords = icon_grid.load_grid_from_balfrin()(UUID(array.attrs["uuidOfHGrid"]))

    array = array.rename({"values": "cell"})
    array = array.assign_coords(
        lon=("cell", hcoords["lon"].data), lat=("cell", hcoords["lat"].data)
    )

    return array


requests = {
    "sfc": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "sfc",
            "step": "0/to/24/by/1",
        },
        "vars": [
            "U_10M",
            "V_10M",
        ],
        "steps": 25,
        "levels": None,
    },
    "ml": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "ml",
            "levelist": "78/to/80",
            "step": "0/to/24/by/1",
        },
        "vars": ["U", "V"],
        "steps": 25,
        "levels": 3,
    },
}

for key, req_info in requests.items():

    print(f"Processing {key}")
    req = req_info["request"]

    req["date"] = "20100917"
    req["param"] = shortname_to_paramid(req_info["vars"])

    # Load data as a stream, otherwise it might not fit in memory
    fs = ekd.from_source("fdb", req, stream=True)

    # Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
    for f in fs.group_by("date"):
        ds = f.to_xarray(profile="grib", **profile)
        for var in ds:
            ds[var] = add_icon_grid(ds[var])
            if key == "10m_avg":
                # Build 1h averages (still sampling at 10')
                ds[var] = ds[var].resample(lead_time="1h").mean()

        if req_info["levels"] and len(ds.coords["z"]) != req_info["levels"]:
            raise RuntimeError("error finding all levelist")
        if req_info["steps"] and len(ds.coords["lead_time"]) != req_info["steps"]:
            raise RuntimeError("error finding all steps")

        out_regrid_target = "epsg:21781,549500,149500,650500,250500,1000,1000"
        swiss_ds = regrid_dataset(ds, out_regrid_target)
        for var in swiss_ds:
            vals = ds.coords["valid_time"].dt.strftime("%Y%m").values
            assert len(vals) == 1
            assert all(x == vals[0][0] for x in vals[0])
            valid_time_month = vals[0][0]
            filename = f"ds_{var}_steps{req_info['steps']}_{valid_time_month}"
            swiss_ds.earthkit.to_netcdf(filename, mode="a")
