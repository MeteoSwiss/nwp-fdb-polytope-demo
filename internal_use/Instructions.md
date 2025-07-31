### FDB access via uenv

#### File Overview

- [radiation.py](radiation.py): single parameter surface level across a year
- [wind_10M.py](wind_10M.py): two parameters surface level across a day
- [wind_multi_levels.py](wind_multi_levels.py): two parameters on multiple model level across a day

#### Installing the uenv image
1. When using **uenv** on Balfrin for the first time. Create a repo in the default location by executing the following command.
```
uenv repo create
```
> **Note**: You will receive an error message if the repository has not yet been created.

2. In order to use the uenv image we need to pull the image using this command.
```
uenv image pull fdb/5.16:v<version>
```

#### Running a uenv image
Run the image as follows:
```
uenv run --view=fdb fdb/5.16:v<version> -- /user-environment/venvs/fdb/bin/python3 internal_use/<filename>
```
This will load the image in memory and unmount it as soon as the application exits.

#### Running a uenv image for development purposes
Start the image:
```
uenv start --view=fdb fdb/5.16:v<version>
```
Now your shell has the image with all FDB libraries loaded.

To stop the image execute:
```
uenv stop
```
#### Request structure
The request is a dictionary containing information on the following typical keywords:
- **"date"**:       Date of the forecast (eg "20121231")
- **"time"**:       Reference Time (eg "0000")
- **"stream"**:     Forecasting system used to generated the data (eg "enfo" for ensemble forecast)
- **"class"**:      Specifies the ECMWF classification given to the data (eg "od" for operational data)
- **"expver"**:     Identifies the experiment or model version (eg "0001" for operational data)
- **"model"**:      Model name (eg "icon-ch1-eps")
- **"type"**:       Type of observation, image or field (eg "cf" for control forecast)
- **"levtype"**:    Type of horizontal level (eg "ml" for model level)
- **"levelist"**:   List of levels only needed for multilevel fields (eg "1/to/20")
- **"param"**:      Parameter of a field (eg "50011" for T_2M)
- **"step"**:       Timestep (eg "1/to/24/by/1" for hourly steps)

To check the full list of identification keywords go to [ECMWF - Identification keywords](https://confluence.ecmwf.int/display/UDOC/Identification+keywords).

#### Parameters

To match a parameter to a number consult the following page: [meteodatalab/data/field_mappings.yml](https://github.com/MeteoSwiss/meteodata-lab/blob/main/src/meteodatalab/data/field_mappings.yml).

#### Links

- [Installing the uenv](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON#Install-FDB-and-python-environment%3A)
- [REA-L-CH1](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/829947927/REA-L-CH1)
