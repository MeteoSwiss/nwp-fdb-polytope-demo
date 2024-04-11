import datetime as dt
import logging
import sys
from pathlib import Path

import click
from idpi import grib_decoder, mars, metadata, data_source, mch_model_data
from idpi.operators.destagger import destagger
from idpi.operators.vertical_interpolation import interpolate_k2any
import pyfdb


logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-r",
    "--ref-time",
    type=click.DateTime(["%Y%m%d%H"]),
    default=dt.datetime(2023, 2, 1, 3),
    help="Reference time, format: YYYYMMDDHH",
)
@click.option(
    "-l",
    "--lead-time",
    type=click.INT,
    default=0,
    help="Lead time, type: int, default: 0",
)
@click.option(
    "-o",
    "--out-path",
    type=click.Path(path_type=Path),
    default=Path("echo_top_in_m.grib"),
    help="Output path",
)
def calculate(ref_time: dt.datetime, lead_time: int, out_path: Path):
    compute_echo_top(ref_time, lead_time, out_path)


def compute_echo_top(ref_time: dt.datetime, lead_time: int, out_path: Path):
    logger.info(
        "Computing ECHOTOPinM for %s at T+%sh",
        ref_time.strftime("%Y%m%d_%H"),
        lead_time,
    )

    request = mars.Request(
        "HHL",
        date=ref_time.strftime("%Y%m%d"),
        time=ref_time.strftime("%H00"),
        expver="0001",
        levelist=tuple(range(1, 82)),
        number=0,
        step=0,
        levtype=mars.LevType.MODEL_LEVEL,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
    )
    hhl = mch_model_data.get_from_fdb(request)["HHL"]
    request = mars.Request(
        "DBZ",
        date=ref_time.strftime("%Y%m%d"),
        time=ref_time.strftime("%H00"),
        expver="0001",
        levelist=tuple(range(1, 82)),
        number=tuple(range(11)),
        step=lead_time,
        levtype=mars.LevType.MODEL_LEVEL,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
    )
    dbz = mch_model_data.get_from_fdb(request)["DBZ"]

    logger.info("Data for ECHOTOPinM received.")
    logger.info("Computation of ECHOTOPinM started.")

    fdb = pyfdb.FDB()

    # Calculate ECHOTOPinM
    hfl = destagger(hhl, "z")
    echo_top = interpolate_k2any(hfl, "high_fold", dbz, [15.0], hfl)

    echo_top.attrs |= metadata.override(
        echo_top.message, shortName="ECHOTOPinM", typeOfLevel="echoTopInDBZ"
    )

    logger.info("Archiving ECHOTOPinM in FDB")
    with data_source.cosmo_grib_defs():
        with open("useCase/echo_top/output.grib", "w+b") as tmp:
            grib_decoder.save(echo_top.rename({"DBZ": "z"}), tmp)
            tmp.seek(0)

            fdb.archive(tmp.read())

    logger.info("Done")
