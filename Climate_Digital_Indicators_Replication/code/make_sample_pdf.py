#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a small sample annual-report PDF for smoke tests.

This file is only for verifying that the pipeline runs.  It is not real company
data and should not be used in empirical analysis.
"""

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "sample" / "000001_SampleFirm_2022.pdf"
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf",
    "/usr/share/fonts/truetype/arphic/uming.ttc",
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    font_name = "Helvetica"
    for font in FONT_CANDIDATES:
        if Path(font).exists():
            try:
                pdfmetrics.registerFont(TTFont("SampleChinese", font))
                font_name = "SampleChinese"
                break
            except Exception:
                pass
    c = canvas.Canvas(str(OUT))
    c.setFont(font_name, 12)
    lines = [
        "样本公司2022年年度报告。",
        "报告期内，公司高度关注气候、天气、暴雨、洪水、干旱等自然灾害风险。",
        "公司加强供应链应急预案和气象预报监测，提升防洪防灾能力。",
        "公司持续推进人工智能、大数据、云计算、区块链、物联网和电子商务建设。",
        "公司开展智能营销、数字金融和移动支付系统升级。",
        "本段为测试否定词过滤：公司没有区块链投机业务，不开展数字货币炒作。",
        "This sample annual report is generated only for testing the replication code.",
    ]
    y = 780
    for line in lines:
        c.drawString(60, y, line)
        y -= 24
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
