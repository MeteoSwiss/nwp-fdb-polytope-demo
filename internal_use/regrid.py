import earthkit.data as ekd

from config import real_fdb_config
import yaml
from meteodatalab.operators import regrid
from meteodatalab import icon_grid
import xarray as xr
from uuid import UUID
from pathlib import Path

script_dir = Path(__file__).parent
# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
with open(script_dir / "profile.yaml", "r") as file:
    profile = yaml.safe_load(file)

# Convert each field to a xarray.Dataset and print the available parameters and the date of the dataset.
with open(script_dir / "profile_2d.yaml", "r") as file:
    profile_2d = yaml.safe_load(file)


mapfile = "/user-environment/env/rea-l-ch1/share/metkit/paramids.yaml"
with open(mapfile, "r") as file:
    param_map_ = yaml.safe_load(file)
    param_map = {}
    for key, val in param_map_.items():
        if int(key) < 500000:
            continue
        param_map[val[0]] = key

    param_map["clcl"] = 500048
    param_map["clch"] = 500050
    param_map["asob_s"] = 500078
    param_map["athb_s"] = 500080
    param_map["runoff_g"] = 500066
    param_map["runoff_s"] = 500068
    param_map["clcm"] = 500049


def var_to_paramid(param_names):
    return [param_map[param.lower()] for param in param_names]


def regrid_dataset(ds, grid_params, x_y_as_dims):
    target_grid = regrid.RegularGrid.parse_regrid_operator(grid_params)

    regridded_ds = xr.Dataset(
        {var: regrid.iconremap(ds[var], target_grid) for var in ds.data_vars}
    )

    # Add x/y as coordinates
    regridded_ds = regridded_ds.assign_coords(x=target_grid.x, y=target_grid.y)

    #    if not x_y_as_dims:
    #        return regridded_ds.swap_dims({"y": "lat", "x": "lon"})

    return regridded_ds


def add_icon_grid(array):
    hcoords = icon_grid.load_grid_from_balfrin()(UUID(array.attrs["uuidOfHGrid"]))

    array = array.rename({"values": "cell"})
    array = array.assign_coords(
        lon=("cell", hcoords["lon"].data), lat=("cell", hcoords["lat"].data)
    )

    return array


requests = {
    "cons": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "sfc",
            "step": "0",
        },
        "vars": ["HSURF"],
        "steps": None,
        "levels": None,
    },
    "cons_ml": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "ml",
            "step": "0",
            "levelist": "74/to/80",
        },
        "vars": ["HHL"],
        "steps": None,
        "levels": None,
    },
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
            "ALB_RAD",
            "CLCT",
            "DURSUN",
            "H_SNOW",
            "PMSL",
            "U_10M",
            "V_10M",
            "SNOW_GSP",
            "GRAU_GSP",
            "SKT",
            "T_G",
            "T_2M",
            "TD_2M",
            "TOT_PREC",
            "PS",
            "ASOB_S",
            "ATHD_S",
            "ATHU_S",
            "ALHFL_S",
            "ASHFL_S",
            "RAIN_GSP",
            "RUNOFF_G",
            "W_SNOW",
            "W_I",
            "TWATER",
            "CAPE_ML",
            "CAPE_MU",
            "HZEROCL",
            "ASWDIFU_S",
            #    "WSPD_1h",
            "ASWDIR_S",
            "ASWDIFD_S",
        ],
        "steps": 25,
        "levels": None,
    },
    "sfc_nostep0": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "sfc",
            "step": "1/to/24/by/1",
        },
        "vars": [
            "VMAX_10M",
        ],
        "steps": 24,
        "levels": None,
    },
    "dp1": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "dp",
            "levelist": ["0", "0.005", "0.02", "0.06", "0.18", "0.54", "1.62", "4.86"],
            "step": "0/to/24/by/1",
        },
        "vars": ["T_SO"],
        "steps": 25,
        "levels": 8,
    },
    "dp2": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "dp",
            "levelist": ["0", "0.01", "0.03", "0.09", "0.27", "0.81", "2.43", "7.29"],
            "step": "0/to/24/by/1",
        },
        "vars": ["W_SO"],
        "steps": 25,
        "levels": 8,
    },
    "10m_sfc": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "sfc",
            "step": "0m/to/1441m/by/10m",
        },
        "vars": ["TOT_PREC", "DHAIL_MX", "DBZ_CMAX"],
        "steps": 145,
        "levels": None,
    },
    "10m_avg": {
        "request": {
            "time": "0000",
            "stream": "reanl",
            "class": "rd",
            "expver": "r001",
            "model": "icon-rea-l-ch1",
            "type": "cf",
            "levtype": "sfc",
            "step": "0m/to/1441m/by/10m",
        },
        "vars": ["U_10M_AV", "V_10M_AV"],
        "steps": 144, # steps - 1 because of avarage function
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
            "levelist": "74/to/80",
            "step": "0/to/24/by/1",
        },
        "vars": ["U", "V"],
        "steps": 25,
        "levels": 7,
    },
}

for key, req_info in requests.items():

    print(f"Processing {key}")
    req = req_info["request"]

    req["date"] = "20100917/to/20100920"
    req["param"] = var_to_paramid(req_info["vars"])

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

        out_regrid_target = "swiss,549500,149500,650500,250500,1000,1000"
        swiss_ds = regrid_dataset(ds, out_regrid_target, False)
        for var in swiss_ds:
            vals = ds.coords["valid_time"].dt.strftime("%Y%m").values
            assert len(vals) == 1
            assert all(x == vals[0][0] for x in vals[0])
            valid_time_month = vals[0][0]

            filename = f"ds_{var}_steps{req_info['steps']}_{valid_time_month}"
            swiss_ds.earthkit.to_netcdf(filename, mode="a")
