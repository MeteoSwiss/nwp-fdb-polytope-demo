# FDB and Polytope model data access and processing using meteodata-lab

This repository contains examples for using FDB and Polytope to access ICON forecast data and process it using meteodata-lab.

The directory [notebooks](notebooks) contains the Jupyter notebooks and the directory [nwp_polytope_demo](nwp_polytope_demo) contains examples of processing data as a Python service.

**Forecasts available in FDB**

> [!NOTE]
> The realtime FDB normally contains **just the two latest forecasts**. This means the FDB requests should usually use date = today and time as either 0000, 0300, 0600, 0900 etc. (given the forecasts run every 3 hour). The data is usually available in the FDB a couple of hours after the forecast start time. If the requests to FDB return no data, see these [instructions](https://meteoswiss.atlassian.net/wiki/spaces/IW2/pages/144150401/Realtime+FDB+ICON-CH1#Query-available-data-on-Balfrin) for how to query yourself which data is currently archived in the FDB, or contact victoria.cherkas@meteoswiss.ch.

## Jupyter Notebooks

The Jupyter notebooks demonstrate access to model data via [FDB](https://github.com/ecmwf/fdb), the [Polytope server](https://github.com/ecmwf/polytope-server) and the [Polytope library](https://github.com/ecmwf/polytope) (ECMWF), and then the subsequent post-processing via a data processing framework [meteodata-lab](https://github.com/MeteoSwiss/meteodata-lab) (in development). The following use cases are covered by the notebooks:

* Retrieving a specified selection of GRIB fields into an xarray object and processing with meteorological operators.
* Remotely retrieving a very reduced subset of GRIB fields, eg just a few grid points, via the Polytope algorithm, to create a timeseries over an extended period.
* Writing GRIB fields data back to FDB having processed the model data at CSCS.

Notebooks to run from CSCS (Balfrin):
- 1_Data_Retrieval_from_FDB_Preprocessing
- 2_Precompute_and_Store_Echotop_to_FDB

Notebooks to run from the LabVM:
- 3_Retrieve_Echotop_and_Regrid
- 4_Location_and_TimeSeries_Access


> [!NOTE]
> Only a single service account can write data to the aforementioned FDB. This means that the writing of computed GRIB fields in notebook 2 (2_Precompute_and_Store_Echotop_to_FDB) cannot be run by any user on CSCS. Subsequently the reading of this same data on the LabVM in Notebook 3 (3_Retrieve_Echotop_and_Regrid) would only work when notebook 2 was run under this specific service account. Please contact victoria.cherkas@meteoswiss.ch or christian.kanesan@meteoswiss.ch to see the demo in full. Alternatively you can create your own FDB and write back to this.

### Making Changes

When modifying the notebooks, work in the `notebooks` directory.

In order to create snapshots based on the current status of the notebooks in the `notebooks/snapshot` directory, run

```
sh make_snapshots.sh
```

Before submitting, also clear the output of the working version of the notebooks. This makes merges and reviews easier as they do not
also include the much larger diffs to the output. Jenkins will also ensure that the working notebooks have been cleared before allowing
to merge a pull request. To clear notebooks and snapshot run

```
sh make_snapshots.sh -c
```

### Running Instructions

To use the Jupyter notebooks you have the following two options regarding the runtime dependencies and the jupyter server:

1. Build dependencies and create a virtual Python environment (recommended for Balfrin)
1. Run everything from a container (recommended for lab-VM)

### Virtual Environment

With this approach you create an environment that you can run as a jupyter kernel.
Setup takes longer, but you can make changes to the environment and persist changes
to the notebooks.

This assumes you already have spack, conda, and poetry configured.

Create and setup the spack environment.

```sh
spack env activate -p spack-env
spack install --no-checksum
```

Setup the python environment.

```sh
conda create -n polytope-demo python=3.11
conda activate polytope-demo
poetry install --with notebook
```

Configure ECCODES definitions.

```sh
git clone --depth 1 --branch v2.35.0.1dm1 https://github.com/COSMO-ORG/eccodes-cosmo-resources.git ${CONDA_PREFIX}/share/eccodes-cosmo-resources
RUN git clone --depth 1 --branch 2.35.0 https://github.com/ecmwf/eccodes.git ${CONDA_PREFIX}/share/eccodes
export GRIB_DEFINITION_PATH=${CONDA_PREFIX}/share/eccodes-cosmo-resources/definitions:${CONDA_PREFIX}/share/eccodes/definitions
```


Start and connect to the jupyter server either through VSCode or on the terminal.

> [!NOTE]
> With VSCode, you need to have the `Jupyter` VSCode extension (https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) insalled.

#### From VSCode

To start a kernel in VSCode and run the notebook:
* Open the notebook you would like to work on
* In the VSCode Command Palette Run `Notebook: Select Notebook Kernel` and choose `Select Another Kernel... > Python Environments...` and select the `polytope-demo` environment you set up.

If running on CSCS, use a VSCode remote connection.

#### From the terminal

```sh
poetry run jupyter lab --port 8080
```
Either open the URL from the logs directly or in VSCode paste the URL in "Select Kernel" -> "Select another Kernel..." -> "Existing Jupyter Server...".

![Exisiting Jupyter Server...](./host/vscode_remote_jupyter-server.png)

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



## Polytope Python Service Example

The [nwp_polytope_demo](nwp_polytope_demo) directory contains three Python examples of accessing and processing ICON forecast data. You can build the container through the VSCode task `Build demo use-case image` and run it with the following commands from the LabVM or CSCS.

In the instructions below, replace `<COMMAND_HERE>` with one of the following commands:
 - `python -m nwp_polytope_demo.total_precipitation -r 2024022303 -l 1440`
 - `python -m nwp_polytope_demo.wind -r 2024022303 -l 0`
 - `python -m nwp_polytope_demo.timeseries -r 2024022303 -l 1440`

Set the environment variable `MCH_MODEL_DATA_SOURCE` to `FDB` if FDB should be accessed directly rather than via Polytope. This also requires the additional environment variable `FDB5_CONFIG`.

### Configuring FDB

Specify the environment variable `FDB5_CONFIG` with the relevant config of FDB depending on your environment

#### Remote
```json
{"type":"remote","engine":"remote","store":"remote","host":"<HOST>","port":"<PORT>"}
```

#### Local (if running on balfrin)
```json
{"type":"local","engine":"toc","schema":"<SCHEMA>","spaces":[{"handler":"Default","roots":[{"path":"<FDB_ROOT>"}]}]}
```

### Run container in LabVM

```shell
mkdir out
podman run \
  -e POLYTOPE_USERNAME=admin \
  -e POLYTOPE_ADDRESS=https://polytope-dev.mchml.cscs.ch \
  -e POLYTOPE_PASSWORD=************ \
  -e https_proxy=$https_proxy \
  -e REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
  -e SSL_CERT_DIR=/etc/ssl/certs \
  -v $(pwd)/out:/src/app-root/out --userns=keep-id \
  --network=host \
  --rm \
  numericalweatherpredictions/polytope/demo/use-case:latest \
  <COMMAND_HERE>
```

### Run container at CSCS

```shell
sarus run \
  -e POLYTOPE_USERNAME=admin \
  -e POLYTOPE_ADDRESS=https://polytope-dev.mchml.cscs.ch \
  -e POLYTOPE_PASSWORD=********** \
  --mount=type=bind,destination=/src/app-root/out,src=<outdir> \
  container-registry.meteoswiss.ch/numericalweatherpredictions/polytope/demo/use-case:latest \
  <COMMAND_HERE>
```

### Run container at AWS

Use the following command to run the container on AWS ECS.

`SPLIT_COMMAND_HERE = "python","-m","wind",...`

```shell
aws ecs run-task \
  --cluster polytope-demo \
  --task-definition polytope-demo \
  --network-configuration '{ "awsvpcConfiguration": {"subnets":["subnet-098ac0ff2aa40933c","subnet-0c36df0a99fe3b136"],"securityGroups":["sg-0c6a013e82af170f1"],"assignPublicIp":"DISABLED" }}' \
  --launch-type FARGATE \
  --overrides '{ "containerOverrides": [{"name": "polytope_demo", "command": [<SPLIT_COMMAND_HERE>]}]}'
```
