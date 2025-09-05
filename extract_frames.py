#!/usr/bin/env python3
# Indique que le script doit être exécuté avec python3

# extract_frames.py
# Nom du fichier script

# Importation des modules nécessaires
import cv2  # OpenCV pour le traitement vidéo
import argparse  # Pour l'analyse des arguments de la ligne de commande
from pathlib import Path  # Pour la manipulation des chemins de fichiers

# Fonction principale du script
def main():
    # Crée un analyseur d'arguments
    p = argparse.ArgumentParser(description="Extrait des images d'une vidéo (MP4/AVI).")
    # Ajoute les arguments attendus
    p.add_argument("video", help="Chemin vers le fichier vidéo d'entrée (ex: .mp4)")
    p.add_argument("--outdir", default="frames", help="Dossier de sortie pour les images (PNG)")
    p.add_argument("--every", type=int, default=10, help="Conserver 1 image toutes les N images (défaut 10)")
    # Analyse les arguments de la ligne de commande
    args = p.parse_args()

    # Crée un objet Path pour le dossier de sortie
    outdir = Path(args.outdir)
    # Crée le dossier de sortie s'il n'existe pas, y compris les parents
    outdir.mkdir(parents=True, exist_ok=True)

    # Ouvre le fichier vidéo avec OpenCV
    cap = cv2.VideoCapture(args.video)
    # Vérifie si la vidéo a été ouverte correctement
    if not cap.isOpened():
        raise SystemExit(f"Impossible d'ouvrir la vidéo: {args.video}")

    # Récupère le nombre total d'images dans la vidéo
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    # Initialise l'index de l'image actuelle
    idx = 0
    # Initialise le compteur d'images conservées
    kept = 0
    # Calcule le nombre de zéros pour le remplissage du nom de fichier (padding)
    zpad = max(6, len(str(total)))

    # Boucle pour lire la vidéo image par image
    while True:
        # Lit une image de la vidéo
        ok, frame = cap.read()
        # Si 'ok' est False, la fin de la vidéo est atteinte
        if not ok:
            break
        # Vérifie si l'index de l'image est un multiple de 'every'
        if idx % args.every == 0:
            # Construit le nom du fichier de sortie avec padding de zéros
            fname = outdir / f"frame_{str(kept).zfill(zpad)}.png"
            # Sauvegarde l'image au format PNG
            cv2.imwrite(str(fname), frame)
            # Incrémente le compteur d'images conservées
            kept += 1
        # Incrémente l'index de l'image
        idx += 1

    # Libère la ressource de capture vidéo
    cap.release()
    # Affiche un message de confirmation
    print(f"OK - Images extraites: {kept} -> {outdir}")

# Point d'entrée du script
if __name__ == "__main__":
    main()
