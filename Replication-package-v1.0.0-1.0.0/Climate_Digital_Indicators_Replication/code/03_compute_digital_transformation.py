#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compute firm-level digital-transformation indicators from annual reports.

The dictionary is: artificial
intelligence, blockchain, cloud computing, big data, and digital-application
terms.  The main indicator is

    digital_transformation_log1p = log(1 + total_digital_keyword_count)

The script also reports category-level counts and a word-frequency share.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from utils_text import (  # noqa:E402
    ReportRecord,
    chinese_character_count,
    count_terms_by_substring,
    discover_reports,
    load_metadata_csv,
    normalize_text,
    parse_report_filename,
    read_keyword_csv,
    write_csv,
)


def build_records(args: argparse.Namespace, project_root: Path) -> List[ReportRecord]:
    if args.metadata:
        return load_metadata_csv(Path(args.metadata), project_root=project_root)
    return discover_reports(Path(args.txt_dir), suffixes=[".txt"])


def compute_for_record(rec: ReportRecord, dictionary_rows: List[tuple[str, str]], skip_negated: bool, skip_non_firm_context: bool) -> tuple[dict, List[dict]]:
    text = normalize_text(rec.path.read_text(encoding="utf-8", errors="ignore"))
    code, company, year = rec.code, rec.company, rec.year
    if code == "UNKNOWN" or year == "UNKNOWN":
        parsed_code, parsed_company, parsed_year = parse_report_filename(rec.path)
        code = code if code != "UNKNOWN" else parsed_code
        company = company if company != rec.path.stem else parsed_company
        year = year if year != "UNKNOWN" else parsed_year

    keywords = [kw for _, kw in dictionary_rows]
    raw_counts = count_terms_by_substring(
        text,
        keywords,
        skip_negated=skip_negated,
        skip_non_firm_context=skip_non_firm_context,
    )
    category_counts: Dict[str, int] = defaultdict(int)
    long_rows: List[dict] = []
    for category, keyword in dictionary_rows:
        count = int(raw_counts.get(keyword, 0))
        category_counts[category] += count
        long_rows.append({
            "code": code,
            "company": company,
            "year": year,
            "category": category,
            "keyword": keyword,
            "count": count,
        })

    total_count = int(sum(category_counts.values()))
    total_words = chinese_character_count(text)
    share = total_count / total_words if total_words else math.nan
    summary = {
        "code": code,
        "company": company,
        "year": year,
        "file_name": rec.path.name,
        "total_word_count_fallback": total_words,
        "digital_total_count": total_count,
        "digital_transformation_log1p": math.log1p(total_count),
        "digital_transformation_share": share,
        "digital_transformation_share_x100": share * 100 if total_words else math.nan,
        "ai_count": category_counts.get("artificial_intelligence", 0),
        "blockchain_count": category_counts.get("blockchain", 0),
        "cloud_count": category_counts.get("cloud_computing", 0),
        "big_data_count": category_counts.get("big_data", 0),
        "digital_application_count": category_counts.get("digital_application", 0),
    }
    return summary, long_rows


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compute digital-transformation indicator from TXT annual reports.")
    parser.add_argument("--txt-dir", default="data/intermediate/txt", help="Directory containing TXT annual reports.")
    parser.add_argument("--metadata", default=None, help="Optional metadata CSV with code, company, year, txt_path.")
    parser.add_argument("--dictionary", default="data/dictionaries/digital_transformation_keywords.csv", help="Digital keyword dictionary CSV.")
    parser.add_argument("--skip-negated", action="store_true", default=True, help="Exclude keywords preceded by negation terms such as 没, 无, 不. Default: on.")
    parser.add_argument("--include-negated", action="store_false", dest="skip_negated", help="Do not exclude negated occurrences.")
    parser.add_argument("--skip-non-firm-context", action="store_true", default=True, help="Exclude approximate non-firm contexts such as shareholder/customer/supplier/executive-intro windows. Default: on.")
    parser.add_argument("--include-non-firm-context", action="store_false", dest="skip_non_firm_context", help="Do not exclude non-firm contexts.")
    parser.add_argument("--output", default="data/output/digital_transformation.csv", help="Summary output CSV.")
    parser.add_argument("--long-output", default="data/output/digital_transformation_keyword_counts_long.csv", help="Keyword-level output CSV.")
    args = parser.parse_args(argv)

    project_root = THIS_DIR.parent
    records = build_records(args, project_root=project_root)
    dictionary_rows = read_keyword_csv(Path(args.dictionary))

    summary_rows: List[dict] = []
    long_rows: List[dict] = []
    for rec in records:
        if not rec.path.exists():
            continue
        summary, long = compute_for_record(rec, dictionary_rows, args.skip_negated, args.skip_non_firm_context)
        summary_rows.append(summary)
        long_rows.extend(long)

    summary_fields = [
        "code", "company", "year", "file_name", "total_word_count_fallback",
        "digital_total_count", "digital_transformation_log1p", "digital_transformation_share",
        "digital_transformation_share_x100", "ai_count", "blockchain_count", "cloud_count",
        "big_data_count", "digital_application_count",
    ]
    long_fields = ["code", "company", "year", "category", "keyword", "count"]
    write_csv(Path(args.output), summary_rows, summary_fields)
    write_csv(Path(args.long_output), long_rows, long_fields)
    print(f"Wrote {len(summary_rows)} firm-year digital-transformation rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
