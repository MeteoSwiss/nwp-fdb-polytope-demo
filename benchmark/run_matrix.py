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
    (500035, "QV", "pl", "100/to/900/by/50"),
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

    results = []

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
                config["benchmark"]["num_members"] = num_members

                levelist_str = levelist if levelist is not None else "-"
                coords_str = format_coords(feature_points)
                steps_str = f"{step_range[0]}-{step_range[1]}"

                try:
                    result = run(config)
                    results.append(
                        f"{name:<8} "
                        f"{levtype:<7} {levelist_str:<16} "
                        f"{feature_type:<11} {coords_str:<28} {steps_str:<8} "
                        f"{forecast_type:<4} {num_members:<7} "
                        f"{result['client_time']:10.2f}s {result['server_timings']['run_time']:>10.2f}s {result['no_values']:>8} points"
                    )
                except Exception as e:
                    results.append(
                        f"{name:<8} "
                        f"{levtype:<7} {levelist_str:<16} "
                        f"{feature_type:<11} {coords_str:<28} {steps_str:<8} "
                        f"{forecast_type:<4} {num_members:<7} "
                        f"ERROR: {e}"
                    )

    print(
        f"{'param':<8} "
        f"{'levtype':<7} {'levelist':<16} "
        f"{'feature':<11} {'coords':<28} {'steps':<8} "
        f"{'type':<4} {'members':>7} "
        f"{'client-side':>11} {'server-side':>11} {'size':>15}"
    )
    print("-" * 135)
    for line in results:
        print(line)

if __name__ == "__main__":
    main()
