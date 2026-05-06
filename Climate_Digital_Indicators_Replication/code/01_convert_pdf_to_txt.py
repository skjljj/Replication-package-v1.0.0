#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert annual-report PDFs to TXT files.

This implements the PDF-to-TXT step described in the climate-risk replication
materials and in Annualreport_tools.  It first tries pdfminer.six, then PyMuPDF,
then pypdf if installed.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import List, Optional

# Allow running from the project root or from the code directory.
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from utils_text import ReportRecord, discover_reports, load_metadata_csv, parse_report_filename, write_csv  # noqa:E402


def extract_text_pdfminer(pdf_path: Path) -> str:
    from pdfminer.high_level import extract_text  # type: ignore
    return extract_text(str(pdf_path)) or ""


def extract_text_pymupdf(pdf_path: Path) -> str:
    import fitz  # type: ignore
    parts: List[str] = []
    with fitz.open(str(pdf_path)) as doc:
        for page in doc:
            parts.append(page.get_text("text"))
    return "\n".join(parts)


def extract_text_pypdf(pdf_path: Path) -> str:
    from pypdf import PdfReader  # type: ignore
    reader = PdfReader(str(pdf_path))
    parts: List[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def extract_pdf_text(pdf_path: Path) -> tuple[str, str]:
    """Extract text from a PDF and return (text, engine_name)."""
    errors = []
    for name, func in [
        ("pdfminer.six", extract_text_pdfminer),
        ("PyMuPDF", extract_text_pymupdf),
        ("pypdf", extract_text_pypdf),
    ]:
        try:
            text = func(pdf_path)
            if text.strip():
                return text, name
            errors.append(f"{name}: empty text")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
    raise RuntimeError("; ".join(errors))


def build_records(args: argparse.Namespace, project_root: Path) -> List[ReportRecord]:
    if args.metadata:
        return load_metadata_csv(Path(args.metadata), project_root=project_root)
    return discover_reports(Path(args.pdf_dir), suffixes=[".pdf"])


def convert_reports(records: List[ReportRecord], txt_dir: Path, overwrite: bool = False) -> List[dict]:
    txt_dir.mkdir(parents=True, exist_ok=True)
    log_rows: List[dict] = []
    for rec in records:
        if not rec.path.exists():
            log_rows.append({
                "code": rec.code, "company": rec.company, "year": rec.year,
                "pdf_path": str(rec.path), "txt_path": "", "engine": "", "status": "missing_pdf",
            })
            continue
        code, company, year = rec.code, rec.company, rec.year
        if code == "UNKNOWN" or year == "UNKNOWN":
            parsed_code, parsed_company, parsed_year = parse_report_filename(rec.path)
            code = code if code != "UNKNOWN" else parsed_code
            company = company if company != rec.path.stem else parsed_company
            year = year if year != "UNKNOWN" else parsed_year
        safe_company = company.replace("/", "_").replace("\\", "_").replace(" ", "")
        txt_path = txt_dir / f"{code}_{safe_company}_{year}.txt"
        if txt_path.exists() and not overwrite:
            log_rows.append({
                "code": code, "company": company, "year": year,
                "pdf_path": str(rec.path), "txt_path": str(txt_path), "engine": "existing", "status": "skipped_existing",
            })
            continue
        try:
            text, engine = extract_pdf_text(rec.path)
            txt_path.write_text(text, encoding="utf-8")
            status = "ok"
        except Exception as exc:  # noqa: BLE001
            engine = ""
            status = f"error: {exc}"
        log_rows.append({
            "code": code, "company": company, "year": year,
            "pdf_path": str(rec.path), "txt_path": str(txt_path) if txt_path.exists() else "",
            "engine": engine, "status": status,
        })
    return log_rows


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Convert annual-report PDFs to TXT.")
    parser.add_argument("--pdf-dir", default="data/raw/annual_reports_pdf", help="Directory containing PDF annual reports.")
    parser.add_argument("--metadata", default=None, help="Optional metadata CSV with code, company, year, pdf_path.")
    parser.add_argument("--txt-dir", default="data/intermediate/txt", help="Output directory for TXT files.")
    parser.add_argument("--log", default="logs/01_pdf_to_txt_log.csv", help="Conversion log CSV.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing TXT files.")
    args = parser.parse_args(argv)

    project_root = THIS_DIR.parent
    records = build_records(args, project_root=project_root)
    rows = convert_reports(records, Path(args.txt_dir), overwrite=args.overwrite)
    write_csv(Path(args.log), rows, ["code", "company", "year", "pdf_path", "txt_path", "engine", "status"])
    ok = sum(1 for r in rows if r["status"] in {"ok", "skipped_existing"})
    print(f"Converted/skipped {ok}/{len(rows)} PDF files. Log: {args.log}")
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
