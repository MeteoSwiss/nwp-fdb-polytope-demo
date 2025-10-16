# FDB access via uenv

## File Overview

**Python:** Retrieve REA-L-CH1 Data from FDB with Python
- [radiation.py](radiation.py): Retrieve two parameters at surface level across 10 days
- [wind_10M.py](wind_10M.py): Retrieve two parameters at surface level across a day
- [wind_multi_levels.py](wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day
- [regrid.py](regrid.py): Retrieve multiple requests and regrid the data

**MARS:** Example MARS requests to retrieve data via the FDB CLI
- [request_surface.mars](request_surface.mars): Retrieve one parameter at surface level
- [request_model_level.mars](request_model_level.mars): Retrieve one parameter on multiple model levels

## Instructions
- [FDB for NWP Data Access at CSCS](https://meteoswiss.atlassian.net/wiki/x/poR-Ew)

### Installation Instructions for regrid.py
To run the script `regrid.py`, there is a different set up necessary. Make sure you navigate to the folder `nwp-fdb-polytope-demo/internal_use` before proceeding with the next steps.
```sh
uenv start --view=rea-l-ch1 fdb/5.17:2057590964
poetry install
poetry run python regrid.py
```
