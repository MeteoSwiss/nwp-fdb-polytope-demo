# FDB and Polytope model data access and processing

This repository contains examples for using [FDB](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON) and [Polytope](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/327780397/Polytope) to access ICON forecast data and process it using meteodata-lab.

The directory [notebooks](notebooks) contains the Jupyter notebooks and the directory [nwp_polytope_demo](nwp_polytope_demo) contains examples of processing data as a Python service. The directory [examples](examples) shows you have to access [FDB](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON) using [earthkit-data](https://earthkit-data.readthedocs.io/en/latest/).

**Forecasts available in FDB**

> [!NOTE]
> The realtime FDB normally contains **just the latest day of forecasts**. This means the FDB requests should usually use date = today and time as either 0000, 0300, 0600, 0900 etc. (given the forecasts run every 3 hour) for ICON-CH1-ENS and 0000, 0600, 1200 etc. for ICON-CH2-ENS. The data is usually available in the FDB a couple of hours after the forecast start time. If the requests to FDB return no data, see these [instructions](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+ICON-CH1#Query-available-data-on-Balfrin) for how to query yourself which data is currently archived in the FDB.

## What is FDB

FDB allows to retrieve any multi-dimensional dataset of the recent real-time ICON NWP forecasts.
FDB is designed to access full horizontal fields (feature extraction is not supported) and it is only accessible from within CSCS.

### FDB access via uenv

#### Installing the uenv image
1. When using **uenv** on Balfrin for the first time. Create a repo in the default location by executing the following command.
```
uenv repo create
```
> **Note**: You will receive an error message if the repository has not ben created yet.

2. In order to use the uenv image we need to pull the image using this command.
```
uenv image pull fdb/5.16:v<version>
```

#### Running a uenv image
Run the image as follows:
```
uenv run --view=fdb fdb/5.16:v<version> -- /user-environment/venvs/fdb/bin/python3 examples/<filename>
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
#### Parameters

To match a parameter to a number consult the following page: [meteodatalab/data/field_mappings.yml](https://github.com/MeteoSwiss/meteodata-lab/blob/main/src/meteodatalab/data/field_mappings.yml).

### FDB Installation
FDB data access requires the FDB libraries. In order to facilitate the use of the notebooks, we provide a jupyter kernel configuration for VSCode that will load the environment with the required libraries:

```
bash host/install_kernel.sh
```

#### From VSCode
(you might need to reload the window Ctrl-Shit P -> 'Developer: Reload Window' in order to let VSCode recognize the newly installed kernel)

Ctrl-Shift P -> 'Notebook: Select Notebook Kernel' -> 'Select Another Kernel' -> 'Jupyter Kernel' -> 'Polytope demo'

Also make sure the python extension of VScode is not in [restricted](https://stackoverflow.com/questions/64723778/visual-studio-code-using-the-microsoft-python-extension-cannot-execute-code) mode

#### FDB environment for python
If you would like to develop python examples outside of the juypeter notebooks, see TODO how to use the FDB uenv environment .

## Jupyter Notebooks

The following notebooks demonstrate how to access ICON model data (ICON-CH1-ENS & ICON-CH2-ENS) through FDB:
* [How to access model data with FDB from CSCS](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/FDB/data_retrieve_from_FDB.ipynb)

## What is Polytope and Feature Extraction

Polytope allows to efficiently extract specific features from the same real-time ICON NWP forecast, such as grid point data, time-series, vertical profiles or polygons.
Polytope is an HTTP service and therefore access is not restricted to CSCS (it supports access from LabVM and ACPM).

### Installation
You can follow the same installation of jupyter kernel as with [FDB](#Installation)
or
deploy your own python environment and
```
poetry install
```

### Jupyter Notebooks

The following notebooks demonstrate various use cases to access model data (ICON-CH1-ENS & ICON-CH2-ENS):
* [How to use feature extraction with Polytope](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/polytope_feature_extraction_icon.ipynb)
* [How to access entire fields with Polytope](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/polytope_retrieve_full_icon_field.ipynb) -> Notice when accessing data from CSCS, using FDB instead will be significantly faster.
