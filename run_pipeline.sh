#!/usr/bin/env bash
# run_pipeline.sh
set -euo pipefail

# Defaults
SAMPLE_EVERY=10
DEDUP_MODE="exact"         # exact | perceptual
DEDUP_THRESHOLD=2
PAGESIZE="A4"              # A4 | LETTER | AUTO
FIT="contain"              # contain | cover
WM_TEXT="CONFIDENTIEL"
WM_OPACITY="0.18"
WM_ANGLE="45"
WM_SIZE="72"
WM_FONT="Helvetica"
WM_TTF=""                  # chemin vers .ttf (optionnel)
OUT_PDF=""                 # si vide => auto
WORKDIR=""                 # si vide => auto

usage() {
  cat <<EOF
Usage: $0 -i INPUT.mp4 [options]

Options:
  -i FILE         Input video (MP4/AVI)
  -o FILE         Output final PDF (default: <basename>_watermarked.pdf)
  -w DIR          Work directory (default: ./work_<basename>)
  -n N            Sample every N frames (default: $SAMPLE_EVERY)
  -m MODE         Dedup mode: exact | perceptual (default: $DEDUP_MODE)
  -t N            Dedup threshold (perceptual only, default: $DEDUP_THRESHOLD)
  -p SIZE         Page size: A4 | LETTER | AUTO (default: $PAGESIZE)
  -f FIT          Fit: contain | cover (default: $FIT)
  --wm-text TXT   Watermark text (default: "$WM_TEXT")
  --wm-opacity V  Watermark opacity 0..1 (default: $WM_OPACITY)
  --wm-angle V    Watermark angle (default: $WM_ANGLE)
  --wm-size N     Watermark font size (default: $WM_SIZE)
  --wm-font NAME  ReportLab font name (default: $WM_FONT)
  --wm-ttf FILE   Path to .ttf font (overrides --wm-font)
  -h              Help

Examples:
  $0 -i input.mp4
  $0 -i input.mp4 -n 30 --wm-text "Brouillon" --wm-opacity 0.15
EOF
}

# Parse args
ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -i) INPUT="$2"; shift 2;;
    -o) OUT_PDF="$2"; shift 2;;
    -w) WORKDIR="$2"; shift 2;;
    -n) SAMPLE_EVERY="$2"; shift 2;;
    -m) DEDUP_MODE="$2"; shift 2;;
    -t) DEDUP_THRESHOLD="$2"; shift 2;;
    -p) PAGESIZE="$2"; shift 2;;
    -f) FIT="$2"; shift 2;;
    --wm-text) WM_TEXT="$2"; shift 2;;
    --wm-opacity) WM_OPACITY="$2"; shift 2;;
    --wm-angle) WM_ANGLE="$2"; shift 2;;
    --wm-size) WM_SIZE="$2"; shift 2;;
    --wm-font) WM_FONT="$2"; shift 2;;
    --wm-ttf) WM_TTF="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Arg inconnu: $1"; usage; exit 1;;
  esac
done

[[ -z "${INPUT:-}" ]] && { echo "Erreur: -i INPUT.mp4 requis"; usage; exit 1; }
[[ ! -f "$INPUT" ]] && { echo "Erreur: fichier introuvable: $INPUT"; exit 1; }

BASENAME="$(basename "${INPUT%.*}")"
WORKDIR="${WORKDIR:-work_${BASENAME}}"
FRAMES_DIR="${WORKDIR}/frames"
PDF_RAW="${WORKDIR}/${BASENAME}.pdf"
OUT_PDF="${OUT_PDF:-${BASENAME}_watermarked.pdf}"

mkdir -p "$WORKDIR"

echo "=== 1/4 Extraction d'images ==="
python3 extract_frames.py "$INPUT" --outdir "$FRAMES_DIR" --every "$SAMPLE_EVERY"

echo "=== 2/4 Déduplication d'images (${DEDUP_MODE}) ==="
if [[ "$DEDUP_MODE" == "perceptual" ]]; then
  python3 deduplicate_images.py "$FRAMES_DIR" --mode perceptual --threshold "$DEDUP_THRESHOLD"
else
  python3 deduplicate_images.py "$FRAMES_DIR" --mode exact
fi

echo "=== 3/4 Construction du PDF ==="
python3 images_to_pdf.py "$FRAMES_DIR" --out "$PDF_RAW" --pagesize "$PAGESIZE" --fit "$FIT"

echo "=== 4/4 Watermark ==="
if [[ -n "$WM_TTF" ]]; then
  python3 watermark_pdf.py "$PDF_RAW" --out "$OUT_PDF" \
    --text "$WM_TEXT" --opacity "$WM_OPACITY" --angle "$WM_ANGLE" \
    --size "$WM_SIZE" --ttf "$WM_TTF"
else
  python3 watermark_pdf.py "$PDF_RAW" --out "$OUT_PDF" \
    --text "$WM_TEXT" --opacity "$WM_OPACITY" --angle "$WM_ANGLE" \
    --size "$WM_SIZE" --font "$WM_FONT"
fi

echo "✅ Terminé."
echo "PDF final : $OUT_PDF"
echo "Dossier de travail : $WORKDIR"
