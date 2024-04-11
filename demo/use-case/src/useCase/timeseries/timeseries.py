import datetime as dt
from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
from idpi import mars, mch_model_data

from ..util import upload


@click.command()
@click.option(
    "-r",
    "--ref-time",
    type=click.DateTime(["%Y%m%d%H"]),
    default=dt.datetime(2024, 2, 22, 3),
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
    default=Path("out/timeseries.png"),
    help="Output path",
)
def timeseries(ref_time: dt.datetime, lead_time: int, out_path: Path):
    lat = 47.47
    lon = 8.55
    request = mars.Request(
        "U_10M",
        date=ref_time.strftime("%Y%m%d"),
        time=ref_time.strftime("%H00"),
        expver="0001",
        number=1,
        levtype=mars.LevType.SURFACE,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
        feature=mars.TimeseriesFeature(points=[(lat, lon)], end=lead_time),
    )
    u = mch_model_data.get_from_polytope(request)["10 metre U wind component"]
    request = mars.Request(
        "V_10M",
        date=ref_time.strftime("%Y%m%d"),
        time=ref_time.strftime("%H00"),
        expver="0001",
        number=1,
        levtype=mars.LevType.SURFACE,
        model=mars.Model.ICON_CH1_EPS,
        stream=mars.Stream.ENS_FORECAST,
        type=mars.Type.ENS_MEMBER,
        feature=mars.TimeseriesFeature(points=[(lat, lon)], end=lead_time),
    )
    v = mch_model_data.get_from_polytope(request)["10 metre V wind component"]
    result = np.sqrt(u**2 + v**2).squeeze()

    m_s_to_knots = 1.94384
    steps = (u.t - np.datetime64(ref_time)) / np.timedelta64(1, "h")

    plt.figure()
    plt.plot(steps, result * m_s_to_knots, label="10m")
    title = (
        f"Wind speed timeseries @ZRH ({lat},{lon})\n {ref_time.isoformat()} - {request.model!s}"
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
    plt.yticks(np.arange(0, yt, step=1), minor=True)
    plt.savefig(out_path)

    object_name = f"timeseries-demo-{dt.datetime.now().isoformat()}.png"
    upload(out_path, object_name)
