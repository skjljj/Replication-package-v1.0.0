#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge climate-attention and digital-transformation firm-year indicators."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def read_csv_keyed(path: Path, key_cols: Tuple[str, str] = ("code", "year")) -> Dict[Tuple[str, str], dict]:
    data: Dict[Tuple[str, str], dict] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (str(row.get(key_cols[0], "")).strip(), str(row.get(key_cols[1], "")).strip())
            if key[0] and key[1]:
                data[key] = row
    return data


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Merge firm-year climate and digital indicators.")
    parser.add_argument("--climate", default="data/output/climate_attention.csv")
    parser.add_argument("--digital", default="data/output/digital_transformation.csv")
    parser.add_argument("--output", default="data/output/firm_year_text_indicators.csv")
    args = parser.parse_args(argv)

    climate = read_csv_keyed(Path(args.climate))
    digital = read_csv_keyed(Path(args.digital))
    keys = sorted(set(climate) | set(digital))
    rows = []
    for code, year in keys:
        c = climate.get((code, year), {})
        d = digital.get((code, year), {})
        row = {
            "code": code,
            "year": year,
            "company": c.get("company") or d.get("company") or "",
            "climate_attention": c.get("climate_attention", ""),
            "climate_attention_x100": c.get("climate_attention_x100", ""),
            "climate_keyword_count": c.get("climate_keyword_count", ""),
            "digital_transformation_log1p": d.get("digital_transformation_log1p", ""),
            "digital_total_count": d.get("digital_total_count", ""),
            "ai_count": d.get("ai_count", ""),
            "blockchain_count": d.get("blockchain_count", ""),
            "cloud_count": d.get("cloud_count", ""),
            "big_data_count": d.get("big_data_count", ""),
            "digital_application_count": d.get("digital_application_count", ""),
        }
        rows.append(row)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else [
        "code", "year", "company", "climate_attention", "climate_attention_x100",
        "climate_keyword_count", "digital_transformation_log1p", "digital_total_count",
        "ai_count", "blockchain_count", "cloud_count", "big_data_count", "digital_application_count",
    ]
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} firm-year rows to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
