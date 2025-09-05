#!/usr/bin/env python3
# watermark_pdf.py
import argparse
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def make_watermark_page(w, h, text, angle, size, font, opacity, ttf):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))

    # Police : option TTF personnalisée
    if ttf:
        pdfmetrics.registerFont(TTFont("WMFont", ttf))
        font_name = "WMFont"
    else:
        font_name = font

    col = Color(0, 0, 0, alpha=opacity)
    c.setFillColor(col)
    c.setStrokeColor(col)
    c.setFont(font_name, size)

    c.saveState()
    c.translate(w/2, h/2)
    c.rotate(angle)
    tw = c.stringWidth(text, font_name, size)
    c.drawString(-tw/2, -size/2, text)
    c.restoreState()

    c.save()
    buf.seek(0)
    return buf

def main():
    ap = argparse.ArgumentParser(description="Add a text watermark to every page of a PDF.")
    ap.add_argument("pdf", help="Input PDF")
    ap.add_argument("--out", default="watermarked.pdf", help="Output PDF")
    ap.add_argument("--text", default="CONFIDENTIEL", help="Watermark text")
    ap.add_argument("--opacity", type=float, default=0.18, help="0..1 (default 0.18)")
    ap.add_argument("--angle", type=float, default=45.0, help="Rotation in degrees")
    ap.add_argument("--size", type=int, default=72, help="Font size")
    ap.add_argument("--font", default="Helvetica", help="ReportLab built-in font name")
    ap.add_argument("--ttf", default=None, help="Path to a .ttf font (overrides --font)")
    args = ap.parse_args()

    reader = PdfReader(args.pdf)
    writer = PdfWriter()

    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        wm_pdf = make_watermark_page(w, h, args.text, args.angle, args.size, args.font, args.opacity, args.ttf)
        wm_page = PdfReader(wm_pdf).pages[0]
        page.merge_page(wm_page)
        writer.add_page(page)

    with open(args.out, "wb") as f:
        writer.write(f)

    print(f"OK - Watermark appliqué : {args.out} ({len(reader.pages)} pages)")

if __name__ == "__main__":
    main()
