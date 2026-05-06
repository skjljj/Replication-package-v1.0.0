# Replication-package-v1.0.0
Replication code for climate-risk attention and digital-transformation indicators
# Climate and Digital Indicator Replication Package

This package constructs two annual-report text indicators used in the paper
`Climate Risk Attention Divergence and Supply Chain Instability`:

1. **Climate-risk attention**: annual-report climate/disaster keyword frequency divided by total annual-report word count and multiplied by 100.  The workflow follows the replication code logic in Wang (2025): annual-report PDFs -> TXT -> Chinese word segmentation -> climate keyword counts -> frequency ratio.
2. **Digital transformation**: annual-report frequency of digital-transformation keywords, aggregated across five categories in Wu et al. (2021): artificial intelligence, blockchain, cloud computing, big data, and digital-application terms.  The main indicator is `log(1 + total digital keyword count)`.

The package is organized in an AEA/AER-style replication format: a master script, modular code, dictionaries, sample data, output folders, logs, source-code provenance, and a tested sample workflow.

## 1. Data Availability Statement

The full empirical dataset is not included in this package.  The code is designed to run on Chinese listed firms' annual reports in PDF format.  Annual reports can be obtained from public company disclosure websites such as CNINFO, the Shanghai Stock Exchange, or the Shenzhen Stock Exchange.  Users should confirm that they have legitimate access to the annual reports and comply with the websites' usage rules.

The sample PDF in `data/sample/` is synthetic and was generated only to test the code.  It is not real firm data and should not be used in empirical analysis.

If the package is uploaded to a public repository, do not upload restricted or non-redistributable raw data.  If raw data cannot be redistributed, keep the code public and document data provenance, access conditions, and the steps needed to recreate the raw data.

## 2. Package Contents

```text
Climate_Digital_Indicators_Replication/
  README.md                         Main README
  README.pdf                        PDF README for journal-style deposits
  CITATION.md                       Citation information
  LICENSE                           License statement
  requirements.txt                  Python package requirements
  run_all.py                        Master script
  code/
    01_convert_pdf_to_txt.py         Convert annual-report PDFs to TXT
    02_compute_climate_attention.py  Compute climate-risk attention
    03_compute_digital_transformation.py Compute digital-transformation counts
    04_merge_indicators.py           Merge firm-year text indicators
    05_build_dyadic_variables.py     Build customer-supplier divergence variables
    make_sample_pdf.py               Regenerate the synthetic sample PDF
    utils_text.py                    Shared text-processing utilities
  data/
    dictionaries/                    Climate and digital keyword dictionaries
    raw/annual_reports_pdf/          Put raw annual-report PDFs here
    intermediate/txt/                Converted TXT files
    sample/                          Synthetic sample PDF and metadata CSV
    output/                          Output CSV files
  legacy/
    climate_attention_original/      Original climate-risk code copied from the supplied Wang-style replication zip
    digital_transformation_original/ Original Annualreport_tools scripts
  logs/                              Logs
  tests/                             Test notes
```

## 3. Software and Hardware

Recommended environment:

- Python 3.10 or later
- `pdfminer.six`, `PyMuPDF`, `pypdf`
- `jieba` is recommended for closest replication of Wang (2025) and Annualreport_tools segmentation.
- `reportlab` is needed only if you regenerate the synthetic sample PDF.

Install dependencies:

```bash
pip install -r requirements.txt
```

Expected running time:

- Synthetic sample: less than 1 minute on a standard laptop.
- Full annual-report corpus: depends on the number and size of PDFs.  PDF-to-TXT conversion is usually the slowest step.

## 4. Reproducing the Sample Test

From the package root, run:

```bash
python run_all.py \
  --pdf-dir data/sample \
  --metadata data/sample/report_metadata.csv \
  --txt-dir data/intermediate/sample_txt \
  --out-dir data/output/sample \
  --overwrite
```

Main sample output:

```text
data/output/sample/firm_year_text_indicators.csv
```

The sample should produce one firm-year observation for `000001, SampleFirm, 2022`.

## 5. Full-Corpus Workflow

### Step 1. Prepare annual-report PDFs

Put PDF annual reports into:

```text
data/raw/annual_reports_pdf/
```

Recommended filename format:

```text
000001_CompanyName_2022.pdf
```

Alternatively, provide a metadata CSV with the following columns:

```text
code,company,year,pdf_path
```

### Step 2. Convert PDFs to TXT

```bash
python code/01_convert_pdf_to_txt.py \
  --pdf-dir data/raw/annual_reports_pdf \
  --txt-dir data/intermediate/txt \
  --log logs/01_pdf_to_txt_log.csv \
  --overwrite
```

This step tries `pdfminer.six`, then `PyMuPDF`, then `pypdf`.

### Step 3. Compute climate-risk attention

```bash
python code/02_compute_climate_attention.py \
  --txt-dir data/intermediate/txt \
  --dictionary data/dictionaries/climate_attention_keywords.csv \
  --stopwords data/dictionaries/stopwords_zh.txt \
  --method auto \
  --output data/output/climate_attention.csv \
  --long-output data/output/climate_attention_keyword_counts_long.csv
```

Variable construction:

```text
climate_attention        = climate_keyword_count / total_word_count
climate_attention_x100   = climate_attention * 100
```

`--method auto` uses `jieba` when installed.  If `jieba` is unavailable, the script falls back to deterministic substring counts so the workflow remains runnable.  For closest replication of Wang (2025), install `jieba` and keep `--method auto` or use `--method jieba`.

### Step 4. Compute digital-transformation indicator

```bash
python code/03_compute_digital_transformation.py \
  --txt-dir data/intermediate/txt \
  --dictionary data/dictionaries/digital_transformation_keywords.csv \
  --output data/output/digital_transformation.csv \
  --long-output data/output/digital_transformation_keyword_counts_long.csv
```

Variable construction:

```text
digital_total_count              = total count of digital-transformation keywords
digital_transformation_log1p     = log(1 + digital_total_count)
digital_transformation_share_x100 = digital_total_count / Chinese-character count * 100
```

The default digital script excludes keyword occurrences preceded by negation terms such as `没`, `无`, `不`, and uses a deterministic context-window filter to exclude approximate non-firm contexts such as shareholder, customer, supplier, and executive-introduction windows.  To turn these filters off, add:

```bash
--include-negated --include-non-firm-context
```

### Step 5. Merge firm-year indicators

```bash
python code/04_merge_indicators.py \
  --climate data/output/climate_attention.csv \
  --digital data/output/digital_transformation.csv \
  --output data/output/firm_year_text_indicators.csv
```

### Step 6. Build customer-supplier dyadic variables

If you have a customer-supplier relationship CSV with columns:

```text
customer_code,supplier_code,year
```

run:

```bash
python code/05_build_dyadic_variables.py \
  --pairs data/raw/customer_supplier_pairs.csv \
  --indicators data/output/firm_year_text_indicators.csv \
  --output data/output/dyadic_text_indicators.csv
```

The script creates:

```text
customer_climate_attention_x100
supplier_climate_attention_x100
climate_attention_divergence_x100 = customer - supplier
positive_climate_attention_divergence_x100
customer_digital_transformation_log1p
supplier_digital_transformation_log1p
```

## 6. Output Mapping

| Output file | Produced by | Purpose |
| --- | --- | --- |
| `climate_attention.csv` | `02_compute_climate_attention.py` | Firm-year climate-risk attention |
| `climate_attention_keyword_counts_long.csv` | `02_compute_climate_attention.py` | Keyword-level climate counts |
| `digital_transformation.csv` | `03_compute_digital_transformation.py` | Firm-year digital-transformation indicator and category counts |
| `digital_transformation_keyword_counts_long.csv` | `03_compute_digital_transformation.py` | Keyword-level digital counts |
| `firm_year_text_indicators.csv` | `04_merge_indicators.py` | Merged firm-year climate and digital indicators |
| `dyadic_text_indicators.csv` | `05_build_dyadic_variables.py` | Customer-supplier dyadic variables and climate-attention divergence |

## 7. Provenance of the Code

- `legacy/climate_attention_original/PhyClimt_original_Wang2025.py` is the original climate physical-risk text code found in the supplied `附件2：复现材料.zip`.
- `legacy/digital_transformation_original/Annualreport_tools-main/` is the original `Annualreport_tools-main.zip` code used for annual-report crawling, PDF-to-TXT conversion, and keyword analysis.
- The `code/` directory contains a cleaned, modular, command-line version that integrates both indicator workflows and can be run from a single master script.

## 8. Notes for Replicators

1. Do not manually edit intermediate TXT files unless the edit is fully documented.
2. Keep raw PDFs, intermediate TXT files, and output CSVs in separate folders.
3. If annual reports are downloaded by a crawler, document the source URL, access date, rate limits, and any exclusions.
4. If a PDF has scanned pages and cannot be extracted by `pdfminer.six`/`PyMuPDF`/`pypdf`, use OCR separately and document the OCR software and settings.
5. For the exact paper regressions, merge the firm-year indicators with the paper's supply-chain relationship data and other financial variables.
