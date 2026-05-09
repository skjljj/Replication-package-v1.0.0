#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compute firm-level climate-risk attention from TXT annual reports.


    climate_attention_x100 = climate_keyword_count / total_word_count * 100

where the numerator is the frequency of climate/disaster-related terms and the
recommended denominator is the jieba-segmented annual-report word count.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import List, Optional

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from utils_text import (  # noqa:E402
    ReportRecord,
    chinese_character_count,
    count_terms_by_substring,
    count_terms_by_tokenization,
    discover_reports,
    load_metadata_csv,
    normalize_text,
    parse_report_filename,
    read_keyword_csv,
    read_stopwords,
    write_csv,
)


def build_records(args: argparse.Namespace, project_root: Path) -> List[ReportRecord]:
    if args.metadata:
        return load_metadata_csv(Path(args.metadata), project_root=project_root)
    return discover_reports(Path(args.txt_dir), suffixes=[".txt"])


def compute_for_record(rec: ReportRecord, keywords: List[str], stopwords: set[str], method: str) -> tuple[dict, List[dict]]:
    text = normalize_text(rec.path.read_text(encoding="utf-8", errors="ignore"))
    code, company, year = rec.code, rec.company, rec.year
    if code == "UNKNOWN" or year == "UNKNOWN":
        parsed_code, parsed_company, parsed_year = parse_report_filename(rec.path)
        code = code if code != "UNKNOWN" else parsed_code
        company = company if company != rec.path.stem else parsed_company
        year = year if year != "UNKNOWN" else parsed_year

    tokenizer = ""
    if method in {"auto", "jieba"}:
        try:
            term_counts, total_words, tokenizer = count_terms_by_tokenization(text, keywords, stopwords=stopwords)
            if tokenizer != "jieba":
                # Exact Wang-style replication requires jieba.  When it is not
                # installed, use deterministic substring counts so that the
                # pipeline remains runnable and transparent.
                term_counts = count_terms_by_substring(text, keywords)
                total_words = chinese_character_count(text)
                tokenizer = "substring_fallback"
                if method == "jieba":
                    print("WARNING: jieba is not installed; falling back to regex/substrings.")
        except Exception:
            term_counts = count_terms_by_substring(text, keywords)
            total_words = chinese_character_count(text)
            tokenizer = "substring_fallback"
    else:
        term_counts = count_terms_by_substring(text, keywords)
        total_words = chinese_character_count(text)
        tokenizer = "substring"

    climate_count = int(sum(term_counts.values()))
    attention = climate_count / total_words if total_words else math.nan
    summary = {
        "code": code,
        "company": company,
        "year": year,
        "file_name": rec.path.name,
        "tokenizer": tokenizer,
        "total_word_count": total_words,
        "climate_keyword_count": climate_count,
        "climate_attention": attention,
        "climate_attention_x100": attention * 100 if total_words else math.nan,
    }
    long_rows = []
    for kw, count in term_counts.items():
        long_rows.append({
            "code": code,
            "company": company,
            "year": year,
            "keyword": kw,
            "count": count,
            "total_word_count": total_words,
        })
    return summary, long_rows


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compute climate-risk attention indicator from TXT annual reports.")
    parser.add_argument("--txt-dir", default="data/intermediate/txt", help="Directory containing TXT annual reports.")
    parser.add_argument("--metadata", default=None, help="Optional metadata CSV with code, company, year, txt_path.")
    parser.add_argument("--dictionary", default="data/dictionaries/climate_attention_keywords.csv", help="Climate keyword dictionary CSV.")
    parser.add_argument("--stopwords", default="data/dictionaries/stopwords_zh.txt", help="Stopword file.")
    parser.add_argument("--method", choices=["auto", "jieba", "substring"], default="auto", help="Counting method. auto uses jieba if available.")
    parser.add_argument("--output", default="data/output/climate_attention.csv", help="Summary output CSV.")
    parser.add_argument("--long-output", default="data/output/climate_attention_keyword_counts_long.csv", help="Keyword-level output CSV.")
    args = parser.parse_args(argv)

    project_root = THIS_DIR.parent
    records = build_records(args, project_root=project_root)
    keywords = [kw for _, kw in read_keyword_csv(Path(args.dictionary))]
    stopwords = read_stopwords(Path(args.stopwords))

    summary_rows: List[dict] = []
    long_rows: List[dict] = []
    for rec in records:
        if not rec.path.exists():
            continue
        summary, long = compute_for_record(rec, keywords, stopwords, method=args.method)
        summary_rows.append(summary)
        long_rows.extend(long)

    summary_fields = [
        "code", "company", "year", "file_name", "tokenizer", "total_word_count",
        "climate_keyword_count", "climate_attention", "climate_attention_x100",
    ]
    long_fields = ["code", "company", "year", "keyword", "count", "total_word_count"]
    write_csv(Path(args.output), summary_rows, summary_fields)
    write_csv(Path(args.long_output), long_rows, long_fields)
    print(f"Wrote {len(summary_rows)} firm-year climate-attention rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
