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

HEADERS = [
    "param", "levtype", "levelist", "feature", "coords",
    "steps", "type", "members", "client-side", "GJ axes", "GJ extract", "size",
]



def main():
    base_config = load_config()

    rows = []

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
                prefix = [name, levtype, levelist_str, feature_type, coords_str, steps_str, forecast_type, str(num_members)]

                try:
                    result = run(config)
                    rows.append(prefix + [
                        f"{result['client_time']:.2f}s",
                        f"{result['server_timings']['axes']['run_time']:.2f}s",
                        f"{result['server_timings']['extract']['run_time']:.2f}s",
                        f"{result['no_values']} points",
                    ])
                except Exception as e:
                    rows.append(prefix + ["ERROR", "ERROR", "ERROR", str(e)])

    print(format_markdown_table(rows))
    

def format_markdown_table(rows: list[list[str]]) -> str:
    """Format rows as a markdown table, computing column widths from content."""
    col_widths = [
        max(len(HEADERS[i]), max(len(row[i]) for row in rows))
        for i in range(len(HEADERS))
    ]

    def format_row(values: list[str]) -> str:
        cells = (f" {v:<{col_widths[i]}} " for i, v in enumerate(values))
        return "|" + "|".join(cells) + "|"

    separator = "|" + "|".join(f" {'-' * col_widths[i]} " for i in range(len(HEADERS))) + "|"

    lines = [format_row(HEADERS), separator] + [format_row(row) for row in rows]
    return "\n".join(lines)

def format_coords(points: list) -> str:
    """Format coordinates for display."""
    if len(points) == 1:
        return f"({points[0][0]:.2f},{points[0][1]:.2f})"
    return f"({points[0][0]:.1f},{points[0][1]:.1f})-({points[1][0]:.1f},{points[1][1]:.1f})"

if __name__ == "__main__":
    main()
