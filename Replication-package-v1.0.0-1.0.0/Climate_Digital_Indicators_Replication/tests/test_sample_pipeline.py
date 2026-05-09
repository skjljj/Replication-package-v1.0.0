#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke test for the sample pipeline."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    cmd = [
        sys.executable, "run_all.py",
        "--pdf-dir", "data/sample",
        "--metadata", "data/sample/report_metadata.csv",
        "--txt-dir", "data/intermediate/test_sample_txt",
        "--out-dir", "data/output/test_sample",
        "--overwrite",
    ]
    subprocess.run(cmd, cwd=str(ROOT), check=True)
    out = ROOT / "data/output/test_sample/firm_year_text_indicators.csv"
    with out.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1, rows
    row = rows[0]
    assert row["code"] == "000001"
    assert float(row["climate_keyword_count"]) > 0
    assert float(row["digital_total_count"]) > 0
    print("Smoke test passed:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
