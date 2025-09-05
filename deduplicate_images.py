#!/usr/bin/env python3
# Indique que le script doit être exécuté avec python3

# deduplicate_images.py
# Nom du fichier script

# Importation des modules nécessaires
import argparse  # Pour l'analyse des arguments de la ligne de commande
import hashlib  # Pour les algorithmes de hachage (MD5 ici)
from pathlib import Path  # Pour la manipulation des chemins de fichiers
from PIL import Image  # Pour ouvrir et manipuler des images
import imagehash  # Pour le hachage perceptuel d'images
import sys  # Pour interagir avec le système (ex: stderr, exit)

# Ensemble des extensions de fichiers d'images supportées
SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# Fonction pour itérer sur les images d'un dossier
def iter_images(folder: Path):
    # Crée une liste des fichiers dont l'extension est dans SUPPORTED
    files = [p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED]
    # Trie les fichiers par ordre alphabétique
    files.sort()
    # Retourne la liste des fichiers d'images
    return files

# Fonction pour calculer le hash MD5 d'un fichier
def file_md5(path: Path, chunk_size=1024 * 1024):
    # Initialise l'objet MD5
    h = hashlib.md5()
    # Ouvre le fichier en mode lecture binaire
    with path.open("rb") as f:
        # Lit le fichier par morceaux (chunks) pour ne pas surcharger la mémoire
        for chunk in iter(lambda: f.read(chunk_size), b""):
            # Met à jour le hash avec le morceau lu
            h.update(chunk)
    # Retourne le hash sous forme de chaîne hexadécimale
    return h.hexdigest()

# Fonction pour calculer le hash perceptuel d'une image
def perceptual_hash(path: Path):
    # Ouvre l'image avec PIL
    with Image.open(path) as im:
        # Convertit l'image en RGB pour la cohérence
        im = im.convert("RGB")
        # Calcule et retourne le hash perceptuel (phash)
        return imagehash.phash(im)

# Fonction principale du script
def main():
    # Crée un analyseur d'arguments
    ap = argparse.ArgumentParser(description="Supprime les images en double dans un dossier.")
    # Ajoute les arguments attendus
    ap.add_argument("folder", help="Dossier contenant les images")
    ap.add_argument("--mode", choices=["exact", "perceptual"], default="exact",
                    help="Méthode de détection des doublons : exacte (MD5) ou perceptuelle (hash)")
    ap.add_argument("--threshold", type=int, default=1,
                    help="Distance de Hamming maximale pour les doublons perceptuels (défaut: 1)")
    ap.add_argument("--dry-run", action="store_true", help="Liste les fichiers à supprimer sans les effacer")
    # Analyse les arguments de la ligne de commande
    args = ap.parse_args()

    # Convertit le chemin du dossier en objet Path
    folder = Path(args.folder)
    # Vérifie si le dossier existe
    if not folder.exists():
        print(f"Dossier introuvable: {folder}", file=sys.stderr)
        sys.exit(1)

    # Récupère la liste des images
    images = iter_images(folder)
    # Vérifie s'il y a des images
    if not images:
        print(f"Aucune image trouvée dans {folder}")
        return

    # Initialise la liste des fichiers à supprimer
    to_delete = []

    # Mode de détection "exact" (basé sur le MD5)
    if args.mode == "exact":
        # Dictionnaire pour stocker les hashs déjà vus
        seen = {}
        # Itère sur chaque image
        for p in images:
            try:
                # Calcule le hash MD5 du fichier
                h = file_md5(p)
            except Exception as e:
                # Affiche un avertissement en cas d'erreur de lecture
                print(f"[WARN] Lecture impossible: {p} ({e})")
                continue
            # Si le hash a déjà été vu, ajoute l'image à la liste de suppression
            if h in seen:
                to_delete.append(p)
            else:
                # Sinon, ajoute le hash et le chemin au dictionnaire
                seen[h] = p
        # Nombre de groupes uniques d'images
        groups = len(seen)
    # Mode de détection "perceptual" (basé sur le hachage d'image)
    else:
        # Liste pour stocker les hashs et les chemins des images de référence
        hashes = []
        # Itère sur chaque image
        for p in images:
            try:
                # Calcule le hash perceptuel de l'image
                h = perceptual_hash(p)
            except Exception as e:
                # Affiche un avertissement en cas d'erreur
                print(f"[WARN] Hash perceptuel impossible: {p} ({e})")
                continue
            # Cherche un hash similaire dans la liste des références
            match = None
            for hp, ref in hashes:
                # Compare la distance de Hamming entre les hashs
                if h - hp <= args.threshold:
                    match = ref
                    break
            # Si aucune correspondance n'est trouvée, ajoute l'image comme nouvelle référence
            if match is None:
                hashes.append((h, p))
            else:
                # Sinon, ajoute l'image à la liste de suppression
                to_delete.append(p)
        # Nombre de groupes uniques d'images
        groups = len(hashes)

    # Si l'option --dry-run est activée
    if args.dry_run:
        print("=== DRY RUN ===")
        # Affiche les fichiers qui seraient supprimés
        for p in to_delete:
            print(f"SUPPRIMER: {p}")
        print(f"Doublons détectés: {len(to_delete)} | Groupes uniques: {groups}")
        return

    # Suppression effective des fichiers
    deleted = 0
    for p in to_delete:
        try:
            # Supprime le fichier
            p.unlink()
            deleted += 1
        except Exception as e:
            # Affiche un avertissement en cas d'échec de la suppression
            print(f"[WARN] Suppression échouée: {p} ({e})")

    # Calcule le nombre d'images conservées
    kept = len(images) - deleted
    # Affiche le résumé de l'opération
    print(f"OK - Uniques conservées: {kept} | Doublons supprimés: {deleted} | Groupes uniques: {groups}")

# Point d'entrée du script
if __name__ == "__main__":
    main()
