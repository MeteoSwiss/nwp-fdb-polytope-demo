import logging
import os
import uuid
from pathlib import Path

import xarray as xr
from idpi import mars
from idpi.data_source import DataSource
from idpi.grib_decoder import GribReader
from polytope.api import Client


def get(request: mars.Request, ref_param_for_grid: str) -> dict[str, xr.DataArray]:
    if os.environ.get("MCH_MODEL_DATA_SOURCE") == "FDB":
        if "FDB5_CONFIG" not in os.environ and "FDB5_CONFIG_FILE" not in os.environ:
            logging.error(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )
            raise RuntimeError(
                "Required environment variables for FDB are not set. Define one of 'FDB5_CONFIG' or 'FDB5_CONFIG_FILE'"
            )

        return get_from_fdb(request, ref_param_for_grid)
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
    return reader.load_fieldnames(list(request.param))


def get_from_fdb(
    request: mars.Request, ref_param_for_grid: str
) -> dict[str, xr.DataArray]:
    reader = GribReader(ref_param=ref_param_for_grid, source=DataSource())

    if not isinstance(request.param, str):
        return reader.load({params: request.to_fdb() for params in request.param})

    return reader.load({request.param: request.to_fdb()})
