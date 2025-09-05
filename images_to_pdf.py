#!/usr/bin/env python3
# Indique que le script doit être exécuté avec python3

# images_to_pdf.py
# Nom du fichier script

# Importation des modules nécessaires
import argparse  # Pour l'analyse des arguments de la ligne de commande
from pathlib import Path  # Pour la manipulation des chemins de fichiers de manière orientée objet
from reportlab.pdfgen import canvas  # Pour créer des PDF
from reportlab.lib.pagesizes import A4, LETTER  # Pour les tailles de page standards
from PIL import Image  # Pour ouvrir et manipuler des images

# Dictionnaire des tailles de page disponibles
PAGESIZES = {"A4": A4, "LETTER": LETTER}

# Fonction pour lister les images dans un dossier
def list_images(folder: Path):
    # Ensemble des extensions d'images supportées
    exts = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
    # Retourne une liste triée des fichiers d'images dans le dossier
    return sorted([p for p in folder.iterdir() if p.suffix.lower() in exts])

# Fonction pour dessiner une image sur une page PDF
def draw_image(c, img_path, page_w, page_h, fit="contain"):
    # Ouvre l'image avec PIL
    im = Image.open(img_path)
    # Récupère les dimensions de l'image
    iw, ih = im.size
    # Calcule le ratio de redimensionnement en largeur et en hauteur
    ratio_w = page_w / iw
    ratio_h = page_h / ih
    # Détermine l'échelle en fonction du mode d'ajustement
    if fit == "contain":
        # "contain" : l'image est entièrement visible, conserve les proportions
        scale = min(ratio_w, ratio_h)
    else:  # "cover"
        # "cover" : l'image couvre toute la page, conserve les proportions, peut être rognée
        scale = max(ratio_w, ratio_h)
    # Calcule les nouvelles dimensions de l'image
    w, h = iw * scale, ih * scale
    # Calcule les coordonnées pour centrer l'image sur la page
    x, y = (page_w - w) / 2, (page_h - h) / 2
    # Dessine l'image sur le canevas PDF
    c.drawInlineImage(str(img_path), x, y, width=w, height=h)

# Fonction principale du script
def main():
    # Crée un analyseur d'arguments
    ap = argparse.ArgumentParser(description="Crée un PDF à partir d'images dans un dossier.")
    # Ajoute les arguments attendus
    ap.add_argument("folder", help="Dossier contenant les images")
    ap.add_argument("--out", default="output.pdf", help="Chemin du PDF de sortie")
    ap.add_argument("--pagesize", choices=["A4", "LETTER", "AUTO"], default="A4", help="Taille de la page : A4, LETTER ou AUTO")
    ap.add_argument("--fit", choices=["contain", "cover"], default="contain", help="Mode d'ajustement de l'image à la page")
    # Analyse les arguments de la ligne de commande
    args = ap.parse_args()

    # Convertit le chemin du dossier en objet Path
    folder = Path(args.folder)
    # Obtient la liste des images dans le dossier
    imgs = list_images(folder)
    # Vérifie s'il y a des images, sinon quitte le script
    if not imgs:
        raise SystemExit(f"Aucune image trouvée dans {folder}")

    # Gère la création du PDF en fonction de la taille de page choisie
    if args.pagesize == "AUTO":
        # Taille de page "AUTO" : la taille de chaque page s'adapte à la taille de l'image
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
        # Taille de page fixe (A4 ou LETTER)
        page_w, page_h = PAGESIZES[args.pagesize]
        c = canvas.Canvas(args.out, pagesize=(page_w, page_h))
        for img in imgs:
            # Dessine chaque image sur une nouvelle page
            draw_image(c, img, page_w, page_h, fit=args.fit)
            c.showPage()

    # Sauvegarde le fichier PDF
    c.save()
    # Affiche un message de confirmation
    print(f"OK - PDF créé: {args.out} ({len(imgs)} pages)")

# Point d'entrée du script
if __name__ == "__main__":
    main()
