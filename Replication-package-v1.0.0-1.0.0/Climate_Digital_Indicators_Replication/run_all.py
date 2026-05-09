#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Master script for the annual-report text indicator pipeline.

Typical sample run:
    python run_all.py --pdf-dir data/sample --metadata data/sample/report_metadata.csv --out-dir data/output/sample --overwrite

Typical full-corpus run after putting PDF annual reports in data/raw/annual_reports_pdf:
    python run_all.py --pdf-dir data/raw/annual_reports_pdf --out-dir data/output/full --overwrite
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent
CODE = ROOT / "code"


def run_step(cmd: List[str]) -> None:
    print("\n$ " + " ".join(cmd), flush=True)
    completed = subprocess.run(cmd, cwd=str(ROOT), text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the full text-indicator pipeline.")
    parser.add_argument("--pdf-dir", default="data/raw/annual_reports_pdf")
    parser.add_argument("--metadata", default=None, help="Optional metadata CSV with code, company, year, pdf_path.")
    parser.add_argument("--txt-dir", default="data/intermediate/txt")
    parser.add_argument("--out-dir", default="data/output")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--climate-method", choices=["auto", "jieba", "substring"], default="auto")
    args = parser.parse_args(argv)

    txt_dir = args.txt_dir
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    convert_cmd = [
        sys.executable, str(CODE / "01_convert_pdf_to_txt.py"),
        "--pdf-dir", args.pdf_dir,
        "--txt-dir", txt_dir,
        "--log", str(out_dir / "01_pdf_to_txt_log.csv"),
    ]
    if args.metadata:
        convert_cmd.extend(["--metadata", args.metadata])
    if args.overwrite:
        convert_cmd.append("--overwrite")
    run_step(convert_cmd)

    climate_cmd = [
        sys.executable, str(CODE / "02_compute_climate_attention.py"),
        "--txt-dir", txt_dir,
        "--method", args.climate_method,
        "--output", str(out_dir / "climate_attention.csv"),
        "--long-output", str(out_dir / "climate_attention_keyword_counts_long.csv"),
    ]
    run_step(climate_cmd)

    digital_cmd = [
        sys.executable, str(CODE / "03_compute_digital_transformation.py"),
        "--txt-dir", txt_dir,
        "--output", str(out_dir / "digital_transformation.csv"),
        "--long-output", str(out_dir / "digital_transformation_keyword_counts_long.csv"),
    ]
    run_step(digital_cmd)

    merge_cmd = [
        sys.executable, str(CODE / "04_merge_indicators.py"),
        "--climate", str(out_dir / "climate_attention.csv"),
        "--digital", str(out_dir / "digital_transformation.csv"),
        "--output", str(out_dir / "firm_year_text_indicators.csv"),
    ]
    run_step(merge_cmd)

    print("\nPipeline completed. Main output:", out_dir / "firm_year_text_indicators.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
