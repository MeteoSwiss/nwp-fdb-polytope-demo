# FDB access via uenv

## File Overview

**Python:** Retrieve from FDB with Python
- [REA-L-CH1 data](https://meteoswiss.atlassian.net/wiki/x/FwB4MQ)
    - [radiation.py](rea-l-ch1/radiation.py): Retrieve two parameters at surface level across 10 days
    - [wind_10M.py](rea-l-ch1/wind_10M.py): Retrieve two parameters at surface level across a day
    - [wind_multi_levels.py](rea-l-ch1/wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day
    - [regrid.py](rea-l-ch1/regrid.py): Retrieve multiple requests and regrid the data
- [Realtime data](https://meteoswiss.atlassian.net/wiki/x/gY_XC)
    - [realtime_radiation.py](realtime/realtime_radiation.py): Retrieve two parameters at surface level across 10 days
    - [realtime_wind_10M.py](realtime/realtime_wind_10M.py): Retrieve two parameters at surface level across a day
    - [realtime_wind_multi_levels.py](realtime/realtime_wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day

**MARS:** Example MARS requests to retrieve via the FDB CLI
- [REA-L-CH1 data](https://meteoswiss.atlassian.net/wiki/x/FwB4MQ)
    - [request_surface.mars](rea-l-ch1/request_surface.mars): Retrieve one parameter at surface level of a control member forecast
    - [request_model_level.mars](rea-l-ch1/request_model_level.mars): Retrieve one parameter on multiple model levels of a control member forecast
- [Realtime data](https://meteoswiss.atlassian.net/wiki/x/gY_XC)
    - [realtime_request_surface.mars](realtime/realtime_request_surface.mars): Retrieve one parameter at surface level of a perturbed forecast
    - [realtime_request_model_level.mars](realtime/realtime_request_model_level.mars): Retrieve one parameter on multiple model levels of a control member forecast

**Jupyter:** Retrieve from FDB
- [data_retrieve_from_FDB.ipynb](realtime/data_retrieve_from_FDB.ipynb)


## Instructions & Installation
To run the scripts or retrieve data via MARS request visit the following page.
- [FDB for NWP Data Access at CSCS](https://meteoswiss.atlassian.net/wiki/x/poR-Ew)

> [!NOTE]
> The script [regrid.py](rea-l-ch1/regrid.py) also needs [meteodata-lab](https://github.com/MeteoSwiss/meteodata-lab).
> This is only a **temporary workaround** until earthkit releases the swissgrid regridding.
>
> 1. Create and activate a virtual environment as described in [Create the venv](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/327124134/FDB+for+NWP+Data+Access+at+CSCS#Create-the-venv) (Confluence).
> 2. Install meteodata-lab without its dependencies (they are already provided by the uenv):
>    ```bash
>    pip install --no-deps "meteodata-lab @ git+https://github.com/MeteoSwiss/meteodata-lab.git@v0.8.2"
>    ```
> 3. Go to the directory containing the script and run it::
>    ```bash
>    python regrid.py
>    ```
