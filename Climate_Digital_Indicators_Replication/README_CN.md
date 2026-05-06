# 气候关注度与数字化转型指标复现代码包

本代码包用于复现论文中两个基于年报文本的指标：

1. **气候风险关注度**：将年报 PDF 转换为 TXT 后，统计气候/灾害相关关键词词频，并除以年报总词数再乘以 100。流程参考王文蔚（2025）复现材料中的 Python 代码：PDF 年报 -> TXT 文本 -> 中文分词 -> 气候关键词词频 -> 词频占比。
2. **企业数字化转型指标**：按照吴非等（2021）的关键词体系，统计人工智能、区块链、云计算、大数据和数字技术应用五类词频，并构造 `log(1 + 数字化关键词总词频)`。

代码包采用接近 AEA/AER 复现代码的组织方式：根目录 README、master script、模块化代码、词典、样本数据、输出文件夹、日志、原始代码来源说明。

## 一、快速测试

在代码包根目录运行：

```bash
python run_all.py \
  --pdf-dir data/sample \
  --metadata data/sample/report_metadata.csv \
  --txt-dir data/intermediate/sample_txt \
  --out-dir data/output/sample \
  --overwrite
```

输出文件为：

```text
data/output/sample/firm_year_text_indicators.csv
```

## 二、完整复现流程

### 第 1 步：准备 PDF 年报

将年报 PDF 放在：

```text
data/raw/annual_reports_pdf/
```

建议文件名：

```text
000001_公司名称_2022.pdf
```

也可以提供 metadata CSV：

```text
code,company,year,pdf_path
```

### 第 2 步：PDF 转 TXT

```bash
python code/01_convert_pdf_to_txt.py \
  --pdf-dir data/raw/annual_reports_pdf \
  --txt-dir data/intermediate/txt \
  --log logs/01_pdf_to_txt_log.csv \
  --overwrite
```

### 第 3 步：计算气候风险关注度

```bash
python code/02_compute_climate_attention.py \
  --txt-dir data/intermediate/txt \
  --dictionary data/dictionaries/climate_attention_keywords.csv \
  --stopwords data/dictionaries/stopwords_zh.txt \
  --method auto \
  --output data/output/climate_attention.csv \
  --long-output data/output/climate_attention_keyword_counts_long.csv
```

变量定义：

```text
climate_attention        = climate_keyword_count / total_word_count
climate_attention_x100   = climate_attention * 100
```

`--method auto` 会在安装 jieba 时自动使用 jieba 分词。为了尽量贴近王文蔚（2025）原始代码，建议安装 `jieba==0.42.1`。

### 第 4 步：计算数字化转型指标

```bash
python code/03_compute_digital_transformation.py \
  --txt-dir data/intermediate/txt \
  --dictionary data/dictionaries/digital_transformation_keywords.csv \
  --output data/output/digital_transformation.csv \
  --long-output data/output/digital_transformation_keyword_counts_long.csv
```

变量定义：

```text
digital_total_count          = 数字化转型关键词总词频
digital_transformation_log1p = log(1 + digital_total_count)
```

脚本默认剔除关键词前存在“没”“无”“不”等否定词语的情况，并用固定窗口近似剔除股东、客户、供应商、高管简介等非本公司语境。若不想剔除，可加：

```bash
--include-negated --include-non-firm-context
```

### 第 5 步：合并企业-年份层面的指标

```bash
python code/04_merge_indicators.py \
  --climate data/output/climate_attention.csv \
  --digital data/output/digital_transformation.csv \
  --output data/output/firm_year_text_indicators.csv
```

### 第 6 步：构造客户-供应商关系对变量

如果有关系对数据：

```text
customer_code,supplier_code,year
```

运行：

```bash
python code/05_build_dyadic_variables.py \
  --pairs data/raw/customer_supplier_pairs.csv \
  --indicators data/output/firm_year_text_indicators.csv \
  --output data/output/dyadic_text_indicators.csv
```

生成变量包括：

```text
customer_climate_attention_x100
supplier_climate_attention_x100
climate_attention_divergence_x100 = customer - supplier
positive_climate_attention_divergence_x100
customer_digital_transformation_log1p
supplier_digital_transformation_log1p
```

## 三、原始代码来源

- `legacy/climate_attention_original/`：从“附件2：复现材料.zip”中提取的王文蔚（2025）相关原始代码。
- `legacy/digital_transformation_original/Annualreport_tools-main/`：从“Annualreport_tools-main.zip”中提取的年报爬取、PDF 转 TXT 和词频分析工具。
- `code/`：本次整理后的可命令行运行版本，方便公开代码链接和审稿人复现。
