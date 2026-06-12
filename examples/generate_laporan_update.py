#!/usr/bin/env python3
"""Generate laporan_update.pdf dari laporan_update.md.

Parser markdown sederhana yang mendukung: judul (#), subtitle (**Periode:**),
heading (## / ###), paragraf, bullet (- ), gambar ![caption](path),
garis pemisah (---), dan footer italic (*...*).
"""

import os
import re
import html
import urllib.parse

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, HRFlowable,
)
from PIL import Image as PILImage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE_DIR, "laporan_update.md")
OUTPUT = os.path.join(BASE_DIR, "laporan_update_juni_2026.pdf")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm
CONTENT_W = PAGE_W - 2 * MARGIN

styles = getSampleStyleSheet()

title_style = ParagraphStyle("Title", parent=styles["Normal"], fontSize=16,
                             fontName="Helvetica-Bold",
                             textColor=colors.HexColor("#1a1a2e"), spaceAfter=4)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10,
                                fontName="Helvetica",
                                textColor=colors.HexColor("#555555"), spaceAfter=12)
h2_style = ParagraphStyle("H2", parent=styles["Normal"], fontSize=13,
                          fontName="Helvetica-Bold",
                          textColor=colors.HexColor("#1a1a2e"),
                          spaceBefore=18, spaceAfter=8)
section_style = ParagraphStyle("Section", parent=styles["Normal"], fontSize=12,
                               fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#1a1a2e"),
                               spaceBefore=14, spaceAfter=6)
body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10,
                            fontName="Helvetica",
                            textColor=colors.HexColor("#333333"),
                            leading=16, spaceAfter=8)
bullet_style = ParagraphStyle("Bullet", parent=body_style, leftIndent=14,
                              bulletIndent=2, spaceAfter=4)
caption_style = ParagraphStyle("Caption", parent=styles["Normal"], fontSize=8,
                               fontName="Helvetica-Oblique",
                               textColor=colors.HexColor("#777777"),
                               alignment=1, spaceAfter=10)
footer_style = ParagraphStyle("Footer", parent=caption_style, alignment=0)


def inline(text):
    """Konversi markup inline markdown -> markup reportlab."""
    text = text.replace("→", "->")  # panah → tidak didukung Helvetica
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    return text


def add_image(path, caption, max_height=12 * cm):
    if not os.path.isfile(path):
        return [Paragraph(f"[Gambar tidak ditemukan: {os.path.basename(path)}]",
                          caption_style)]
    with PILImage.open(path) as img:
        w, h = img.size
    ratio = w / h
    w, h = CONTENT_W, CONTENT_W / ratio
    if h > max_height:
        h = max_height
        w = h * ratio
    out = [RLImage(path, width=w, height=h)]
    if caption:
        out.append(Paragraph(inline(caption), caption_style))
    return out


def build_story():
    with open(MD_PATH, encoding="utf-8") as f:
        lines = f.read().splitlines()

    story = [Spacer(1, 0.5 * cm)]
    para = []

    def flush_para():
        if para:
            story.append(Paragraph(inline(" ".join(para)), body_style))
            para.clear()

    img_re = re.compile(r"!\[(.*?)\]\((.*?)\)")

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("<!--"):
            continue
        if not stripped:
            flush_para()
            continue
        if stripped == "---":
            flush_para()
            story.append(Spacer(1, 0.2 * cm))
            story.append(HRFlowable(width="100%", thickness=1,
                                    color=colors.HexColor("#cccccc")))
            story.append(Spacer(1, 0.1 * cm))
            continue

        m = img_re.search(stripped)
        if m:
            flush_para()
            caption, src = m.group(1), urllib.parse.unquote(m.group(2))
            story += add_image(os.path.join(BASE_DIR, src), caption)
            continue

        if stripped.startswith("# "):
            flush_para()
            story.append(Paragraph(inline(stripped[2:]), title_style))
        elif stripped.startswith("## "):
            flush_para()
            story.append(Paragraph(inline(stripped[3:]), h2_style))
        elif stripped.startswith("### "):
            flush_para()
            story.append(Paragraph(inline(stripped[4:]), section_style))
        elif stripped.startswith("**Periode:**"):
            flush_para()
            story.append(Paragraph(inline(stripped), subtitle_style))
        elif stripped.startswith("- "):
            flush_para()
            story.append(Paragraph(inline(stripped[2:]), bullet_style, bulletText="•"))
        elif stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
            flush_para()
            story.append(Paragraph(inline(stripped.strip("*")), footer_style))
        else:
            para.append(stripped)

    flush_para()
    return story


def main():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=MARGIN,
                            rightMargin=MARGIN, topMargin=MARGIN,
                            bottomMargin=MARGIN)
    doc.build(build_story())
    print(f"PDF berhasil dibuat: {OUTPUT}")


if __name__ == "__main__":
    main()
