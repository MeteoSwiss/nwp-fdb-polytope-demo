import logging
import os
import uuid
from pathlib import Path
from typing import Any

import xarray as xr
from idpi.data_source import DataSource
from idpi.grib_decoder import GribReader
from polytope.api import Client


def get(request: dict[str, Any], fields: list[str]) -> dict[str, xr.DataArray]:
    if os.environ.get("MCH_MODEL_DATA_SOURCE") == "FDB":
        if "FDB5_CONFIG" not in os.environ and "FDB5_CONFIG_FILE" not in os.environ:
            logging.error(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )
            raise RuntimeError(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )

        return get_from_fdb(request, fields)
    else:
        return get_from_polytope(request, fields)


def get_from_polytope(
    request: dict[str, Any], fields: list[str]
) -> dict[str, xr.DataArray]:
    polytope_client = Client()
    filename = f"{uuid.uuid4()}.grib"

    polytope_client.retrieve("mch", request, filename)
    datafiles = [Path(filename)]
    reader = GribReader.from_files(datafiles, ref_param=fields[0])
    return reader.load_fieldnames(fields)


def get_from_fdb(request: dict[str, Any], fields: list[str]) -> dict[str, xr.DataArray]:
    reader = GribReader(ref_param=fields[0], source=DataSource())

    if not isinstance(request["param"], str):
        return reader.load({params: request for params in request["param"]})

    return reader.load({request["param"]: request})
