# file_parser.py
import re
from pathlib import Path
import chardet
from datetime import datetime
from typing import Optional, Dict, Any, List 

def detect_encoding(file_path: str) -> str:
    """Détecte l'encodage du fichier avec fallback"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Analyse les premiers 10ko
            result = chardet.detect(raw_data)
            return result['encoding'] or 'ISO-8859-1'
    except Exception as e:
        print(f"Erreur lors de la détection de l'encodage: {str(e)}")
        return 'ISO-8859-1'

def parse_file(file_path: str) -> Optional[Dict[str, Any]]:
    try:
        # Détection de l'encodage et lecture du fichier
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        if not content.strip():
            raise ValueError("Le fichier est vide ou mal formaté.")

        # Extraction de la date avec formatage robuste
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', content)
        if not date_match:
            raise ValueError("Date non trouvée dans le fichier.")
        date = datetime.strptime(date_match.group(1), '%d/%m/%Y').strftime('%Y-%m-%d')

        # Extraction du lieu
        lieu_match = re.search(r'^(.*?) /', content, re.MULTILINE)
        lieu = lieu_match.group(1).strip() if lieu_match else "Inconnu"
        # Extraction de la discipline
        discipline_match = re.search(r'^\s*(Attelé|Steeple-chase|Haies|Plat|Monté)\s*', content, re.MULTILINE)
        discipline = discipline_match.group(1).strip() if discipline_match else "Inconnu"
        # Extraction de la distance
        distance_match = re.search(r'Tiercé Quarté\+ Quinté\+ Multi / (\d+m)', content)
        distance = distance_match.group(1).strip() if distance_match else "Inconnu"
        # Extraction de l'arrivée
        arrivee_match = re.search(r'Arrivée du Tiercé/Quarté\+/Quinté\+\s*([\d\s-]+)', content)
        arrivee = arrivee_match.group(1).strip() if arrivee_match else ""
        # Extraction de la synthèse
        synthese_match = re.search(r'Place des 5 premiers dans la synthèse\s*([\d\w\s-]+)', content)
        synthese = synthese_match.group(1).strip() if synthese_match else ""
        # Extraction des partants
        partants = set()
        for line in content.splitlines():
            match = re.match(r'(\d{1,2})(?:er|e)?\s+(\d+)', line)  # Gère "1er", "2e", etc.
            if match:
                partants.add(int(match.group(2)))  # Le numéro du cheval est le deuxième élément

        if not partants:
            raise ValueError(f"Aucun partant trouvé dans le fichier {file_path}")

        return {
            'date': date,
            'lieu': lieu,
            'type': discipline,
            'distance': distance,
            'arrivée': arrivee,
            'synthese': synthese,
            'partants': list(partants)  # Convertir en liste pour stockage
        }
    except Exception as e:
        print(f"Erreur lors du parsing du fichier {file_path}: {str(e)}")
        return None