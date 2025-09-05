# video2pdf-watermark

Pipeline en 4 étapes pour convertir une vidéo (MP4/AVI) en PDF avec filigrane (watermark) :
1) extraction d’images  
2) déduplication d’images (exacte ou perceptuelle)  
3) assemblage en PDF  
4) ajout du watermark texte

## 🔧 Prérequis
- Python 3.10+  
- (Linux/macOS/WSL) Bash pour `run_pipeline.sh`  
- ffmpeg *non requis* (OpenCV lit directement les MP4)

## ⚡ Installation rapide

### Option A — Environnement virtuel (recommandé)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
chmod +x run_pipeline.sh
