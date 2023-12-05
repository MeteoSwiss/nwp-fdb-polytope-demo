import uuid
from pathlib import Path
from typing import Any

import xarray as xr
from idpi.grib_decoder import GribReader
from polytope.api import Client


def get_from_polytope(
    request: dict[str, Any], fields: list[str]
) -> dict[str, xr.DataArray]:
    polytope_client = Client()
    filename = f"{uuid.uuid4()}.grib"

    polytope_client.retrieve("mch", request, filename)
    datafiles = [Path(filename)]
    reader = GribReader.from_files(datafiles, ref_param=fields[0])
    return reader.load_fieldnames(fields)
