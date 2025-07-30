# How to run examples

## Installing the uenv image
1. When using **uenv** on Balfrin for the first time. Create a repo in the default location by executing the following command.
```
uenv repo create
```
> **Note**: You will receive an error message if the repository has not ben created yet.

2. In order to use the uenv image we need to pull the image using this command.
```
uenv image pull fdb/5.16:v<version>
```

## Running a uenv image
Run the image as follows:
```
uenv run --view=fdb fdb/5.16:v<version> -- /user-environment/venvs/fdb/bin/python3 examples/<filename>
```
This will load the image in memory and unmount it as soon as the application exits.

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
## Parameters

To match a parameter to a number consult the following page: [meteodatalab/data/field_mappings.yml](https://github.com/MeteoSwiss/meteodata-lab/blob/main/src/meteodatalab/data/field_mappings.yml).
