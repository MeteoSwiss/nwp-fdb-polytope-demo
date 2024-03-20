import datetime as dt
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import click
import idpi.operators.time_operators as time_ops
import matplotlib.pyplot as plt
import numpy as np
from idpi import mars
from idpi.operators.support_operators import get_grid_coords

from ..mch_model_data import mch_model_data
from ..util import upload


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
    default=1440,
    help="End of lead time range, type: int, default: 1440",
)
@click.option(
    "-o",
    "--out-path",
    type=click.Path(path_type=Path),
    default=Path("out/total_precipitation.png"),
    help="Output path",
)
def plot_total_precipitation(ref_time: dt.datetime, lead_time: int, out_path: Path):
    request = mars.Request(
        "TOT_PREC",
        date=ref_time.strftime("%Y%m%d"),
        time=ref_time.strftime("%H00"),
        expver="0001",
        number=0,
        step=(lead_time - 1440, lead_time),
        levtype=mars.LevType.SURFACE,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
    )
    ds = mch_model_data.get(request)

    tot_prec = ds["TOT_PREC"]
    tot_prec_24h = time_ops.delta(tot_prec, np.timedelta64(24, "h"))

    geo = tot_prec_24h.attrs["geography"]

    x, y = _get_x_y(geo)

    crs = _get_crs_rotll(geo)

    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(1, 1, 1, projection=crs)
    ax.set_extent([-3, 1, -1.5, 1], crs=crs)

    ax.add_feature(cfeature.BORDERS, linestyle=":")
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    a = ax.contourf(x, y, tot_prec_24h.isel(eps=0, time=1), transform=crs)

    ax.set_title("Total Precipitation rate (S) (24h)")
    fig.colorbar(a, label="kg m^-2 s^-1")
    fig.savefig(out_path)

    object_name = f"total_precipitation-demo-{dt.datetime.now().isoformat()}.png"
    upload(out_path, object_name)


def _get_crs_rotll(geo):
    pol_lat = -1 * geo["latitudeOfSouthernPoleInDegrees"]
    pol_lon = (geo["longitudeOfSouthernPoleInDegrees"] - 180) % 360

    return ccrs.RotatedPole(pole_longitude=pol_lon, pole_latitude=pol_lat)


def _get_x_y(geo):
    nx = geo["Ni"]
    ny = geo["Nj"]

    lon_min = _normalize(geo["longitudeOfFirstGridPointInDegrees"])
    lat_min = geo["latitudeOfFirstGridPointInDegrees"]

    dlon = geo["iDirectionIncrementInDegrees"]
    dlat = geo["jDirectionIncrementInDegrees"]

    x = get_grid_coords(nx, lon_min, dlon, "x")
    y = get_grid_coords(ny, lat_min, dlat, "y")

    return x, y


def _normalize(angle: float) -> float:
    return np.fmod(angle + 180, 360) - 180
