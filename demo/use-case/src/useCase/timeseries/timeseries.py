import datetime as dt
from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
from idpi import mars
from idpi.operators import destagger, wind

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
def timeseries(ref_time: dt.datetime, lead_time: int, out_path: Path):
    steps = [t * 60 for t in range(lead_time // 60)]
    request = mars.Request(
        ("U_10M", "V_10M"),
        date="20230201",
        time="0300",
        expver="0001",
        number=0,
        step=tuple(steps),
        levtype=mars.LevType.SURFACE,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
    )
    ds = mch_model_data.get(request, ref_param_for_grid="U_10M")
    request_ml = mars.Request(
        ("HHL", "U", "V"),
        date="20230201",
        time="0300",
        expver="0001",
        levelist=(20, 40),
        number=0,
        step=tuple(steps),
        levtype=mars.LevType.MODEL_LEVEL,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
    )
    ds_ml = mch_model_data.get(request_ml, ref_param_for_grid="HHL")

    xi = 588
    yi = 493

    u_point = ds["U_10M"].isel(z=0, eps=0, x=xi, y=yi)
    v_point = ds["V_10M"].isel(z=0, eps=0, x=xi, y=yi)
    result = wind.speed(u_point, v_point)

    u = ds_ml["U"]
    v = ds_ml["V"]
    hhl = ds_ml["HHL"]
    u_ml = destagger.destagger(u, "x")
    v_ml = destagger.destagger(v, "y")

    u_ml_point = u_ml.isel(eps=0, x=xi, y=yi)
    v_ml_point = v_ml.isel(eps=0, x=xi, y=yi)

    hhl_point = hhl.isel(eps=0, x=xi, y=yi)

    result_ml = wind.speed(u_ml_point, v_ml_point)

    m_s_to_knots = 1.94384
    lat = u_point.coords.get("lat").item()
    lon = u_point.coords.get("lon").item()

    plt.figure()
    plt.plot(steps, result * m_s_to_knots, label="10m")
    plt.plot(
        steps,
        result_ml.isel(z=0) * m_s_to_knots,
        label=f"height amsl (m) ~ {hhl_point.isel(z=0).item():.0f}",
    )
    plt.plot(
        steps,
        result_ml.isel(z=1) * m_s_to_knots,
        label=f"height amsl (m) ~ {hhl_point.isel(z=1).item():.0f}",
    )
    title = (
        f"Wind speed timeseries @ZRH ({lat},{lon})\n {ref_time.isoformat()} - COSMO-1E"
    )
    plt.title(title)
    plt.ylabel("knots")
    plt.xlabel("lead time in h")
    plt.grid(which="both")
    plt.legend()
    yb, yt = plt.ylim()
    plt.xlim(0, 23)
    plt.ylim(bottom=0)
    plt.xticks(np.arange(0, 24, step=1), minor=True)
    plt.yticks(np.arange(0, yt, step=5), minor=True)
    plt.savefig(out_path)

    object_name = f"timeseries-demo-{dt.datetime.now().isoformat()}.png"
    upload(out_path, object_name)
