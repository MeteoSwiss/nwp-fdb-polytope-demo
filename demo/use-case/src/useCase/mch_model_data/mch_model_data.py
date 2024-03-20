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
SOURCE = os.environ.get("MCH_MODEL_DATA_SOURCE")


def get(request: mars.Request) -> dict[str, xr.DataArray]:
    if SOURCE == "FDB":
        if "FDB5_CONFIG" not in os.environ and "FDB5_CONFIG_FILE" not in os.environ:
            logger.error(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )
            raise RuntimeError(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )

        return get_from_fdb(request)
    else:
        return get_from_polytope(request)


def get_from_polytope(request: mars.Request) -> dict[str, xr.DataArray]:
    polytope_client = Client()
    filename = f"{uuid.uuid4()}.grib"

    polytope_client.retrieve("mch", request.to_fdb(), filename)
    datafiles = [Path(filename)]
    reader = GribReader.from_files(datafiles)
    if not isinstance(request.param, str):
        return reader.load_fieldnames(request.param)
    return reader.load_fieldnames([request.param])


def get_from_fdb(request: mars.Request) -> dict[str, xr.DataArray]:
    base = request.to_fdb()
    reader = GribReader(source=DataSource())

    if not isinstance(request.param, str):
        return reader.load({param: base | {"param": param} for param in request.param})

    return reader.load({request.param: base | {"param": request.param}})
