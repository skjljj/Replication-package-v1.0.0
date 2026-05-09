# Smoke-Test Record

The package was tested on the synthetic sample annual-report PDF included in `data/sample/`.

Command:

```bash
python tests/test_sample_pipeline.py
```

Result:

```text
Converted/skipped 1/1 PDF files.
Wrote 1 firm-year climate-attention row.
Wrote 1 firm-year digital-transformation row.
Wrote 1 merged firm-year row.
Smoke test passed.
```

The main output is:

```text
data/output/test_sample/firm_year_text_indicators.csv
```

Sample result:

```text
code=000001
year=2022
climate_keyword_count>0
digital_total_count>0
```

Note: the execution environment used for the smoke test did not have `jieba` installed, so the climate-attention script used its deterministic substring fallback.  For closest replication of the published Chinese text-analysis workflow, install the dependencies in `requirements.txt`, especially `jieba==0.42.1`, and run the same command again.
