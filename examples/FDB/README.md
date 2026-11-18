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
> 1. Clone meteodata-lab:
>    ```bash
>    git clone https://github.com/MeteoSwiss/meteodata-lab.git
>    ```
> 2. Add its `src` folder to `PYTHONPATH`, keeping the existing entries:
>    ```bash
>    export PYTHONPATH=/path/to/meteodata-lab/src:$PYTHONPATH
>    ```
> 3. Add package metadata so `meteodata-lab` is recognised as installed. Create the folder
>    `meteodata-lab/src/meteodata_lab-0.0.0+local.dist-info` with a file `METADATA` in it:
>    ```bash
>    mkdir -p /path/to/meteodata-lab/src/meteodata_lab-0.0.0+local.dist-info
>    cat > /path/to/meteodata-lab/src/meteodata_lab-0.0.0+local.dist-info/METADATA <<EOF
>    Metadata-Version: 2.1
>    Name: meteodata-lab
>    Version: 0.0.0+local
>    EOF
>    ```
