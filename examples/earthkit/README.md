# Earthkit onboarding

This folder contains a short introduction to **earthkit** using a small MeteoSwiss **ICON-CH2-EPS** forecast.

The notebook covers:

* reading GRIB data with `earthkit.data`;
* inspecting metadata and fields;
* converting data to Xarray and NumPy;
* regridding to regular lat/lon with `earthkit.geo`
* making a quick plot with `earthkit.plots`;
* understanding the role of ecCodes definitions and ICON grids.

## Getting started

The notebook can be run:

* in **Google Colab**.
* locally in Jupyter or VS Code;

No Python environment is required beforehand. The notebook installs the required packages during execution.

## Files

* `earthkit_onboarding_meteoswiss.ipynb` – onboarding notebook.
* `icon-ch2-eps-202607131200-100-t_2m-ctrl.grib2` – sample MeteoSwiss ICON forecast used throughout the notebook.
* `definitions.edzw-2.47.0-1.tar.bz2` – temporary ecCodes definitions required for some MeteoSwiss ICON metadata until the earthkit 1.x compatible definitions are publicly available.

For more information about earthkit, see:

* https://earthkit.ecmwf.int/
* https://earthkit.readthedocs.io/