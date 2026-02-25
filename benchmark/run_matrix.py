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
    (500014, "T", "pl", "100/to/900/by/50"),
]

# Feature configurations: (type, step_range)
FEATURES = [
    ("boundingbox", [0, 1], [[5.8, 47.81], [10.5, 45.81]]),
    ("timeseries", [0, 120], [[8.565074, 47.453928]]),
]

# Forecast types
FORECAST_TYPES = [("cf", 1), ("pf", 20)]


def format_coords(points: list) -> str:
    """Format coordinates for display."""
    if len(points) == 1:
        return f"({points[0][0]:.2f},{points[0][1]:.2f})"
    return f"({points[0][0]:.1f},{points[0][1]:.1f})-({points[1][0]:.1f},{points[1][1]:.1f})"


def main():
    base_config = load_config()

    print(
        f"{'param':<8} {'levtype':<7} {'levelist':<10} {'feature':<11} {'type':<4} "
        f"{'members':>7} {'coords':<28} {'time':>7} {'size':>11}"
    )
    print("-" * 100)

    for param_id, name, levtype, levelist in PARAMS:
        for feature_type, step_range, feature_points in FEATURES:
            for forecast_type, num_members in FORECAST_TYPES:
                config = deepcopy(base_config)
                config["benchmark"]["param"] = param_id
                config["benchmark"]["levtype"] = levtype
                config["benchmark"]["levelist"] = levelist
                config["benchmark"]["feature"]["type"] = feature_type
                config["benchmark"]["feature"]["range"] = step_range
                config["benchmark"]["feature"]["points"] = feature_points
                config["benchmark"]["forecast_type"] = forecast_type

                levelist_str = levelist if levelist is not None else "-"
                coords_str = format_coords(feature_points)

                try:
                    result = run(config)
                    print(
                        f"{name:<8} {levtype:<7} {levelist_str:<10} {feature_type:<11} {forecast_type:<4} "
                        f"{num_members:<7} {coords_str:<28} "
                        f"{result['client_time']:>6.2f}s {result['output_size_kb']:>8.1f} KB"
                    )
                except Exception as e:
                    print(
                        f"{name:<8} {levtype:<7} {levelist_str:<10} {feature_type:<11} {forecast_type:<4} "
                        f"{num_members:>7} {coords_str:<28} ERROR: {e}"
                    )


if __name__ == "__main__":
    main()
