# FDB access via uenv

## File Overview

**Python:** Retrieve REA-L-CH1 Data from FDB with Python
- [config.py](config.py): Contains the configuration of the FDB instance
- [radiation.py](radiation.py): Retrieve two parameters at surface level across 10 days
- [wind_10M.py](wind_10M.py): Retrieve two parameters at surface level across a day
- [wind_multi_levels.py](wind_multi_levels.py): Retrieve two parameters on multiple model levels across a day

**Mars:** Retrieve FDB Realtime Data via Mars Request
- [request_model_level.mars](request_model_level.mars): Retrieve one parameter at surface level
- [request_surface.mars](request_surface.mars): Retrieve one parameter on multiple model levels

## Installing the uenv image
1. When using **uenv** on Balfrin for the first time. Create a repo to store the uenv images in the default location `/scratch/mch/<user>/.uenv-images` by executing the following command.
> **Note**: You will receive an error message if the repository has not yet been created.
```
uenv repo create
```
2. In order to use the uenv image we need to pull the image using this command.
> **Note**: The recomended production image is fdb/5.16:v2. Full list of available images is maintained [here](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/801538270/FDB+uenv#List-of-releases).
```
uenv image pull fdb/5.16:v<version>
```

## Running a uenv image
Open a termial and run the image as follows:
```
uenv run --view=fdb fdb/5.16:v<version> -- /user-environment/venvs/fdb/bin/python3 internal_use/<filename>
```
This will load the image in memory, execute the python script and unmount it as soon as the application exits.

## Running a uenv image for development purposes
Start the image:
```
uenv start --view=fdb fdb/5.16:v<version>
```
Now your shell has the image with all FDB libraries loaded.

To stop the image execute:
```
uenv stop
```

## How to retrieve data

### Request structure
The request is a dictionary containing information on the following typical keywords:
- **date**:       Date of the forecast (eg "20121231")
- **time**:       Reference Time (eg "0000")
- **stream**:     Forecasting system used to generated the data (eg "enfo" for ensemble forecast)
- **class**:      Specifies the ECMWF classification given to the data (eg "od" for operational data)
- **expver**:     Identifies the experiment or model version (eg "0001" for operational data)
- **model**:      Model name (eg "icon-ch1-eps")
- **type**:       Type of observation, image or field (eg "cf" for control forecast)
- **levtype**:    Type of horizontal level (eg "ml" for model level)
- **levelist**:   List of levels only needed for multilevel fields (eg "1/to/20")
- **param**:      Parameter ID of a field (eg "50011" for T_2M)
- **step**:       Timestep (eg "1/to/24/by/1" for hourly steps)

More information on the identification keywords are available at [ECMWF - Identification keywords](https://confluence.ecmwf.int/display/UDOC/Identification+keywords).

### Parameters

To match a short name to a parameter ID consult the following page: [eccodes-cosmo-resources](https://github.com/COSMO-ORG/eccodes-cosmo-resources/blob/master/definitions/grib2/localConcepts/edzw/shortName.def).

### Via Python

Make sure the uenv is running in the current shell, then execute:

```
python <path-to-file>
```

### Via Mars Request

Make sure the uenv is running in the current shell, then execute:

```
fdb-read <path-to-mars-request> <gribfile_output>
```

### How to query available data on Balfrin
To check archived data on FDB Realtime, run the following command:
```
uenv run --view=fdb fdb/5.16:v<version> -- fdb-utils list --filter number=0,step=0,time=2100,date=20250802,model=icon-ch1-eps
```
To find out more about the FDB Realtime environement, enter:
```
uenv run --view=fdb fdb/5.16:v<version> -- fdb-info --all
```

## Links

- [Installing the uenv](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON#Install-FDB-and-python-environment%3A)
- [Reading from  FDB](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/1906843/FDB#Reading-from-FDB)
- [REA-L-CH1](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/829947927/REA-L-CH1)
