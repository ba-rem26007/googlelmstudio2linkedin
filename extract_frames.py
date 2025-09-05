#!/usr/bin/env python3
# extract_frames.py
import cv2
import argparse
from pathlib import Path

def main():
    p = argparse.ArgumentParser(description="Extract frames from a video (MP4/AVI).")
    p.add_argument("video", help="Path to input video file (e.g., .mp4)")
    p.add_argument("--outdir", default="frames", help="Output directory for frames (PNG)")
    p.add_argument("--every", type=int, default=10, help="Keep 1 frame every N frames (default 10)")
    args = p.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Impossible d'ouvrir la vidéo: {args.video}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    idx = 0
    kept = 0
    zpad = max(6, len(str(total)))

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if idx % args.every == 0:
            fname = outdir / f"frame_{str(kept).zfill(zpad)}.png"
            cv2.imwrite(str(fname), frame)
            kept += 1
        idx += 1

    cap.release()
    print(f"OK - Images extraites: {kept} -> {outdir}")

if __name__ == "__main__":
    main()
