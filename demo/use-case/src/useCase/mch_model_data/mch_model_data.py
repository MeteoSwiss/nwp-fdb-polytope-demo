import logging
import os
import uuid
from pathlib import Path

import xarray as xr
from idpi import mars
from idpi.data_source import DataSource
from idpi.grib_decoder import GribReader
from polytope.api import Client


logger = logging.getLogger(__name__)
FDB_HOST = os.environ.get("FDB_HOST", "http://balfrin-ln002:8989")
SOURCE = os.environ.get("MCH_MODEL_DATA_SOURCE")


def get(request: mars.Request, ref_param_for_grid: str) -> dict[str, xr.DataArray]:
    if SOURCE == "FDB":
        if "FDB5_CONFIG" not in os.environ and "FDB5_CONFIG_FILE" not in os.environ:
            logger.error(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )
            raise RuntimeError(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )

        return get_from_fdb(request, ref_param_for_grid)
    elif SOURCE == "FASTAPI":
        return get_from_fdb_client(request, ref_param_for_grid)
    else:
        return get_from_polytope(request, ref_param_for_grid)


def get_from_polytope(
    request: mars.Request, ref_param_for_grid: str
) -> dict[str, xr.DataArray]:
    polytope_client = Client()
    filename = f"{uuid.uuid4()}.grib"

    polytope_client.retrieve("mch", request.to_fdb(), filename)
    datafiles = [Path(filename)]
    reader = GribReader.from_files(datafiles, ref_param=ref_param_for_grid)
    if not isinstance(request.param, str):
        return reader.load_fieldnames(request.param)
    return reader.load_fieldnames([request.param])


def get_from_fdb(
    request: mars.Request, ref_param_for_grid: str
) -> dict[str, xr.DataArray]:
    base = request.to_fdb()
    reader = GribReader(
        ref_param=base | {"param": ref_param_for_grid},
        source=DataSource(),
    )

    if not isinstance(request.param, str):
        return reader.load({param: base | {"param": param} for param in request.param})

    return reader.load({request.param: base | {"param": request.param}})


def get_from_fdb_client(
    request: mars.Request, ref_param_for_grid: str
) -> dict[str, xr.DataArray]:
    from idpi import fdb_client

    base = request.to_fdb()
    client = fdb_client.FDBClient(FDB_HOST)
    reader = GribReader(
        ref_param=base | {"param": ref_param_for_grid}, source=DataSource(client=client)
    )

    if not isinstance(request.param, str):
        return reader.load({param: base | {"param": param} for param in request.param})

    return reader.load({request.param: base | {"param": request.param}})
