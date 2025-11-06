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
5) oop_data_processing.py
6) OOP refactor with DataLoader and Table classes.
"""

from __future__ import annotations
import csv
import os
from typing import Any, Callable, Iterable, List, Dict

def _to_float(v: Any) -> float | None:
    try:
        return float(v)
    except Exception:
        return None

def _norm_key(k: Any) -> Any:
    return k.strip().lower() if isinstance(k, str) else k

def _norm_val(v: Any) -> Any:
    return v.strip() if isinstance(v, str) else v

class Table:

    def __init__(self, rows: Iterable[Dict[str, Any]]):
        normalized = []
        for r in rows:
            normalized.append({_norm_key(k): _norm_val(v) for k, v in r.items()})
        self._rows: List[Dict[str, Any]] = list(normalized)

    def __len__(self) -> int:
        return len(self._rows)

    def to_list(self) -> List[Dict[str, Any]]:
        return list(self._rows)

    def filter(self, predicate: Callable[[Dict[str, Any]], bool]) -> "Table":
        return Table(r for r in self._rows if predicate(r))

    def select(self, *cols: str) -> "Table":
        wanted = {c.strip().lower() for c in cols}
        return Table({k: v for k, v in r.items() if k in wanted} for r in self._rows)

    def aggregate(self, key: str, agg_fn: Callable[[List[Any]], Any]) -> Any:
        key = _norm_key(key)
        vals: List[Any] = [r[key] for r in self._rows if key in r]
        return agg_fn(vals)

    def mean(self, key: str) -> float | None:
        key = _norm_key(key)
        nums = [_to_float(r.get(key)) for r in self._rows if key in r]
        nums = [n for n in nums if n is not None]
        if not nums:
            return None
        return sum(nums) / len(nums)

    def unique(self, key: str) -> List[Any]:
        key = _norm_key(key)
        seen = []
        seen_set = set()
        for r in self._rows:
            if key in r:
                v = r[key]
                marker = str(v).strip().lower()
                if marker not in seen_set:
                    seen_set.add(marker)
                    seen.append(v)
        return seen

    def nunique(self, key: str) -> int:
        return len(self.unique(key))


class DataLoader:
    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def find_first_existing(paths: list[str]) -> str | None:
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def load(self) -> Table:
        rows: List[Dict[str, Any]] = []
        with open(self.path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                norm = {_norm_key(k): _norm_val(v) for k, v in r.items()}
                rows.append(norm)
        return Table(rows)

    @classmethod
    def from_common_locations(cls) -> "Table":
        candidates = [
            "./Cities.csv",
            "Cities.csv",
            "/content/Cities.csv",
        ]
        path = cls.find_first_existing(candidates)
        if path is None:
            raise FileNotFoundError(
                "Could not find Cities.csv in common locations. "
                "Put it next to this script or pass an explicit path to DataLoader(path)."
            )
        return cls(path).load()


if __name__ == "__main__":
    try:
        table = DataLoader.from_common_locations()
    except FileNotFoundError as e:
        print(e)
        raise SystemExit(1)

    avg_temp = table.mean("temperature")
    print("Average temperature of all the cities:", avg_temp)

    cities_in_germany = (
        table
        .filter(lambda r: str(r.get("country", "")).strip().lower() == "germany")
        .to_list()
    )
    print("\nCities in Germany:")
    for row in cities_in_germany:
        print(row)

    spain_above_12 = (
        table
        .filter(lambda r: str(r.get("country", "")).strip().lower() == "spain")
        .filter(lambda r: (_to_float(r.get("temperature")) or float("-inf")) > 12)
        .to_list()
    )
    print("\nCities in Spain with temperature > 12°C:")
    for row in spain_above_12:
        print(row)

    uniq_countries_count = table.nunique("country")
    print("\nNumber of unique countries:", uniq_countries_count)