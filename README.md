<h1 align="center">FDB and Polytope model data access and processing</h1>
<h3 align="center">Jupyter Notebook Examples Using MeteoSwiss NWP Data</h3>

<p align="center">
  <img src="polytope.png" alt="Polytope Image" width="250" />
</p>


This repository contains examples for using [FDB](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON) and [Polytope](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/327780397/Polytope) to access ICON forecast data and process it using meteodata-lab.

**FDB** allows to retrieve any multi-dimensional dataset of the recent real-time ICON NWP forecasts.
FDB is designed to access **full horizontal fields** (feature extraction is not supported) and it is only accessible from within CSCS.

**Polytope** allows to efficiently extract specific **features** from the same real-time ICON NWP forecast, such as grid point data, time-series, vertical profiles or polygons.
Polytope is an HTTP service and therefore access is not restricted to CSCS (it supports access from LabVM and ACPM).

---

## 📓 Notebooks

The following notebook demonstrates how to access ICON-CH1-EPS & ICON-CH2-EPS model data with FDB:
* [How to access model data with FDB from CSCS](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/FDB/realtime/data_retrieve_from_FDB.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/data_retrieve_from_FDB.html)

The following notebooks demonstrate various use cases to access ICON-CH1-EPS & ICON-CH2-EPS model data via Polytope:
**Feature extraction**:
* [Bounding Box](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/Polytope/feature_bounding_box.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/feature_bounding_box.html)
* [Polygon country cut-out](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/Polytope/feature_polygon_country_cut-out.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/feature_polygon_country_cut-out.html)
* [Time Series](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/Polytope/feature_time_series.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/feature_time_series.html)
* [Trajectory](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/Polytope/feature_trajectory.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/feature_trajectory.html)
* [Vertical Profile](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/Polytope/feature_vertical_profile.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/feature_vertical_profile.html)

**Full field retrieval**:
* [Full field](https://github.com/MeteoSwiss/nwp-fdb-polytope-demo/blob/main/examples/Polytope/full_field.ipynb) and [HTML rendered output](https://htmlpreview.github.io/?https://raw.githubusercontent.com/MeteoSwiss/nwp-fdb-polytope-demo/main/examples/snapshots/full_field.html)

---

## 🚀 Getting Started

### Option 1: FDB setup at CSCS
FDB data access requires the FDB libraries. In order to facilitate the use of the notebooks, we provide a pre-built environment with the required libraries, as well as jupyter kernel configuration for VSCode. To download this environment and create/configure a jupyter kernel to use it, run:
```
bash host/install_kernel.sh
```
If you would like to develop Python examples outside of the Juypter notebooks, see https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+for+ICON#How-to-use-it how to use the FDB uenv environment.

#### Using VSCode

Ctrl-Shift P -> 'Notebook: Select Notebook Kernel' -> 'Select Another Kernel' -> 'Jupyter Kernel' -> 'Polytope demo'
> [!TIP]
> * The python extension of VScode should not be in [restricted](https://stackoverflow.com/questions/64723778/visual-studio-code-using-the-microsoft-python-extension-cannot-execute-code) mode.
> 
> * You might need to reload the window Ctrl-Shit P -> 'Developer: Reload Window' in order to let VSCode recognize the newly installed kernel.

### Option 2: Python setup for Polytope

Deploy your own python environment using the following commands. Alternatively, when working at CSCS, you can use Option 1 mentioned above.

1. Install the poetry environment.
```
poetry install
```
2. Install the kernel.
```
poetry run python -m ipykernel install --user --name=polytope-env --display-name "polytope demo"
```

---

## 📚 Forecasts available in FDB

> [!NOTE]
> The realtime FDB normally contains **just the latest day of forecasts**. This means the FDB requests should usually use date = today and time as either 0000, 0300, 0600, 0900 etc. (given the forecasts run every 3 hour) for ICON-CH1-ENS and 0000, 0600, 1200 etc. for ICON-CH2-ENS. The data is usually available in the FDB a couple of hours after the forecast start time. If the requests to FDB return no data, see these [instructions](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+ICON-CH1#Query-available-data-on-Balfrin) for how to query yourself which data is currently archived in the FDB.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for how to update and publish notebooks consistently.
