#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build customer-supplier dyadic variables from firm-year text indicators.

Input relationship CSV should contain at least:
    customer_code,supplier_code,year

The script attaches customer and supplier climate attention and digital indicators
and computes climate attention divergence:
    climate_attention_divergence = customer_attention - supplier_attention
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def read_indicators(path: Path) -> Dict[Tuple[str, str], dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return {(row["code"].strip(), str(row["year"]).strip()): row for row in reader}


def to_float(x: object) -> Optional[float]:
    try:
        if x is None or str(x).strip() == "":
            return None
        return float(x)
    except Exception:
        return None


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build dyadic customer-supplier climate divergence variables.")
    parser.add_argument("--pairs", required=True, help="CSV with customer_code, supplier_code, year.")
    parser.add_argument("--indicators", default="data/output/firm_year_text_indicators.csv")
    parser.add_argument("--output", default="data/output/dyadic_text_indicators.csv")
    args = parser.parse_args(argv)

    indicators = read_indicators(Path(args.indicators))
    out_rows: List[dict] = []
    with Path(args.pairs).open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            customer = (row.get("customer_code") or row.get("cus_code") or "").strip()
            supplier = (row.get("supplier_code") or row.get("sup_code") or "").strip()
            year = str(row.get("year") or "").strip()
            c = indicators.get((customer, year), {})
            s = indicators.get((supplier, year), {})
            ca = to_float(c.get("climate_attention_x100"))
            sa = to_float(s.get("climate_attention_x100"))
            div = ca - sa if ca is not None and sa is not None else ""
            out = dict(row)
            out.update({
                "customer_climate_attention_x100": ca if ca is not None else "",
                "supplier_climate_attention_x100": sa if sa is not None else "",
                "climate_attention_divergence_x100": div,
                "positive_climate_attention_divergence_x100": div if isinstance(div, float) and div > 0 else (0 if isinstance(div, float) else ""),
                "customer_digital_transformation_log1p": c.get("digital_transformation_log1p", ""),
                "supplier_digital_transformation_log1p": s.get("digital_transformation_log1p", ""),
            })
            if "customer_code" not in out:
                out["customer_code"] = customer
            if "supplier_code" not in out:
                out["supplier_code"] = supplier
            out_rows.append(out)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(out_rows[0].keys()) if out_rows else [
        "customer_code", "supplier_code", "year", "customer_climate_attention_x100",
        "supplier_climate_attention_x100", "climate_attention_divergence_x100",
        "positive_climate_attention_divergence_x100", "customer_digital_transformation_log1p",
        "supplier_digital_transformation_log1p",
    ]
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {len(out_rows)} dyadic rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
