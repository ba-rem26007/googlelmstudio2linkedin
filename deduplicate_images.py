#!/usr/bin/env python3
# deduplicate_images.py
import argparse
import hashlib
from pathlib import Path
from PIL import Image
import imagehash
import sys

SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

def iter_images(folder: Path):
    files = [p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED]
    files.sort()
    return files

def file_md5(path: Path, chunk_size=1024 * 1024):
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def perceptual_hash(path: Path):
    with Image.open(path) as im:
        im = im.convert("RGB")
        return imagehash.phash(im)

def main():
    ap = argparse.ArgumentParser(description="Remove duplicate images in a folder.")
    ap.add_argument("folder", help="Folder containing images")
    ap.add_argument("--mode", choices=["exact", "perceptual"], default="exact",
                    help="Duplicate method: exact md5 or perceptual hash")
    ap.add_argument("--threshold", type=int, default=1,
                    help="Max Hamming distance for perceptual duplicates (default: 1)")
    ap.add_argument("--dry-run", action="store_true", help="List files to delete without deleting")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        print(f"Dossier introuvable: {folder}", file=sys.stderr)
        sys.exit(1)

    images = iter_images(folder)
    if not images:
        print(f"Aucune image trouvée dans {folder}")
        return

    to_delete = []

    if args.mode == "exact":
        seen = {}
        for p in images:
            try:
                h = file_md5(p)
            except Exception as e:
                print(f"[WARN] Lecture impossible: {p} ({e})")
                continue
            if h in seen:
                to_delete.append(p)
            else:
                seen[h] = p
        groups = len(seen)
    else:
        hashes = []
        for p in images:
            try:
                h = perceptual_hash(p)
            except Exception as e:
                print(f"[WARN] Hash perceptuel impossible: {p} ({e})")
                continue
            match = None
            for hp, ref in hashes:
                if h - hp <= args.threshold:
                    match = ref
                    break
            if match is None:
                hashes.append((h, p))
            else:
                to_delete.append(p)
        groups = len(hashes)

    if args.dry_run:
        print("=== DRY RUN ===")
        for p in to_delete:
            print(f"SUPPRIMER: {p}")
        print(f"Doublons détectés: {len(to_delete)} | Groupes uniques: {groups}")
        return

    deleted = 0
    for p in to_delete:
        try:
            p.unlink()
            deleted += 1
        except Exception as e:
            print(f"[WARN] Suppression échouée: {p} ({e})")

    kept = len(images) - deleted
    print(f"OK - Uniques conservées: {kept} | Doublons supprimés: {deleted} | Groupes uniques: {groups}")

if __name__ == "__main__":
    main()


