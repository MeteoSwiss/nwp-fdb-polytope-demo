# FDB and Polytope model data access and processing using meteodata-lab

This repository contains examples for using [FDB](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON) and [Polytope](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/327780397/Polytope) to access ICON forecast data and process it using meteodata-lab.

The directory [notebooks](notebooks) contains the Jupyter notebooks and the directory [nwp_polytope_demo](nwp_polytope_demo) contains examples of processing data as a Python service.

**Forecasts available in FDB**

> [!NOTE]
> The realtime FDB normally contains **just the latest day of forecasts**. This means the FDB requests should usually use date = today and time as either 0000, 0300, 0600, 0900 etc. (given the forecasts run every 3 hour) for ICON-CH1-ENS and 0000, 0600, 1200 etc. for ICON-CH2-ENS. The data is usually available in the FDB a couple of hours after the forecast start time. If the requests to FDB return no data, see these [instructions](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+ICON-CH1#Query-available-data-on-Balfrin) for how to query yourself which data is currently archived in the FDB.

## What is FDB

FDB allows to retrieve any multi-dimensional dataset of the recent real-time ICON NWP forecasts. 
FDB is designed to access full horizontal fields (feature extraction is not supported) and it is only accessible from within CSCS.

### Installation
FDB data access requires the FDB libraries. In order to facilitate the use of the notebooks, we provide a jupyter kernel configuration for VSCode that will load the environment with the required libraries:

```
bash host/install_kernel.sh
```

#### From VSCode
(you might need to reload the window Ctrl-Shit P -> 'Developer: Reload Window' in order to let VSCode recognize the newly installed kernel)

Ctrl-Shift P -> 'Notebook: Select Notebook Kernel' -> 'Select Another Kernel' -> 'Jupyter Kernel' -> 'Polytope demo'

#### FDB environment for python
If you would like to develop python examples outside of the juypeter notebooks, see TODO how to use the FDB uenv environment .

## Jupyter Notebooks

The following notebooks demonstrate how to access ICON model data (ICON-CH1-ENS & ICON-CH2-ENS) through FDB: 
* [How to access model data with FDB from CSCS](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/1_Data_Retrieval_from_FDB_Preprocessing.ipynb)
* [How to store data in FDB](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/2_Precompute_and_Store_Echotop_to_FDB.ipynb)
  (for developers)

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
* [How to access feature extraction with Polytope](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/4_Location_and_TimeSeries_Access.ipynb)
* [How to further process NWP data with meteodata-lab](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/3_Retrieve_Echotop_and_Regrid.ipynb)

