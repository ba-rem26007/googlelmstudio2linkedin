#!/usr/bin/env python3
# images_to_pdf.py
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from PIL import Image

PAGESIZES = {"A4": A4, "LETTER": LETTER}

def list_images(folder: Path):
    exts = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
    return sorted([p for p in folder.iterdir() if p.suffix.lower() in exts])

def draw_image(c, img_path, page_w, page_h, fit="contain"):
    im = Image.open(img_path)
    iw, ih = im.size
    ratio_w = page_w / iw
    ratio_h = page_h / ih
    if fit == "contain":
        scale = min(ratio_w, ratio_h)
    else:  # cover
        scale = max(ratio_w, ratio_h)
    w, h = iw * scale, ih * scale
    x, y = (page_w - w) / 2, (page_h - h) / 2
    c.drawInlineImage(str(img_path), x, y, width=w, height=h)

def main():
    ap = argparse.ArgumentParser(description="Build a PDF from images in a folder.")
    ap.add_argument("folder", help="Folder with images")
    ap.add_argument("--out", default="output.pdf", help="Output PDF path")
    ap.add_argument("--pagesize", choices=["A4", "LETTER", "AUTO"], default="A4")
    ap.add_argument("--fit", choices=["contain", "cover"], default="contain")
    args = ap.parse_args()

    folder = Path(args.folder)
    imgs = list_images(folder)
    if not imgs:
        raise SystemExit(f"Aucune image trouvée dans {folder}")

    if args.pagesize == "AUTO":
        first = Image.open(imgs[0])
        page_w, page_h = first.size
        c = canvas.Canvas(args.out, pagesize=(page_w, page_h))
        for img in imgs:
            im = Image.open(img)
            page_w, page_h = im.size
            c.setPageSize((page_w, page_h))
            c.drawInlineImage(str(img), 0, 0, width=page_w, height=page_h)
            c.showPage()
    else:
        page_w, page_h = {"A4": A4, "LETTER": LETTER}[args.pagesize]
        c = canvas.Canvas(args.out, pagesize=(page_w, page_h))
        for img in imgs:
            draw_image(c, img, page_w, page_h, fit=args.fit)
            c.showPage()

    c.save()
    print(f"OK - PDF créé: {args.out} ({len(imgs)} pages)")

if __name__ == "__main__":
    main()
