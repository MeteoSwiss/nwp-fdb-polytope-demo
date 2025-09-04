## Notebook development workflow

Edit only in developer_notebooks/. These notebooks do not contain outputs, which keeps diffs small and reviews easy.

notebooks/ contains the executed, user-facing copies (with outputs) and is not intended for code review.

Note: We’ll add automated checks to ensure notebooks/ always reflects developer_notebooks/. For now, reviewers should look only at changes under developer_notebooks/.

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
