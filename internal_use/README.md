# FDB access via uenv

## File Overview

**Python:** Retrieve [REA-L-CH1](https://meteoswiss.atlassian.net/wiki/x/FwB4MQ) Data from FDB with Python
- [config.py](config.py): Contains the configuration of the FDB instance
- [radiation.py](radiation.py): Retrieve two parameters at surface level across 10 days
- [wind_10M.py](wind_10M.py): Retrieve two parameters at surface level across a day
- [wind_multi_levels.py](wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day

**MARS:** Example MARS requests to retrieve [Realtime](https://meteoswiss.atlassian.net/wiki/x/gY_XC) data via the FDB CLI
- [request_surface.mars](request_surface.mars): Retrieve one parameter at surface level of a perturbed forecast
- [request_model_level.mars](request_model_level.mars): Retrieve one parameter on multiple model levels of a control member forecast

## Instructions

- [FDB for NWP Data Access at CSCS](https://meteoswiss.atlassian.net/wiki/x/poR-Ew)
