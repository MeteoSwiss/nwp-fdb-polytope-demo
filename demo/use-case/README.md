# Polytope Demo wind

After building the container through the VSCode task `Build demo use-case image`, you can run it with the following command from the LabVM.

Replase `<COMMAND_HERE>` with one of the following commands:
 - python -m useCase.total_precipitation
 - python -m useCase.wind
 - python -m useCase.timeseries


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
