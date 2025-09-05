#!/usr/bin/env python3
# Indique que le script doit être exécuté avec python3

# watermark_pdf.py
# Nom du fichier script

# Importation des modules nécessaires
import argparse  # Pour l'analyse des arguments de la ligne de commande
from io import BytesIO  # Pour manipuler les données binaires en mémoire
from pypdf import PdfReader, PdfWriter  # Pour lire et écrire des fichiers PDF
from reportlab.pdfgen import canvas  # Pour créer des graphiques et du texte sur un PDF
from reportlab.lib.colors import Color  # Pour définir les couleurs
from reportlab.pdfbase import pdfmetrics  # Pour la gestion des polices
from reportlab.pdfbase.ttfonts import TTFont  # Pour utiliser des polices TrueType

# Définition de la fonction pour créer une page de filigrane
def make_watermark_page(w, h, text, angle, size, font, opacity, ttf):
    # Crée un objet BytesIO pour stocker le PDF du filigrane en mémoire
    buf = BytesIO()
    # Crée un canevas ReportLab avec la largeur et la hauteur de la page
    c = canvas.Canvas(buf, pagesize=(w, h))

    # Gestion de la police : option pour une police TTF personnalisée
    if ttf:
        # Enregistre la police TTF si un chemin est fourni
        pdfmetrics.registerFont(TTFont("WMFont", ttf))
        # Définit le nom de la police à utiliser
        font_name = "WMFont"
    else:
        # Utilise la police par défaut si aucune police TTF n'est spécifiée
        font_name = font

    # Définit la couleur du texte avec une opacité spécifiée
    col = Color(0, 0, 0, alpha=opacity)
    # Applique la couleur de remplissage
    c.setFillColor(col)
    # Applique la couleur du contour
    c.setStrokeColor(col)
    # Définit la police et sa taille
    c.setFont(font_name, size)

    # Sauvegarde l'état actuel du canevas
    c.saveState()
    # Déplace l'origine du canevas au centre de la page
    c.translate(w/2, h/2)
    # Fait pivoter le canevas selon l'angle spécifié
    c.rotate(angle)
    # Calcule la largeur du texte
    tw = c.stringWidth(text, font_name, size)
    # Dessine le texte centré sur le canevas
    c.drawString(-tw/2, -size/2, text)
    # Restaure l'état précédent du canevas
    c.restoreState()

    # Sauvegarde le canevas, ce qui finalise le PDF du filigrane
    c.save()
    # Remet le curseur du buffer au début
    buf.seek(0)
    # Retourne le buffer contenant le PDF du filigrane
    return buf

# Définition de la fonction principale
def main():
    # Crée un analyseur d'arguments
    ap = argparse.ArgumentParser(description="Ajoute un filigrane textuel à chaque page d'un PDF.")
    # Ajoute les arguments attendus en ligne de commande
    ap.add_argument("pdf", help="Chemin du PDF d'entrée")
    ap.add_argument("--out", default="watermarked.pdf", help="Chemin du PDF de sortie")
    ap.add_argument("--text", default="CONFIDENTIEL", help="Texte du filigrane")
    ap.add_argument("--opacity", type=float, default=0.18, help="Opacité du texte (0 à 1, par défaut 0.18)")
    ap.add_argument("--angle", type=float, default=45.0, help="Angle de rotation en degrés")
    ap.add_argument("--size", type=int, default=72, help="Taille de la police")
    ap.add_argument("--font", default="Helvetica", help="Nom de la police intégrée à ReportLab")
    ap.add_argument("--ttf", default=None, help="Chemin vers une police .ttf (remplace --font)")
    # Analyse les arguments fournis par l'utilisateur
    args = ap.parse_args()

    # Ouvre le PDF d'entrée en mode lecture
    reader = PdfReader(args.pdf)
    # Crée un objet pour écrire le nouveau PDF
    writer = PdfWriter()

    # Itère sur chaque page du PDF d'entrée
    for page in reader.pages:
        # Récupère la largeur et la hauteur de la page
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        # Crée le PDF du filigrane avec les dimensions et les options actuelles
        wm_pdf = make_watermark_page(w, h, args.text, args.angle, args.size, args.font, args.opacity, args.ttf)
        # Lit la page de filigrane nouvellement créée
        wm_page = PdfReader(wm_pdf).pages[0]
        # Fusionne la page de filigrane sur la page actuelle du PDF
        page.merge_page(wm_page)
        # Ajoute la page modifiée au writer
        writer.add_page(page)

    # Ouvre le fichier de sortie en mode écriture binaire
    with open(args.out, "wb") as f:
        # Écrit le contenu du writer dans le fichier de sortie
        writer.write(f)

    # Affiche un message de confirmation avec le nom du fichier de sortie et le nombre de pages
    print(f"OK - Filigrane appliqué : {args.out} ({len(reader.pages)} pages)")

# Vérifie si le script est exécuté directement
if __name__ == "__main__":
    # Appelle la fonction principale
    main()
