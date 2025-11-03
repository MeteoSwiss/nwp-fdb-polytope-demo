# FDB access via uenv

## File Overview

**Python:** Retrieve from FDB with Python
- [REA-L-CH1 data](https://meteoswiss.atlassian.net/wiki/x/FwB4MQ)
    - [radiation.py](radiation.py): Retrieve two parameters at surface level across 10 days
    - [wind_10M.py](wind_10M.py): Retrieve two parameters at surface level across a day
    - [wind_multi_levels.py](wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day
    - [regrid.py](regrid.py): Retrieve multiple requests and regrid the data
- [Realtime data](https://meteoswiss.atlassian.net/wiki/x/gY_XC)
    - [realtime_radiation.py](realtime_radiation.py): Retrieve two parameters at surface level across 10 days
    - [realtime_wind_10M.py](realtime_wind_10M.py): Retrieve two parameters at surface level across a day
    - [realtime_wind_multi_levels.py](realtime_wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day

**MARS:** Example MARS requests to retrieve via the FDB CLI
- [REA-L-CH1 data](https://meteoswiss.atlassian.net/wiki/x/FwB4MQ)
    - [request_surface.mars](request_surface.mars): Retrieve one parameter at surface level of a control member forecast
    - [request_model_level.mars](request_model_level.mars): Retrieve one parameter on multiple model levels of a control member forecast
- [Realtime data](https://meteoswiss.atlassian.net/wiki/x/gY_XC)
    - [realtime_request_surface.mars](realtime_request_surface.mars): Retrieve one parameter at surface level of a perturbed forecast
    - [realtime_request_model_level.mars](realtime_request_model_level.mars): Retrieve one parameter on multiple model levels of a control member forecast


## Instructions & Installation
To run the scripts or retrieve data via MARS request visit the following page.
- [FDB for NWP Data Access at CSCS](https://meteoswiss.atlassian.net/wiki/x/poR-Ew)

> [!NOTE]
> To execute the script [regrid.py](regrid.py) there is a different set up necessary. See below.

### Installtion for regrid.py

Make sure you navigate to the folder `nwp-fdb-polytope-demo/examples/FDB/scripts/` before proceeding with the next steps.
```sh
uenv start --view=rea-l-ch1 fdb/5.17:2057590964
poetry install
poetry run python regrid.py
```
