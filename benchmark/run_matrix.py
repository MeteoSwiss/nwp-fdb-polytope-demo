#!/usr/bin/env python3
"""
Run benchmark matrix across multiple parameter/feature/forecast configurations.
"""

from copy import deepcopy

from polytope_benchmark import load_config, run

# Parameter configurations: (param_id, name, levtype, levelist)
PARAMS = [
    (500011, "T_2M", "sfc", None),
    (500028, "U", "ml", "74/to/80"),
    (500014, "T", "pl", "/".join(str(p) for p in range(100, 900, 50))),
]

# Feature configurations: (type, step_range)
FEATURES = [
    ("boundingbox", [0, 1]),
    ("timeseries", [0, 120]),
]

# Forecast types
FORECAST_TYPES = ["cf", "pf"]


def format_coords(points: list) -> str:
    """Format coordinates for display."""
    if len(points) == 1:
        return f"({points[0][0]:.2f},{points[0][1]:.2f})"
    return f"({points[0][0]:.1f},{points[0][1]:.1f})-({points[1][0]:.1f},{points[1][1]:.1f})"


def main():
    base_config = load_config()
    num_members = base_config["benchmark"]["num_members"]
    coords = base_config["benchmark"]["feature"]["points"]
    coords_str = format_coords(coords)

    print(
        f"{'param':<8} {'levtype':<7} {'levelist':<10} {'feature':<11} {'type':<4} "
        f"{'members':>7} {'coords':<28} {'time':>7} {'size':>11}"
    )
    print("-" * 100)

    for param_id, name, levtype, levelist in PARAMS:
        for feature_type, step_range in FEATURES:
            for forecast_type in FORECAST_TYPES:
                config = deepcopy(base_config)
                config["benchmark"]["param"] = param_id
                config["benchmark"]["levtype"] = levtype
                config["benchmark"]["levelist"] = levelist
                config["benchmark"]["feature"]["type"] = feature_type
                config["benchmark"]["feature"]["range"] = step_range
                config["benchmark"]["forecast_type"] = forecast_type

                members = num_members if forecast_type == "pf" else 1
                levelist_str = levelist if levelist is not None else "-"

                try:
                    result = run(config)
                    print(
                        f"{name:<8} {levtype:<7} {levelist_str:<10} {feature_type:<11} {forecast_type:<4} "
                        f"{members:<7} {coords_str:<28} "
                        f"{result['client_time']:>6.2f}s {result['output_size_kb']:>8.1f} KB"
                    )
                except Exception as e:
                    print(
                        f"{name:<8} {levtype:<7} {levelist_str:<10} {feature_type:<11} {forecast_type:<4} "
                        f"{members:>7} {coords_str:<28} ERROR: {e}"
                    )


if __name__ == "__main__":
    main()
