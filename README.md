# FDB and Polytope model data access and processing using meteodata-lab

This repository contains examples for using [FDB](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON) and [Polytope](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/327780397/Polytope) to access ICON forecast data and process it using meteodata-lab.

The directory [notebooks](notebooks) contains the Jupyter notebooks and the directory [nwp_polytope_demo](nwp_polytope_demo) contains examples of processing data as a Python service.

**Forecasts available in FDB**

> [!NOTE]
> The realtime FDB normally contains **just the latest day of forecasts**. This means the FDB requests should usually use date = today and time as either 0000, 0300, 0600, 0900 etc. (given the forecasts run every 3 hour) for ICON-CH1-ENS and 0000, 0600, 1200 etc. for ICON-CH2-ENS. The data is usually available in the FDB a couple of hours after the forecast start time. If the requests to FDB return no data, see these [instructions](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+ICON-CH1#Query-available-data-on-Balfrin) for how to query yourself which data is currently archived in the FDB, or contact victoria.cherkas@meteoswiss.ch.

## What is FDB

FDB allows to retrieve any multi-dimensional dataset of the recent real-time NWP forecasts. FDB is restricted to access within CSCS and feature extracion is not supported

## What is Polytope and Feature Extraction

Polytope allows to extract specific features from the same real-time NWP forecast, such as grid point data, time-series, vertical profiles or polygons. 
Polytope is an HTTP service and therefore access is not restricted to CSCS (it supports LabVM and ACPM).

## Jupyter Notebooks

The following notebooks demonstrate various use cases to access model data (ICON-CH1-ENS & ICON-CH2-ENS): 
* [How to access model data with FDB from CSCS](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/1_Data_Retrieval_from_FDB_Preprocessing.ipynb)
* [How to access feature extraction with Polytope](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/4_Location_and_TimeSeries_Access.ipynb)
* [How to further process NWP data with meteodata-lab](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/3_Retrieve_Echotop_and_Regrid.ipynb)
* [How to store data in FDB](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/notebooks/2_Precompute_and_Store_Echotop_to_FDB.ipynb)
  (for developers)

## Running the Notebooks

For running the notebooks you can [install](#installation-of-own-environment) the runtime environment required for the notebooks or execute them from a ready-made [container](#jupyter-server-in-a-container-labvm-only). 

### Installation of own environment

#### Polytope

```sh
pip install meteodata-lab
```
#### FDB

We use spack for the build and deployment of the FDB environment.

```
spack env activate -p spack-env
spack install --no-checksum
```

```
pip install meteodata-lab
```

###   Jupyter server in a container (LabVM only)
With this approach you have both the Jupyter server and the runtime dependencies in a container.
This simplifies the setup as it doesn't require any local installations or to check out the github
project, but currently does not work in CSCS.

```sh
podman run \
  -p 8888:8888
  --network=host \
  --rm \
  dockerhub.apps.cp.meteoswiss.ch/numericalweatherpredictions/polytope/demo/notebook:<TAG>
```
`<TAG>`:The current container tag can be retrieved from: [https://nexus.meteoswiss.ch/nexus/service/rest/repository/browse/docker-all/v2/numericalweatherpredictions/polytope/demo/notebook/tags/](https://nexus.meteoswiss.ch/nexus/service/rest/repository/browse/docker-all/v2/numericalweatherpredictions/polytope/demo/notebook/tags/)

If you want to persist changes to local versions of the notebooks, run the container from
project directory and mount the local notebooks directory.

```
podman run \
  -p 8888:8888
  --network=host \
  --mount type=bind,src=notebooks,dst=/src/app-root/notebooks/ \
  --rm \
  dockerhub.apps.cp.meteoswiss.ch/numericalweatherpredictions/polytope/demo/notebook:<TAG>
```

Afterwards connect to the external Jupyter server from the notebook with the url from container log.

To rebuild and run the container with local changes, run the following

```sh
podman build --network=host --pull --target notebook -t polytope-demo .
podman run -p 8888:8888 --network=host --rm polytope-demo
```



