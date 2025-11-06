# -*- coding: utf-8 -*-
"""
Reusable helpers and demo for working with a list of city dicts.

Defines two functions:
- filter(condition, dict_list): returns only items where condition(item) is True
- aggregate(aggregation_key, aggregation_function, dict_list): extracts values for
  aggregation_key and applies aggregation_function(list_of_values)

Then uses them to reproduce the four actions from Commit 1:
1) Print the average temperature of all the cities
2) Print all cities in Germany
3) Print all cities in Spain with a temperature above 12°C
4) Count the number of unique countries
"""

from __future__ import annotations
import csv
import os
from typing import Callable, Dict, Iterable, List, Any

# NOTE: This shadows Python's built-in `filter`. That's intentional to match the prompt.
def filter(condition: Callable[[Dict[str, Any]], bool], dict_list: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return items from dict_list for which condition(item) is True."""
    return [d for d in dict_list if condition(d)]

def aggregate(aggregation_key: str, aggregation_function: Callable[[List[Any]], Any], dict_list: Iterable[Dict[str, Any]]) -> Any:
    """
    Extract values for `aggregation_key` from dict_list and apply `aggregation_function` to them.
    Example aggregation_function: lambda xs: sum(xs)/len(xs)
    """
    vals: List[Any] = []
    for d in dict_list:
        if aggregation_key in d:
            vals.append(d[aggregation_key])
    return aggregation_function(vals)

def _to_float(x: Any) -> float:
    try:
        return float(x)
    except Exception:
        # If conversion fails, ignore this value by returning NaN sentinel
        return float("nan")

def _load_cities(csv_path_candidates=None) -> List[Dict[str, Any]]:
    """
    Load rows from Cities.csv as a list of dicts.
    Attempts several common locations; accepts a list of path candidates.
    """
    if csv_path_candidates is None:
        csv_path_candidates = [
            "./Cities.csv",
            "Cities.csv",
            "/content/Cities.csv",
            "/mnt/data/Cities.csv",
        ]

    file_path = None
    for p in csv_path_candidates:
        if os.path.exists(p):
            file_path = p
            break

    if not file_path:
        print("⚠️ Could not find Cities.csv in any known location. "
              "Put the file next to this script or update the path list inside _load_cities().")
        return []

    cities: List[Dict[str, Any]] = []
    with open(file_path, newline="", encoding="utf-8") as f:
        rows = csv.DictReader(f)
        for r in rows:
            # Normalize keys to lowercase and strip whitespace from values
            norm = { (k.strip().lower() if isinstance(k,str) else k): (v.strip() if isinstance(v,str) else v) for k, v in r.items() }
            cities.append(norm)
    return cities

def main():
    cities = _load_cities()
    if not cities:
        return

    # 1) Average temperature of all the cities
    avg_temp = aggregate(
        "temperature",
        lambda xs: (sum(_to_float(x) for x in xs) / max(1, sum(0 if (isinstance(_to_float(x), float) and str(_to_float(x)) == 'nan') else 1 for x in xs)))
        if xs else float("nan"),
        cities,
    )
    print("Average temperature of all the cities:", avg_temp)

    # 2) All cities in Germany
    cities_in_germany = filter(
        lambda d: str(d.get("country","")).strip().lower() == "germany",
        cities,
    )
    print("\nCities in Germany:")
    for c in cities_in_germany:
        print(c)

    # 3) All cities in Spain with temperature > 12°C
    spain_above_12 = filter(
        lambda d: str(d.get("country","")).strip().lower() == "spain"
                  and (_to_float(d.get("temperature")) > 12),
        cities,
    )
    print("\nCities in Spain with temperature > 12°C:")
    for c in spain_above_12:
        print(c)

    # 4) Count the number of unique countries
    unique_country_count = aggregate(
        "country",
        lambda xs: len({str(x).strip().lower() for x in xs if str(x).strip()}),
        cities,
    )
    print("\nNumber of unique countries:", unique_country_count)

if __name__ == "__main__":
    main()
