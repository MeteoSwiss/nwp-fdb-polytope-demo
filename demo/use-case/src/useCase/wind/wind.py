import dataclasses as dc

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from idpi.operators import gis, regrid, wind

from ..mch_model_data import mch_model_data


def get_levels_colors():
    with open("useCase/wind/colormap.txt") as f:
        it = iter(f)
        for _ in range(4):
            next(it)
        levels = [0.0] + [float(v) for v in next(it).split(" ")]
        colors = [tuple(int(v) / 255 for v in line.split(" ") if v) for line in it]
    return levels, colors


def plot_wind():
    # Doesn't work yet
    # request = mars.Request(
    #     ["U_10M", "V_10M"],
    #     date="20230201",
    #     time="0300",
    #     levtype=mars.LevType.SURFACE,
    # )
    request = {
        "class": "od",
        "date": "20230201",
        "expver": "0001",
        "stream": "enfo",
        "time": "0300",
        "model": "COSMO-1E",
        "type": "ememb",
        "number": "0",
        "levtype": "sfc",
        "step": "0",
        "param": ["500027", "500029"],
    }
    ds = mch_model_data.get_from_polytope(request, fields=["U_10M", "V_10M"])

    u_10m = ds["U_10M"].isel(z=0, eps=0, time=0)
    v_10m = ds["V_10M"].isel(z=0, eps=0, time=0)

    ff_10m = wind.speed(u_10m, v_10m)
    # rotate vector fields to the geographic north
    u_g, v_g = gis.vref_rot2geolatlon(u_10m, v_10m)

    ff_10m.attrs["geography"] = u_10m.geography
    u_g.attrs["geography"] = u_10m.geography
    v_g.attrs["geography"] = v_10m.geography

    # regular grid in LV03 coordinates
    target = regrid.RegularGrid(
        "epsg:21781",
        nx=40,
        ny=30,
        xmin=460000,
        xmax=860000,
        ymin=40000,
        ymax=340000,
    )
    # change to web mercator due to bounds
    dst = regrid.RegularGrid.to_crs(target, "epsg:3857")

    # use average sampling because the dst grid is much sparser
    resampling = regrid.Resampling.average
    u = regrid.regrid(u_g, dst=dst, resampling=resampling)
    v = regrid.regrid(v_g, dst=dst, resampling=resampling)

    # the wind speed is a raster and needs to be on a denser grid
    # use cubic resampling since the resolution is about the same as the model grid
    dense = dc.replace(dst, nx=400, ny=300)
    ff = regrid.regrid(u_g, dst=dense, resampling=regrid.Resampling.cubic)

    crs = ccrs.epsg(3857)
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(1, 1, 1, projection=crs)
    m_s_to_knots = 1.94384

    levels, colors = get_levels_colors()
    c = ax.contourf(
        dense.x, dense.y, ff * m_s_to_knots, transform=crs, levels=levels, colors=colors
    )
    fig.colorbar(c, label="knots")

    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)

    ax.quiver(dst.x, dst.y, u, v, transform=crs, scale=500)

    ax.set_title("10m Wind Speed (CTRL)")
    fig.savefig("out/wind.png")
