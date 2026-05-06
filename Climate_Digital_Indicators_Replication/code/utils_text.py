#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for annual-report text-based indicators.

The functions here are intentionally lightweight and deterministic.  They use
jieba when it is installed, because the climate-risk code in Wang (2025) and the
Annualreport_tools text-analysis scripts use jieba segmentation.  If jieba is
not installed, the code falls back to substring matching so that the workflow can
still be smoke-tested.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:  # optional, but recommended for exact replication of the referenced code
    import jieba  # type: ignore
    JIEBA_AVAILABLE = True
except Exception:  # pragma: no cover - depends on environment
    jieba = None  # type: ignore
    JIEBA_AVAILABLE = False

CHINESE_RE = re.compile(r"[\u4e00-\u9fff]+")
DEFAULT_NEGATIONS = ("没", "没有", "无", "不", "未", "否", "尚未")
DEFAULT_NON_FIRM_CONTEXT_TERMS = (
    "股东", "客户", "供应商", "高管", "董事", "监事", "简历", "简介", "履历"
)


@dataclass(frozen=True)
class ReportRecord:
    """Metadata for one annual report."""

    code: str
    company: str
    year: str
    path: Path


def read_keyword_csv(path: Path) -> List[Tuple[str, str]]:
    """Read a dictionary CSV with columns category, keyword."""
    rows: List[Tuple[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = (row.get("category") or "all").strip()
            keyword = (row.get("keyword") or "").strip()
            if keyword:
                rows.append((category, keyword))
    return rows


def read_stopwords(path: Optional[Path]) -> set[str]:
    """Read a stopword file, one item per line."""
    if path is None or not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def parse_report_filename(path: Path) -> Tuple[str, str, str]:
    """Parse metadata from common annual-report filenames.

    Supported examples:
        000001_PingAnBank_2022.pdf
        000001-平安银行-2022.txt
        000001_平安银行_2022_annual_report.pdf

    If no metadata can be parsed, returns code="UNKNOWN", company=stem,
    year="UNKNOWN".
    """
    stem = path.stem
    patterns = [
        r"^(?P<code>\d{6})[_\-](?P<company>.*?)[_\-](?P<year>20\d{2}|19\d{2})",
        r"^(?P<company>.*?)[_\-](?P<code>\d{6})[_\-](?P<year>20\d{2}|19\d{2})",
    ]
    for pat in patterns:
        match = re.search(pat, stem)
        if match:
            return match.group("code"), match.group("company"), match.group("year")
    year_match = re.search(r"(20\d{2}|19\d{2})", stem)
    return "UNKNOWN", stem, year_match.group(1) if year_match else "UNKNOWN"


def load_metadata_csv(path: Path, project_root: Path) -> List[ReportRecord]:
    """Read report metadata CSV.

    Expected columns are code, company, year, pdf_path or txt_path.  Relative
    paths are interpreted relative to the project root.
    """
    records: List[ReportRecord] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_path = row.get("pdf_path") or row.get("txt_path") or row.get("path")
            if not raw_path:
                continue
            p = Path(raw_path)
            if not p.is_absolute():
                p = project_root / p
            code = (row.get("code") or "UNKNOWN").strip()
            company = (row.get("company") or p.stem).strip()
            year = str(row.get("year") or parse_report_filename(p)[2]).strip()
            records.append(ReportRecord(code=code, company=company, year=year, path=p))
    return records


def discover_reports(input_dir: Path, suffixes: Sequence[str]) -> List[ReportRecord]:
    """Discover reports recursively under input_dir."""
    suffix_set = {s.lower() for s in suffixes}
    records: List[ReportRecord] = []
    for p in sorted(input_dir.rglob("*")):
        if p.is_file() and p.suffix.lower() in suffix_set:
            code, company, year = parse_report_filename(p)
            records.append(ReportRecord(code=code, company=company, year=year, path=p))
    return records


def normalize_text(text: str) -> str:
    """Normalize whitespace and full-width spaces."""
    return re.sub(r"\s+", " ", text.replace("\u3000", " ")).strip()


def chinese_character_count(text: str) -> int:
    """Count Chinese characters, used as a fallback denominator."""
    return len("".join(CHINESE_RE.findall(text)))


def tokenize_chinese(text: str, keywords: Optional[Iterable[str]] = None, stopwords: Optional[set[str]] = None) -> Tuple[List[str], str]:
    """Tokenize Chinese text.

    Returns a pair: (tokens, tokenizer_name).  When jieba is available, keywords
    are added to its dictionary so multi-character terms are preserved.  Tokens
    of length 1 and stopwords are removed, following the spirit of the Wang
    climate-risk replication script.  Without jieba, the function returns a
    character-level fallback so that the pipeline can still run.
    """
    stopwords = stopwords or set()
    if JIEBA_AVAILABLE:
        if keywords:
            for kw in keywords:
                try:
                    jieba.add_word(kw)  # type: ignore[union-attr]
                except Exception:
                    pass
        raw_tokens = list(jieba.cut(text))  # type: ignore[union-attr]
        tokens = [w.strip() for w in raw_tokens if len(w.strip()) > 1 and w.strip() not in stopwords]
        return tokens, "jieba"
    # Fallback: count continuous Chinese runs as coarse tokens plus English words.
    # This is not a substitute for exact replication, but enables smoke tests.
    chinese_runs = CHINESE_RE.findall(text)
    english_words = re.findall(r"[A-Za-z][A-Za-z0-9_+\-.]*", text)
    tokens = [x for x in chinese_runs + english_words if x not in stopwords]
    return tokens, "fallback_regex"


def count_terms_by_tokenization(text: str, keywords: Sequence[str], stopwords: Optional[set[str]] = None) -> Tuple[Dict[str, int], int, str]:
    """Count keyword frequency using jieba tokenization when available."""
    tokens, tokenizer_name = tokenize_chinese(text, keywords=keywords, stopwords=stopwords)
    counter = Counter(tokens)
    counts = {kw: int(counter.get(kw, 0)) for kw in keywords}
    total = int(sum(counter.values()))
    return counts, total, tokenizer_name


def count_terms_by_substring(
    text: str,
    keywords: Sequence[str],
    skip_negated: bool = False,
    skip_non_firm_context: bool = False,
    negations: Sequence[str] = DEFAULT_NEGATIONS,
    non_firm_context_terms: Sequence[str] = DEFAULT_NON_FIRM_CONTEXT_TERMS,
    context_window: int = 12,
) -> Dict[str, int]:
    """Count literal keyword occurrences with optional context filters.

    Chinese terms are matched literally.  ASCII terms are matched case-insensitively.
    The filter for negated statements follows Wu et al. (2021)'s instruction to
    exclude terms preceded by words such as 没, 无, 不.  The optional non-firm
    context filter removes matches appearing near words such as 股东, 客户,
    供应商, 高管简介, etc.; it is deterministic but inevitably approximate.
    """
    counts: Dict[str, int] = {}
    for kw in keywords:
        if not kw:
            counts[kw] = 0
            continue
        flags = re.IGNORECASE if re.search(r"[A-Za-z]", kw) else 0
        pattern = re.escape(kw)
        n = 0
        for m in re.finditer(pattern, text, flags=flags):
            start, end = m.start(), m.end()
            prev = text[max(0, start - context_window):start]
            context = text[max(0, start - context_window):min(len(text), end + context_window)]
            if skip_negated and any(neg in prev for neg in negations):
                continue
            if skip_non_firm_context and any(term in context for term in non_firm_context_terms):
                continue
            n += 1
        counts[kw] = n
    return counts


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    """Write rows to CSV, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
