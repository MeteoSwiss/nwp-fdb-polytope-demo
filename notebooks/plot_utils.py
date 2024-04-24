from pathlib import Path

import cartopy
import matplotlib.pyplot as plt
import numpy as np
from cartopy import crs as ccrs
from cartopy import feature as cfeature

from meteodatalab.operators.support_operators import get_grid_coords

cartopy.config["pre_existing_data_dir"] = "/scratch/mch/ckanesan/cartopy_data_dir"


def _normalize(angle: float) -> float:
    return np.fmod(angle + 180, 360) - 180


def get_levels_colors():
    path = Path(__file__).parent / "colormap.txt"
    with path.open() as f:
        it = iter(f)
        for _ in range(3):
            next(it)
        levels = [0.0] + [float(v) for v in next(it).split(" ")]
        colors = [tuple(int(v) / 255 for v in line.split(" ") if v) for line in it]
    return levels, colors


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


def plot_tot_prec(field):
    crs = _get_crs_rotll(field.geography)
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(1, 1, 1, projection=crs)

    x, y = _get_x_y(field.geography)
    levels, colors = get_levels_colors()
    c = ax.contourf(
        x, y, field.values, transform=crs, levels=levels, colors=colors
    )
    fig.colorbar(c, label="mm / 6h")

    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.COASTLINE)

    ax.set_title("Total Precipitation 6 hours")


def plot_pot_vortic(field, geo, title):
    crs = _get_crs_rotll(geo)
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(1, 1, 1, projection=crs)

    x, y = _get_x_y(geo)
    levels = np.linspace(-20, 20, 21)
    c = ax.contourf(
        x, y, field.squeeze().values * 1e6, levels, transform=crs, cmap="RdBu",
    )
    fig.colorbar(c, label="potential vorticity units (PVU)")

    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.COASTLINE)

    ax.set_title(title)
