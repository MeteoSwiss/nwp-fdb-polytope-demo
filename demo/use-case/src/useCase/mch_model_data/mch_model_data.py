import logging
import os

import xarray as xr
from idpi import mars
from idpi.data_source import DataSource
from idpi.grib_decoder import load

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
    return load(DataSource(polytope_collection="mch"), request=request)


def get_from_fdb(request: mars.Request) -> dict[str, xr.DataArray]:
    return load(DataSource(), request=request)
