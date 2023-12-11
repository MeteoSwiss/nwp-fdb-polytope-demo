# Polytope Use-Case Demo

After building the container through the VSCode task `Build demo use-case image`, you can run it with the following command from the LabVM.

Replase `<COMMAND_HERE>` with one of the following commands:
 - python -m useCase.total_precipitation
 - python -m useCase.wind
 - python -m useCase.timeseries

Set the environment variable `MCH_MODEL_DATA_SOURCE` to `FDB` if FDB should be accessed directly rather than via Polytope. This also requires the additional environment variable `FDB5_CONFIG`.

## Run container

```shell
podman run \
  -e POLYTOPE_USERNAME=admin \
  -e POLYTOPE_ADDRESS=https://polytope-dev.mchml.cscs.ch \
  -e POLYTOPE_PASSWORD=************ \
  -e https_proxy=$https_proxy \
  -e REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
  -v $(pwd)/demo/use-case/out:/app/out --userns=keep-id \
  --network=host \
  numericalweatherpredictions/polytope/demo/use-case:latest \
  <COMMAND_HERE>
```

## Run container at CSCS

```shell
sarus run \
  -e POLYTOPE_USERNAME=admin \
  -e POLYTOPE_ADDRESS=https://polytope-dev.mchml.cscs.ch \
  -e POLYTOPE_PASSWORD=********** \
  --mount=type=bind,destination=/app/out,src=<outdir> \
  container-registry.meteoswiss.ch/numericalweatherpredictions/polytope/demo/use-case:latest \
  <COMMAND_HERE>
```

Specify the environment variable `FDB5_CONFIG` with the config of FDB
#### Remote
```json
{'type':'remote','engine':'remote','store':'remote','host':'<HOST>','port':'<PORT>'}
```

#### Local
```json
{'type':'local','engine':'toc','schema':'<SCHEMA>','spaces':[{'handler':'Default','roots':[{'path':'<FDB_ROOT>'}]}]}
```
