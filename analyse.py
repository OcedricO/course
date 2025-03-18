# analyse.py
from typing import List, Dict, Any, Tuple, Optional
from itertools import combinations
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import streamlit as st
import seaborn as sns
import numpy as np

def analyse_positions(courses: List[Dict[str, Any]], pos1: int, pos2: int) -> Dict[str, Any]:
    """
    Analyse les positions de synthèse pour les positions données (pos1 et pos2).
    """
    if not courses:
        return {"erreur": "Aucune donnée de course disponible."}
    
    # Initialisation des compteurs
    pos1_dans_synthese = 0
    pos2_dans_synthese = 0
    double_reussite = 0
    total_courses = len(courses)
    
    for course in courses:
        # Extraction de la synthèse
        synthese = course.get('synthese', '')  # La synthèse est une chaîne de caractères
        
        # Conversion de la synthèse en liste de chaînes (avec ou sans 'e')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        
        # Affichage pour vérification
        print(f"Synthèse : {synthese_list}")
        
        # Vérification des positions dans la synthèse
        if str(pos1) in [x.replace('e', '') for x in synthese_list]:
            pos1_dans_synthese += 1
        
        if str(pos2) in [x.replace('e', '') for x in synthese_list]:
            pos2_dans_synthese += 1
        
        # Vérification de la double réussite
        if (str(pos1) in [x.replace('e', '') for x in synthese_list] and
            str(pos2) in [x.replace('e', '') for x in synthese_list]):
            double_reussite += 1
    
    # Calcul des pourcentages
    pos1_reussite = (pos1_dans_synthese / total_courses) * 100 if total_courses > 0 else 0
    pos2_reussite = (pos2_dans_synthese / total_courses) * 100 if total_courses > 0 else 0
    double_reussite_pct = (double_reussite / total_courses) * 100 if total_courses > 0 else 0
    
    return {
        'total_courses': total_courses,
        'pos1_reussite': pos1_reussite,
        'pos2_reussite': pos2_reussite,
        'double_reussite': double_reussite_pct
    }

def analyse_positions_arrivee(courses: List[Dict[str, Any]], num1: int, num2: int) -> Dict[str, Any]:
    """
    Analyse les positions de l'arrivée pour les numéros donnés (num1 et num2).
    """
    if not courses:
        return {"erreur": "Aucune donnée de course disponible."}
    
    # Initialisation des compteurs
    num1_dans_arrivee = 0
    num2_dans_arrivee = 0
    double_reussite = 0
    total_courses = len(courses)
    courses_double_reussite = []  # Liste des courses où les deux numéros sont arrivés
    
    for course in courses:
        # Extraction de l'arrivée
        arrivee = course.get('arrivee', '')  # L'arrivée est une chaîne de caractères
        
        # Conversion de l'arrivée en liste de numéros
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        # Vérification des numéros dans l'arrivée
        if str(num1) in arrivee_list:
            num1_dans_arrivee += 1
        
        if str(num2) in arrivee_list:
            num2_dans_arrivee += 1
        
        # Vérification de la double réussite
        if str(num1) in arrivee_list and str(num2) in arrivee_list:
            double_reussite += 1
            courses_double_reussite.append(course['date_course'])  # Ajouter la date de la course
    
    # Calcul des pourcentages
    num1_reussite = (num1_dans_arrivee / total_courses) * 100 if total_courses > 0 else 0
    num2_reussite = (num2_dans_arrivee / total_courses) * 100 if total_courses > 0 else 0
    double_reussite_pct = (double_reussite / total_courses) * 100 if total_courses > 0 else 0
    
    return {
        'total_courses': total_courses,
        'num1_reussite': num1_reussite,
        'num2_reussite': num2_reussite,
        'double_reussite': double_reussite_pct,
        'courses_double_reussite': courses_double_reussite  # Ajouter la liste des courses
    }
    

def analyse_all_pairs(courses: List[Dict[str, Any]]) -> None:
    """
    Analyse toutes les paires de positions possibles dans la synthèse.
    """
    if not courses:
        print("Aucune donnée de course disponible.")
        return
    
    # Liste de toutes les paires possibles (pos1, pos2) où 1 <= pos1 < pos2 <= 5
    paires = [(pos1, pos2) for pos1 in range(1, 6) for pos2 in range(pos1 + 1, 6)]
    
    print("\n=== Analyse de toutes les paires de positions ===")
    for pos1, pos2 in paires:
        resultats = analyse_positions(courses, pos1, pos2)
        print(f"\nPaire ({pos1}, {pos2}) :")
        print(f"Position {pos1} de la synthèse : {resultats['pos1_reussite']:.1f}% de réussite dans le top 5")
        print(f"Position {pos2} de la synthèse : {resultats['pos2_reussite']:.1f}% de réussite dans le top 5")
        print(f"Double réussite : {resultats['double_reussite']:.1f}% des courses")

def analyse_frequence_arrivee(courses: List[Dict[str, Any]], top_n: int = 3) -> Dict[int, float]:
    """
    Analyse la fréquence des numéros dans les top_n premières positions de l'arrivée.
    :param courses: Liste des courses.
    :param top_n: Nombre de positions à analyser (par défaut 3).
    :return: Dictionnaire avec les numéros et leur fréquence en pourcentage.
    """
    if not courses:
        return {}
    
    # Initialisation du compteur
    compteur = Counter()
    
    for course in courses:
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        for i, num in enumerate(arrivee_list[:top_n]):
            if num.isdigit():
                compteur[int(num)] += 1
    
    total_courses = len(courses)
    return {num: (count / total_courses) * 100 for num, count in compteur.items()}

def analyser_couples_arrivee(courses: List[Dict[str, Any]]) -> Dict[tuple, float]:
    """
    Analyse la fréquence des couples de numéros dans l'arrivée.
    """
    if not courses:
        return {}
    
    couple_compteur = defaultdict(int)
    total_courses = len(courses)
    
    for course in courses:
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        for couple in combinations(numeros, 2):
            couple_compteur[tuple(sorted(couple))] += 1
    
    return {couple: (count / total_courses) * 100 for couple, count in couple_compteur.items()}

def analyser_triples_arrivee(courses: List[Dict[str, Any]]) -> Dict[tuple, float]:
    """
    Analyse la fréquence des triples de numéros dans l'arrivée.
    """
    if not courses:
        return {}
    
    triple_compteur = defaultdict(int)
    total_courses = len(courses)
    
    for course in courses:
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        for triple in combinations(numeros, 3):
            triple_compteur[tuple(sorted(triple))] += 1
    
    return {triple: (count / total_courses) * 100 for triple, count in triple_compteur.items()}

def analyser_ecarts_arrivee(courses: List[Dict[str, Any]]) -> Dict[int, float]:
    """
    Analyse la fréquence des écarts entre les numéros dans l'arrivée.
    """
    if not courses:
        return {}
    
    ecart_compteur = defaultdict(int)
    total_courses = len(courses)
    
    for course in courses:
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        for i in range(len(numeros) - 1):
            ecart = abs(numeros[i] - numeros[i + 1])
            ecart_compteur[ecart] += 1
    
    return {ecart: (count / total_courses) * 100 for ecart, count in ecart_compteur.items()}

def calculer_ecarts_numeros_arrivee(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """
    Calcule l'écart et l'écart maximum pour chaque numéro dans l'arrivée.
    """
    courses_triees = sorted(courses, key=lambda x: x['date_course'])
    
    ecarts_numeros = defaultdict(lambda: {"derniere_occurrence": -1, "ecart_actuel": 0, "ecart_max": 0})
    total_courses = len(courses_triees)
    
    for index, course in enumerate(courses_triees):
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        for num in numeros:
            if ecarts_numeros[num]["derniere_occurrence"] != -1:
                ecart = index - ecarts_numeros[num]["derniere_occurrence"] - 1
                if ecart > ecarts_numeros[num]["ecart_max"]:
                    ecarts_numeros[num]["ecart_max"] = ecart
            ecarts_numeros[num]["derniere_occurrence"] = index
    
    dernier_index = len(courses_triees) - 1
    for num in ecarts_numeros:
        if ecarts_numeros[num]["derniere_occurrence"] == dernier_index:
            ecarts_numeros[num]["ecart_actuel"] = 0
        else:
            ecarts_numeros[num]["ecart_actuel"] = dernier_index - ecarts_numeros[num]["derniere_occurrence"]
        
        if ecarts_numeros[num]["derniere_occurrence"] == -1:
            ecarts_numeros[num]["ecart_max"] = total_courses
        elif ecarts_numeros[num]["ecart_actuel"] > ecarts_numeros[num]["ecart_max"]:
            ecarts_numeros[num]["ecart_max"] = ecarts_numeros[num]["ecart_actuel"]
    
    return ecarts_numeros

def calculer_ecarts_couples_arrivee(courses: List[Dict[str, Any]]) -> Dict[tuple, Dict[str, int]]:
    """
    Calcule l'écart et l'écart maximum pour chaque couple de numéros dans l'arrivée.
    """
    courses_triees = sorted(courses, key=lambda x: x['date_course'])
    ecarts_couples = defaultdict(lambda: {"derniere_occurrence": -1, "ecart_actuel": 0, "ecart_max": 0})
    total_courses = len(courses_triees)
    
    for index, course in enumerate(courses_triees):
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        # Générer tous les couples possibles
        for couple in combinations(numeros, 2):
            couple_trié = tuple(sorted(couple))
            if ecarts_couples[couple_trié]["derniere_occurrence"] != -1:
                ecart = index - ecarts_couples[couple_trié]["derniere_occurrence"] - 1
                if ecart > ecarts_couples[couple_trié]["ecart_max"]:
                    ecarts_couples[couple_trié]["ecart_max"] = ecart
            ecarts_couples[couple_trié]["derniere_occurrence"] = index
    
    dernier_index = len(courses_triees) - 1
    for couple in ecarts_couples:
        if ecarts_couples[couple]["derniere_occurrence"] == dernier_index:
            ecarts_couples[couple]["ecart_actuel"] = 0
        else:
            ecarts_couples[couple]["ecart_actuel"] = dernier_index - ecarts_couples[couple]["derniere_occurrence"]
        
        if ecarts_couples[couple]["derniere_occurrence"] == -1:
            ecarts_couples[couple]["ecart_max"] = total_courses
        elif ecarts_couples[couple]["ecart_actuel"] > ecarts_couples[couple]["ecart_max"]:
            ecarts_couples[couple]["ecart_max"] = ecarts_couples[couple]["ecart_actuel"]
    
    return ecarts_couples

def calculer_ecarts_triples_arrivee(courses: List[Dict[str, Any]]) -> Dict[tuple, Dict[str, int]]:
    """
    Calcule l'écart et l'écart maximum pour chaque triple de numéros dans l'arrivée.
    """
    courses_triees = sorted(courses, key=lambda x: x['date_course'])
    ecarts_triples = defaultdict(lambda: {"derniere_occurrence": -1, "ecart_actuel": 0, "ecart_max": 0})
    total_courses = len(courses_triees)
    
    for index, course in enumerate(courses_triees):
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        # Générer tous les triples possibles
        for triple in combinations(numeros, 3):
            triple_trié = tuple(sorted(triple))
            if ecarts_triples[triple_trié]["derniere_occurrence"] != -1:
                ecart = index - ecarts_triples[triple_trié]["derniere_occurrence"] - 1
                if ecart > ecarts_triples[triple_trié]["ecart_max"]:
                    ecarts_triples[triple_trié]["ecart_max"] = ecart
            ecarts_triples[triple_trié]["derniere_occurrence"] = index
    
    dernier_index = len(courses_triees) - 1
    for triple in ecarts_triples:
        if ecarts_triples[triple]["derniere_occurrence"] == dernier_index:
            ecarts_triples[triple]["ecart_actuel"] = 0
        else:
            ecarts_triples[triple]["ecart_actuel"] = dernier_index - ecarts_triples[triple]["derniere_occurrence"]
        
        if ecarts_triples[triple]["derniere_occurrence"] == -1:
            ecarts_triples[triple]["ecart_max"] = total_courses
        elif ecarts_triples[triple]["ecart_actuel"] > ecarts_triples[triple]["ecart_max"]:
            ecarts_triples[triple]["ecart_max"] = ecarts_triples[triple]["ecart_actuel"]
    
    return ecarts_triples

def calculer_ecarts_numeros_arrivee_avec_participation(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """
    Calcule l'écart et l'écart maximum pour chaque numéro dans l'arrivée, en tenant compte des courses où le numéro a couru.
    :param courses: Liste des courses.
    :return: Dictionnaire contenant les écarts pour chaque numéro.
    """
    courses_triees = sorted(courses, key=lambda x: x['date_course'])
    
    ecarts_numeros = defaultdict(lambda: {"derniere_occurrence": -1, "ecart_actuel": 0, "ecart_max": 0, "courses_participées": 0})
    total_courses = len(courses_triees)
    
    for index, course in enumerate(courses_triees):
        arrivee = course.get('arrivee', '')
        arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
        
        numeros = [int(x.replace('e', '')) for x in arrivee_list if x.replace('e', '').isdigit()]
        
        for num in numeros:
            if ecarts_numeros[num]["derniere_occurrence"] != -1:
                ecart = index - ecarts_numeros[num]["derniere_occurrence"] - 1
                if ecart > ecarts_numeros[num]["ecart_max"]:
                    ecarts_numeros[num]["ecart_max"] = ecart
            ecarts_numeros[num]["derniere_occurrence"] = index
            ecarts_numeros[num]["courses_participées"] += 1
    
    dernier_index = len(courses_triees) - 1
    for num in ecarts_numeros:
        if ecarts_numeros[num]["derniere_occurrence"] == dernier_index:
            ecarts_numeros[num]["ecart_actuel"] = 0
        else:
            ecarts_numeros[num]["ecart_actuel"] = dernier_index - ecarts_numeros[num]["derniere_occurrence"]
        
        if ecarts_numeros[num]["derniere_occurrence"] == -1:
            ecarts_numeros[num]["ecart_max"] = total_courses
        elif ecarts_numeros[num]["ecart_actuel"] > ecarts_numeros[num]["ecart_max"]:
            ecarts_numeros[num]["ecart_max"] = ecarts_numeros[num]["ecart_actuel"]
    
    return ecarts_numeros

def analyser_par_discipline_et_distance_arrivee(courses: List[Dict[str, Any]], discipline: str, distance: str) -> Dict[str, Any]:
    """
    Analyse les données d'arrivée filtrées par discipline et distance.
    """
    # Filtrer les courses par discipline et distance
    courses_filtrees = [course for course in courses if course.get('type_course') == discipline and course.get('distance') == distance]
    
    if not courses_filtrees:
        return {"erreur": "Aucune donnée disponible pour les critères sélectionnés."}
    
    # Calculer les statistiques pour les courses filtrées
    resultats = {
        'total_courses': len(courses_filtrees),
        'frequence_arrivee': analyse_frequence_arrivee(courses_filtrees),
        'ecarts_numeros_arrivee': calculer_ecarts_numeros_arrivee(courses_filtrees),
        'ecarts_couples_arrivee': calculer_ecarts_couples_arrivee(courses_filtrees),
        'ecarts_triples_arrivee': calculer_ecarts_triples_arrivee(courses_filtrees),
    }
    
    return resultats

def analyser_numero_synthese(courses: List[Dict[str, Any]], numero_cible: int) -> Dict[str, Any]:
    stats = {
        'total_courses': 0,
        'presence_top3': 0,
        'paires_avec_cible': defaultdict(int),  # Changement de nom
        'triplets': defaultdict(int),
        'ecarts': {
            'actuel': 0,
            'max': 0,
            'historique': []
        }
    }
    
    dernier_index = -1
    
    for idx, course in enumerate(courses):
        stats['total_courses'] += 1
        
        synthese = course.get('synthese', '')
        elements = [x.strip().lower().rstrip('e') for x in synthese.split('-') if x.strip()]
        
        try:
            top3 = list(map(int, elements[:3]))
        except (ValueError, IndexError):
            continue
            
        if numero_cible in top3:
            stats['presence_top3'] += 1
            
            # Génération des paires AVEC le numéro cible
            autres = [n for n in top3 if n != numero_cible]
            for autre_num in autres:
                paire = tuple(sorted([numero_cible, autre_num]))
                stats['paires_avec_cible'][paire] += 1  # Stockage correct
            
            # Triplet complet
            stats['triplets'][tuple(sorted(top3))] += 1
            
            # Calcul des écarts
            if dernier_index != -1:
                ecart = idx - dernier_index - 1
                stats['ecarts']['historique'].append(ecart)
                stats['ecarts']['max'] = max(stats['ecarts']['max'], ecart)
            dernier_index = idx
    
    stats['ecarts']['actuel'] = len(courses) - dernier_index - 1 if dernier_index != -1 else 0
    return stats

def analyse_frequence_synthese(courses: List[Dict[str, Any]]) -> Dict[int, float]:
    """
    Analyse la fréquence d'apparition de chaque numéro dans la synthèse.
    :param courses: Liste des courses.
    :return: Dictionnaire avec les numéros et leur fréquence en pourcentage.
    """
    if not courses:
        return {}
    
    # Initialisation du compteur
    compteur = Counter()
    
    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        
        for element in synthese_list:
            num = element.replace('e', '')
            if num.isdigit():
                compteur[int(num)] += 1
    
    total_courses = len(courses)
    return {num: (count / total_courses) * 100 for num, count in compteur.items()}

def analyser_couples_synthese(courses: List[Dict[str, Any]]) -> Dict[tuple, float]:
    """
    Analyse la fréquence des couples de numéros dans la synthèse.
    """
    if not courses:
        return {}
    
    # Initialisation du compteur pour les couples
    couple_compteur = defaultdict(int)
    total_courses = len(courses)
    
    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        
        # Extraction des numéros de la synthèse
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]
        
        # Génération de toutes les paires possibles
        for couple in combinations(numeros, 2):
            couple_compteur[tuple(sorted(couple))] += 1
    
    # Calcul des pourcentages
    return {couple: (count / total_courses) * 100 for couple, count in couple_compteur.items()}

def analyser_triples_synthese(courses: List[Dict[str, Any]]) -> Dict[tuple, float]:
    """
    Analyse la fréquence des triples de numéros dans la synthèse.
    """
    if not courses:
        return {}
    
    # Initialisation du compteur pour les triples
    triple_compteur = defaultdict(int)
    total_courses = len(courses)
    
    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        
        # Extraction des numéros de la synthèse
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]
        
        # Génération de toutes les combinaisons de 3 numéros
        for triple in combinations(numeros, 3):
            triple_compteur[tuple(sorted(triple))] += 1
    
    # Calcul des pourcentages
    return {triple: (count / total_courses) * 100 for triple, count in triple_compteur.items()}

def analyser_ecarts_synthese(courses: List[Dict[str, Any]]) -> Dict[int, float]:
    """
    Analyse la fréquence des écarts entre les numéros dans la synthèse.
    """
    if not courses:
        return {}
    
    # Initialisation du compteur pour les écarts
    ecart_compteur = defaultdict(int)
    total_courses = len(courses)
    
    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        
        # Extraction des numéros de la synthèse
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]
        
        # Calcul des écarts entre les numéros
        for i in range(len(numeros) - 1):
            ecart = abs(numeros[i] - numeros[i + 1])
            ecart_compteur[ecart] += 1
    
    # Calcul des pourcentages
    return {ecart: (count / total_courses) * 100 for ecart, count in ecart_compteur.items()}

def calculer_ecarts_numeros(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """
    Calcule l'écart et l'écart maximum pour chaque numéro dans la synthèse.
    :param courses: Liste des courses.
    :return: Dictionnaire contenant les écarts pour chaque numéro.
    """
    # Tri des courses par date
    courses_triees = sorted(courses, key=lambda x: x['date_course'])
    
    # Dictionnaire pour stocker les écarts
    ecarts_numeros = defaultdict(lambda: {"derniere_occurrence": -1, "ecart_actuel": 0, "ecart_max": 0})
    total_courses = len(courses_triees)
    
    for index, course in enumerate(courses_triees):
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        
        # Extraction des numéros de la synthèse
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]
        
        # Mise à jour des écarts pour chaque numéro
        for num in numeros:
            if ecarts_numeros[num]["derniere_occurrence"] != -1:
                ecart = index - ecarts_numeros[num]["derniere_occurrence"] - 1
                if ecart > ecarts_numeros[num]["ecart_max"]:
                    ecarts_numeros[num]["ecart_max"] = ecart
            ecarts_numeros[num]["derniere_occurrence"] = index
    
    # Calcul de l'écart actuel pour la dernière course
    dernier_index = len(courses_triees) - 1
    for num in ecarts_numeros:
        if ecarts_numeros[num]["derniere_occurrence"] == dernier_index:
            ecarts_numeros[num]["ecart_actuel"] = 0  # Apparu dans la dernière course
        else:
            ecarts_numeros[num]["ecart_actuel"] = dernier_index - ecarts_numeros[num]["derniere_occurrence"]
        
        # Si le numéro n'est jamais apparu, l'écart maximum est égal au nombre total de courses
        if ecarts_numeros[num]["derniere_occurrence"] == -1:
            ecarts_numeros[num]["ecart_max"] = total_courses
        # Sinon, s'assurer que l'écart actuel ne dépasse pas l'écart maximum
        elif ecarts_numeros[num]["ecart_actuel"] > ecarts_numeros[num]["ecart_max"]:
            ecarts_numeros[num]["ecart_max"] = ecarts_numeros[num]["ecart_actuel"]
    
    return ecarts_numeros

def calculer_ecarts_combinaisons(courses, taille_combinaison=2):
    """
    Calcule l'écart et l'écart maximum pour chaque combinaison de numéros (couple ou triple).
    """
    if not courses:
        return {}

    # Tri des courses par date
    courses_triees = sorted(courses, key=lambda x: x['date_course'])

    # Dictionnaire pour stocker les écarts
    ecarts_combinaisons = defaultdict(lambda: {"derniere_occurrence": -1, "ecart_actuel": 0, "ecart_max": 0, "occurrences": []})

    # Parcourir les courses triées par date
    for index, course in enumerate(courses_triees):
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]

        # Extraction des numéros de la synthèse
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

        # Génération de toutes les combinaisons possibles
        for combinaison in combinations(numeros, taille_combinaison):
            combinaison_triee = tuple(sorted(combinaison))
            ecarts_combinaisons[combinaison_triee]["occurrences"].append(index)

    # Calcul des écarts pour chaque combinaison
    for combinaison, data in ecarts_combinaisons.items():
        occurrences = data["occurrences"]
        if not occurrences:
            # Si la combinaison n'est jamais apparue
            data["ecart_actuel"] = len(courses_triees)
            data["ecart_max"] = len(courses_triees)
        else:
            # Calcul des écarts entre les occurrences
            ecarts = []
            prev_occurrence = -1
            for occurrence in occurrences:
                if prev_occurrence != -1:
                    ecart = occurrence - prev_occurrence - 1
                    ecarts.append(ecart)
                prev_occurrence = occurrence

            # Ajouter l'écart entre la première occurrence et le début
            ecarts.append(occurrences[0])  # Écart avant la première occurrence

            # Ajouter l'écart entre la dernière occurrence et la fin
            ecarts.append(len(courses_triees) - 1 - occurrences[-1])

            # L'écart maximum est le plus grand écart observé
            data["ecart_max"] = max(ecarts) if ecarts else 0

            # Calcul de l'écart actuel
            derniere_occurrence = occurrences[-1]
            if derniere_occurrence == len(courses_triees) - 1:
                # Si la combinaison est apparue dans la dernière course
                data["ecart_actuel"] = 0
            else:
                # Sinon, l'écart actuel est le nombre de courses depuis la dernière occurrence
                data["ecart_actuel"] = len(courses_triees) - 1 - derniere_occurrence

    return ecarts_combinaisons

def afficher_graphique_frequence(frequence: Dict[int, float]):
    """
    Affiche un graphique de la fréquence des numéros dans la synthèse.
    :param frequence: Dictionnaire contenant les fréquences des numéros.
    """
    nums = sorted(frequence.keys())
    freqs = [frequence[num] for num in nums]
    
    plt.bar(nums, freqs, color='blue')
    plt.xlabel('Numéro')
    plt.ylabel('Fréquence (%)')
    plt.title('Fréquence des numéros dans la synthèse')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    plt.close()
    
def afficher_graphique_ecarts(ecarts: Dict[int, float]):
    """
    Affiche un graphique en barres des écarts entre les numéros dans la synthèse.
    :param ecarts: Dictionnaire contenant les écarts entre les numéros.
    """
    ecarts_keys = sorted(ecarts.keys())
    ecarts_values = [ecarts[key] for key in ecarts_keys]
    
    plt.bar(ecarts_keys, ecarts_values, color='green')
    plt.xlabel('Écart')
    plt.ylabel('Fréquence (%)')
    plt.title('Fréquence des écarts entre les numéros dans la synthèse')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()
    plt.close()

def afficher_graphique_frequence_numeros(frequence: Dict[int, float]):
    """
    Affiche un graphique en barres de la fréquence des numéros dans la synthèse.
    :param frequence: Dictionnaire contenant les fréquences des numéros.
    """
    nums = sorted(frequence.keys())
    freqs = [frequence[num] for num in nums]
    
    plt.bar(nums, freqs, color='skyblue', edgecolor='black')
    plt.xlabel('Numéro')
    plt.ylabel('Fréquence (%)')
    plt.title('Fréquence des numéros dans la synthèse')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Ajouter des annotations
    for i, freq in enumerate(freqs):
        plt.text(nums[i], freq + 1, f"{freq:.1f}%", ha='center')
    
    plt.show()
    plt.close()

def afficher_graphique_frequence_couples(frequence_couples: Dict[Tuple[int, int], float]):
    """
    Affiche un graphique en barres de la fréquence des couples de numéros dans la synthèse.
    :param frequence_couples: Dictionnaire contenant les fréquences des couples.
    """
    couples = sorted(frequence_couples.keys(), key=lambda x: frequence_couples[x], reverse=True)  # Tous
    freqs = [frequence_couples[couple] for couple in couples]
    labels = [f"{couple[0]}-{couple[1]}" for couple in couples]
    
    plt.bar(labels, freqs, color='lightgreen', edgecolor='black')
    plt.xlabel('Couple de numéros')
    plt.ylabel('Fréquence (%)')
    plt.title('Fréquence des couples de numéros dans la synthèse ')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Ajouter des annotations
    for i, freq in enumerate(freqs):
        plt.text(i, freq + 1, f"{freq:.1f}%", ha='center')
    
    plt.xticks(rotation=90)  # Rotation des étiquettes pour une meilleure lisibilité
    plt.show()
    plt.close()

def afficher_graphique_frequence_triples(frequence_triples: Dict[Tuple[int, int, int], float]):
    """
    Affiche un graphique en barres de la fréquence des triples de numéros dans la synthèse.
    :param frequence_triples: Dictionnaire contenant les fréquences des triples.
    """
    # Trier tous les triples par fréquence (du plus fréquent au moins fréquent)
    triples = sorted(frequence_triples.keys(), key=lambda x: frequence_triples[x], reverse=True)
    
    # Extraire les fréquences et les labels pour tous les triples
    freqs = [frequence_triples[triple] for triple in triples]
    labels = [f"{triple[0]}-{triple[1]}-{triple[2]}" for triple in triples]
    
    # Créer le graphique en barres
    plt.figure(figsize=(12, 6))  # Ajuster la taille du graphique pour une meilleure lisibilité
    plt.bar(labels, freqs, color='salmon', edgecolor='black')
    
    # Ajouter des labels et un titre
    plt.xlabel('Triple de numéros')
    plt.ylabel('Fréquence (%)')
    plt.title('Fréquence des triples de numéros dans la synthèse')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Rotation des étiquettes pour une meilleure lisibilité
    plt.xticks(rotation=90)
    
    # Afficher ou sauvegarder le graphique
    plt.tight_layout()  # Ajuster l'espacement pour éviter que les étiquettes se chevauchent
    plt.show()
    plt.close()

def comparer_arrivees(courses: List[Dict[str, Any]]) -> List[str]:
    """
    Compare les numéros des deux dernières arrivées et retourne les numéros en commun.
    :param courses: Liste des courses.
    :return: Liste des numéros en commun entre les deux dernières arrivées.
    """
    if len(courses) < 2:
        return []  # Pas assez de courses pour comparer
    
    # Extraire les deux dernières arrivées
    derniere_arrivee = courses[-1]['arrivee'].strip()
    avant_derniere_arrivee = courses[-2]['arrivee'].strip()
    
    # Nettoyer les numéros : supprimer les espaces et les caractères indésirables
    derniere_numeros = [num.strip() for num in derniere_arrivee.split('-') if num.strip()]
    avant_derniere_numeros = [num.strip() for num in avant_derniere_arrivee.split('-') if num.strip()]
    
    # Convertir en ensembles pour faciliter la comparaison
    derniere_set = set(derniere_numeros)
    avant_derniere_set = set(avant_derniere_numeros)
    
    # Retourner les numéros en commun
    return list(derniere_set.intersection(avant_derniere_set))

def comparer_syntheses(courses: List[Dict[str, Any]]) -> int:
    """
    Compare les numéros des deux dernières synthèses et retourne le nombre de numéros en commun.
    :param courses: Liste des courses.
    :return: Nombre de numéros en commun entre les deux dernières synthèses.
    """
    if len(courses) < 2:
        return 0  # Pas assez de courses pour comparer
    
    derniere_synthese = courses[-1]['synthese'].split('-')
    avant_derniere_synthese = courses[-2]['synthese'].split('-')
    
    # Convertir en ensembles pour faciliter la comparaison
    derniere_synthese_set = set(derniere_synthese)
    avant_derniere_synthese_set = set(avant_derniere_synthese)
    
    # Retourner le nombre de numéros en commun
    return len(derniere_synthese_set.intersection(avant_derniere_synthese_set))

def extraire_partants(partants_str: Optional[str]) -> set[int]:
    """
    Extrait les numéros des partants à partir d'une chaîne de caractères.
    :param partants_str: Chaîne de caractères contenant les partants (peut être None ou vide).
    :return: Ensemble des numéros des partants.
    """
    partants = set()
    if not partants_str:  # Si partants_str est None ou vide
        return partants  # Retourne un ensemble vide

    for line in partants_str.splitlines():
        # Exemple de ligne : "1er 	8 	Doctor Ron 		5040"
        parts = line.split()
        if len(parts) >= 2:  # Vérifie qu'il y a au moins un numéro
            try:
                numero = int(parts[1])  # Le numéro est le deuxième élément
                partants.add(numero)
            except (ValueError, IndexError):
                continue  # Ignore les lignes mal formatées
    return partants

def afficher_courbe_numeros_communs(courses: List[Dict[str, Any]]) -> None:
    """
    Affiche une courbe montrant le nombre de numéros en commun entre les deux dernières arrivées pour chaque course,
    ainsi que la moyenne cumulative en rouge. Affiche également une liste des numéros en commun.
    :param courses: Liste des courses.
    """
    dates = []
    numeros_communs = []
    moyennes_cumulatives = []
    numeros_communs_liste = []  # Liste pour stocker les numéros en commun
    
    for i in range(1, len(courses)):
        # Extraire les deux dernières arrivées
        derniere_arrivee = courses[i]['arrivee'].strip()
        avant_derniere_arrivee = courses[i-1]['arrivee'].strip()
        
        # Nettoyer les numéros : supprimer les espaces et les caractères indésirables
        derniere_numeros = [num.strip() for num in derniere_arrivee.split('-') if num.strip()]
        avant_derniere_numeros = [num.strip() for num in avant_derniere_arrivee.split('-') if num.strip()]
        
        # Convertir en ensembles pour faciliter la comparaison
        derniere_set = set(derniere_numeros)
        avant_derniere_set = set(avant_derniere_numeros)
        
        # Compter les numéros en commun
        communs = len(derniere_set.intersection(avant_derniere_set))
        numeros_communs_liste.append((courses[i]['date_course'], list(derniere_set.intersection(avant_derniere_set))))
        
        dates.append(courses[i]['date_course'])
        numeros_communs.append(communs)
        
        # Calculer la moyenne cumulative
        moyenne_cumulative = sum(numeros_communs) / len(numeros_communs)
        moyennes_cumulatives.append(moyenne_cumulative)
    
    # Tracer la courbe des numéros en commun
    plt.plot(dates, numeros_communs, marker='o', color='blue', label='Numéros en commun')
    
    # Tracer la courbe de la moyenne cumulative
    plt.plot(dates, moyennes_cumulatives, marker='o', color='red', label='Moyenne cumulative')
    
    # Ajouter des labels et une légende
    plt.xlabel('Date de la course')
    plt.ylabel('Nombre de numéros en commun')
    plt.title('Nombre de numéros en commun entre les deux dernières arrivées')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
    plt.legend()  # Afficher la légende
    plt.show()
    plt.close()

    # Afficher la liste des numéros en commun
    print("\n=== Liste des numéros en commun entre chaque course ===")
    for date, numeros in numeros_communs_liste:
        print(f"Date : {date}, Numéros en commun : {', '.join(numeros) if numeros else 'Aucun'}")


def afficher_courbe_arrivees_communes_par_discipline(courses: List[Dict[str, Any]], discipline: str) -> None:
    """
    Affiche une courbe montrant le nombre de numéros en commun entre les deux dernières arrivées pour chaque course,
    filtrée par discipline. Affiche également une liste des numéros en commun.
    :param courses: Liste des courses.
    :param discipline: Discipline à filtrer (par exemple, "Attelé", "Plat", "Haies").
    """
    # Filtrer les courses par discipline
    courses_filtrees = [course for course in courses if course.get('type_course') == discipline]
    
    if len(courses_filtrees) < 2:
        print(f"Pas assez de courses pour la discipline '{discipline}'.")
        return
    
    dates = []
    numeros_communs = []
    moyennes_cumulatives = []
    numeros_communs_liste = []  # Liste pour stocker les numéros en commun
    
    for i in range(1, len(courses_filtrees)):
        derniere_arrivee = courses_filtrees[i]['arrivee'].split('-')
        avant_derniere_arrivee = courses_filtrees[i-1]['arrivee'].split('-')
        
        # Nettoyer les numéros en supprimant les espaces
        derniere_arrivee_set = set([x.strip() for x in derniere_arrivee])
        avant_derniere_arrivee_set = set([x.strip() for x in avant_derniere_arrivee])
        
        # Compter les numéros en commun
        communs = len(derniere_arrivee_set.intersection(avant_derniere_arrivee_set))
        numeros_communs_liste.append((courses_filtrees[i]['date_course'], list(derniere_arrivee_set.intersection(avant_derniere_arrivee_set))))
        
        dates.append(courses_filtrees[i]['date_course'])
        numeros_communs.append(communs)
        
        # Calculer la moyenne cumulative
        moyenne_cumulative = sum(numeros_communs) / len(numeros_communs)
        moyennes_cumulatives.append(moyenne_cumulative)
    
    # Tracer la courbe des numéros en commun
    plt.plot(dates, numeros_communs, marker='o', color='blue', label='Numéros en commun')
    
    # Tracer la courbe de la moyenne cumulative
    plt.plot(dates, moyennes_cumulatives, marker='o', color='red', label='Moyenne cumulative')
    
    # Ajouter des labels et une légende
    plt.xlabel('Date de la course')
    plt.ylabel('Nombre de numéros en commun')
    plt.title(f'Nombre de numéros en commun entre les deux dernières arrivées (Discipline : {discipline})')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
    plt.legend()  # Afficher la légende
    plt.show()
    plt.close()

    # Afficher la liste des numéros en commun
    print(f"\n=== Liste des numéros en commun entre chaque arrivée (Discipline : {discipline}) ===")
    for date, numeros in numeros_communs_liste:
        print(f"Date : {date}, Numéros en commun : {', '.join(numeros) if numeros else 'Aucun'}")

def afficher_courbe_syntheses_communes(courses: List[Dict[str, Any]]) -> None:
    """
    Affiche une courbe montrant le nombre de numéros en commun entre les deux dernières synthèses pour chaque course,
    ainsi que la moyenne cumulative en rouge. Affiche également une liste des numéros en commun.
    :param courses: Liste des courses.
    """
    dates = []
    numeros_communs = []
    moyennes_cumulatives = []
    numeros_communs_liste = []  # Liste pour stocker les numéros en commun
    
    for i in range(1, len(courses)):
        derniere_synthese = courses[i]['synthese'].split('-')
        avant_derniere_synthese = courses[i-1]['synthese'].split('-')
        
        # Nettoyer les numéros en supprimant les suffixes comme 'e'
        derniere_synthese_set = set([x.replace('e', '').strip() for x in derniere_synthese])
        avant_derniere_synthese_set = set([x.replace('e', '').strip() for x in avant_derniere_synthese])
        
        # Compter les numéros en commun
        communs = len(derniere_synthese_set.intersection(avant_derniere_synthese_set))
        numeros_communs_liste.append((courses[i]['date_course'], list(derniere_synthese_set.intersection(avant_derniere_synthese_set))))
        
        dates.append(courses[i]['date_course'])
        numeros_communs.append(communs)
        
        # Calculer la moyenne cumulative
        moyenne_cumulative = sum(numeros_communs) / len(numeros_communs)
        moyennes_cumulatives.append(moyenne_cumulative)
    
    # Tracer la courbe des numéros en commun
    plt.plot(dates, numeros_communs, marker='o', color='blue', label='Numéros en commun')
    
    # Tracer la courbe de la moyenne cumulative
    plt.plot(dates, moyennes_cumulatives, marker='o', color='red', label='Moyenne cumulative')
    
    # Ajouter des labels et une légende
    plt.xlabel('Date de la course')
    plt.ylabel('Nombre de numéros en commun')
    plt.title('Nombre de numéros en commun entre les deux dernières synthèses')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
    plt.legend()  # Afficher la légende
    plt.show()
    plt.close()

    # Afficher la liste des numéros en commun
    print("\n=== Liste des numéros en commun entre chaque synthèse ===")
    for date, numeros in numeros_communs_liste:
        print(f"Date : {date}, Numéros en commun : {', '.join(numeros) if numeros else 'Aucun'}")

def afficher_graphique_tranches_synthese(courses):
    """
    Affiche un graphique en barres empilées montrant la répartition des numéros de la synthèse en trois tranches.
    """
    tranche_1 = []
    tranche_2 = []
    tranche_3 = []
    dates = []

    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

        # Comptage des numéros dans chaque tranche
        tranche_1.append(len([num for num in numeros if 1 <= num <= 5]))
        tranche_2.append(len([num for num in numeros if 6 <= num <= 10]))
        tranche_3.append(len([num for num in numeros if num >= 11]))

        # Ajout de la date pour l'axe X
        dates.append(course['date_course'])

    # Création du graphique en barres empilées
    plt.figure(figsize=(12, 6))
    plt.bar(dates, tranche_1, label='Tranche 1 (1-5)', color='blue')
    plt.bar(dates, tranche_2, bottom=tranche_1, label='Tranche 2 (6-10)', color='orange')
    plt.bar(dates, tranche_3, bottom=[t1 + t2 for t1, t2 in zip(tranche_1, tranche_2)], label='Tranche 3 (11+)', color='green')

    # Ajout des labels et de la légende
    plt.xlabel('Date de la course')
    plt.ylabel('Nombre de numéros')
    plt.title('Répartition des numéros de la synthèse par tranche')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
    plt.tight_layout()  # Ajuster l'espacement
    plt.show()
def afficher_graphique_tranches_synthese_tierce(courses):
    """
    Affiche un graphique en barres empilées montrant la répartition des numéros de la synthèse en trois tranches.
    """
    tranche_1 = []
    tranche_2 = []
    tranche_3 = []
    dates = []

    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]
        # Limiter l'analyse aux trois premiers numéros
        numeros = numeros[:3]
        # Comptage des numéros dans chaque tranche
        tranche_1.append(len([num for num in numeros if 1 <= num <= 5]))
        tranche_2.append(len([num for num in numeros if 6 <= num <= 10]))
        tranche_3.append(len([num for num in numeros if num >= 11]))

        # Ajout de la date pour l'axe X
        dates.append(course['date_course'])

    # Création du graphique en barres empilées
    plt.figure(figsize=(12, 6))
    plt.bar(dates, tranche_1, label='Tranche 1 (1-5)', color='blue')
    plt.bar(dates, tranche_2, bottom=tranche_1, label='Tranche 2 (6-10)', color='orange')
    plt.bar(dates, tranche_3, bottom=[t1 + t2 for t1, t2 in zip(tranche_1, tranche_2)], label='Tranche 3 (11+)', color='green')

    # Ajout des labels et de la légende
    plt.xlabel('Date de la course')
    plt.ylabel('Nombre de numéros')
    plt.title('Répartition des numéros de la synthèse par tranche')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)  # Rotation des dates pour une meilleure lisibilité
    # Définir les graduations de l'axe Y avec une unité de 1
    max_y = max(max(tranche_1), max(tranche_2), max(tranche_3))
    plt.yticks(range(0, max_y + 1, 1))
    plt.tight_layout()  # Ajuster l'espacement
    plt.show()

def analyser_premiers_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des premiers avec visualisation optimisée"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])  # Plus ancien d'abord
    derniers_30 = courses_triées[-30:]  # 30 plus récentes (toujours ordre chrono)
    
    # 1. Camembert global (tous premiers historiques)
    ax1 = plt.subplot(131)
    pairs_historique = 0
    impairs_historique = 0
    
    for course in courses_triées:
        arrivee = course.get('arrivee', '')
        if arrivee:
            premier = arrivee.split('-')[0].strip()
            if premier.isdigit():
                num = int(premier)
                if num % 2 == 0:
                    pairs_historique += 1
                else:
                    impairs_historique += 1
                    
    ax1.pie([pairs_historique, impairs_historique], 
            labels=[f'Pairs\n{pairs_historique}', f'Impairs\n{impairs_historique}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90,
            textprops={'fontsize': 12})
    ax1.set_title("Premiers de toutes les courses\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            premier = arrivee.split('-')[0].strip()
            if premier.isdigit():
                num = int(premier)
                if num % 2 == 0:
                    pairs_30 += 1
                else:
                    impairs_30 += 1
                    
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("Premiers des 30 dernières courses", pad=20)

    # 3. Graphique temporel (ancien en bas)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    valeurs = []
    couleurs = []
    
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            premier = arrivee.split('-')[0].strip()
            if premier.isdigit():
                num = int(premier)
                valeurs.append(num)
                couleurs.append('#1f77b4' if num%2 ==0 else '#ff7f0e')
    
    # Création des barres horizontales (ancien en bas)
    bars = ax3.barh(dates, valeurs, color=couleurs, height=0.8, edgecolor='black')
    
    # Ajout des valeurs
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{width}', 
                ha='left', va='center',
                fontsize=10)
    
    # Configuration axes
    ax3.set_xlabel('Numéro gagnant', fontsize=12)
    ax3.set_title("Évolution chronologique\n(ancien → récent)", pad=20)
    ax3.grid(axis='x', alpha=0.3)
    
    # Légende unifiée
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label=f'Pair ({pairs_30})'),
        Patch(facecolor='#ff7f0e', label=f'Impair ({impairs_30})')
    ]
    ax3.legend(handles=legende, 
               loc='lower center',
               bbox_to_anchor=(0.5, -0.25),
               ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Espace pour légende
    plt.show()

def analyser_deuxieme_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des premiers avec visualisation optimisée"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])  # Plus ancien d'abord
    derniers_30 = courses_triées[-30:]  # 30 plus récentes (toujours ordre chrono)
    
    # 1. Camembert global (tous premiers historiques)
    ax1 = plt.subplot(131)
    pairs_historique = 0
    impairs_historique = 0
    
    for course in courses_triées:
        arrivee = course.get('arrivee', '')
        if arrivee:
            deuxieme = arrivee.split('-')[1].strip()
            if deuxieme.isdigit():
                num = int(deuxieme)
                if num % 2 == 0:
                    pairs_historique += 1
                else:
                    impairs_historique += 1
                    
    ax1.pie([pairs_historique, impairs_historique], 
            labels=[f'Pairs\n{pairs_historique}', f'Impairs\n{impairs_historique}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90,
            textprops={'fontsize': 12})
    ax1.set_title("deuxieme de toutes les courses\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            deuxieme = arrivee.split('-')[1].strip()
            if deuxieme.isdigit():
                num = int(deuxieme)
                if num % 2 == 0:
                    pairs_30 += 1
                else:
                    impairs_30 += 1
                    
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("deuxieme des 30 dernières courses", pad=20)

    # 3. Graphique temporel (ancien en bas)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    valeurs = []
    couleurs = []
    
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            deuxieme = arrivee.split('-')[1].strip()
            if deuxieme.isdigit():
                num = int(deuxieme)
                valeurs.append(num)
                couleurs.append('#1f77b4' if num%2 ==0 else '#ff7f0e')
    
    # Création des barres horizontales (ancien en bas)
    bars = ax3.barh(dates, valeurs, color=couleurs, height=0.8, edgecolor='black')
    
    # Ajout des valeurs
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{width}', 
                ha='left', va='center',
                fontsize=10)
    
    # Configuration axes
    ax3.set_xlabel('Numéro deuxieme', fontsize=12)
    ax3.set_title("Évolution chronologique\n(ancien → récent)", pad=20)
    ax3.grid(axis='x', alpha=0.3)
    
    # Légende unifiée
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label=f'Pair ({pairs_30})'),
        Patch(facecolor='#ff7f0e', label=f'Impair ({impairs_30})')
    ]
    ax3.legend(handles=legende, 
               loc='lower center',
               bbox_to_anchor=(0.5, -0.25),
               ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Espace pour légende
    plt.show()
def analyser_troisieme_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des premiers avec visualisation optimisée"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])  # Plus ancien d'abord
    derniers_30 = courses_triées[-30:]  # 30 plus récentes (toujours ordre chrono)
    
    # 1. Camembert global (tous premiers historiques)
    ax1 = plt.subplot(131)
    pairs_historique = 0
    impairs_historique = 0
    
    for course in courses_triées:
        arrivee = course.get('arrivee', '')
        if arrivee:
            troisieme = arrivee.split('-')[2].strip()
            if troisieme.isdigit():
                num = int(troisieme)
                if num % 2 == 0:
                    pairs_historique += 1
                else:
                    impairs_historique += 1
                    
    ax1.pie([pairs_historique, impairs_historique], 
            labels=[f'Pairs\n{pairs_historique}', f'Impairs\n{impairs_historique}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90,
            textprops={'fontsize': 12})
    ax1.set_title("troisieme de toutes les courses\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            troisieme = arrivee.split('-')[2].strip()
            if troisieme.isdigit():
                num = int(troisieme)
                if num % 2 == 0:
                    pairs_30 += 1
                else:
                    impairs_30 += 1
                    
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("troisieme des 30 dernières courses", pad=20)

    # 3. Graphique temporel (ancien en bas)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    valeurs = []
    couleurs = []
    
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            troisieme = arrivee.split('-')[2].strip()
            if troisieme.isdigit():
                num = int(troisieme)
                valeurs.append(num)
                couleurs.append('#1f77b4' if num%2 ==0 else '#ff7f0e')
    
    # Création des barres horizontales (ancien en bas)
    bars = ax3.barh(dates, valeurs, color=couleurs, height=0.8, edgecolor='black')
    
    # Ajout des valeurs
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{width}', 
                ha='left', va='center',
                fontsize=10)
    
    # Configuration axes
    ax3.set_xlabel('Numéro troisieme', fontsize=12)
    ax3.set_title("Évolution chronologique\n(ancien → récent)", pad=20)
    ax3.grid(axis='x', alpha=0.3)
    
    # Légende unifiée
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label=f'Pair ({pairs_30})'),
        Patch(facecolor='#ff7f0e', label=f'Impair ({impairs_30})')
    ]
    ax3.legend(handles=legende, 
               loc='lower center',
               bbox_to_anchor=(0.5, -0.25),
               ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Espace pour légende
    plt.show()

def analyser_quatrieme_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des premiers avec visualisation optimisée"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])  # Plus ancien d'abord
    derniers_30 = courses_triées[-30:]  # 30 plus récentes (toujours ordre chrono)
    
    # 1. Camembert global (tous premiers historiques)
    ax1 = plt.subplot(131)
    pairs_historique = 0
    impairs_historique = 0
    
    for course in courses_triées:
        arrivee = course.get('arrivee', '')
        if arrivee:
            quatrieme = arrivee.split('-')[3].strip()
            if quatrieme.isdigit():
                num = int(quatrieme)
                if num % 2 == 0:
                    pairs_historique += 1
                else:
                    impairs_historique += 1
                    
    ax1.pie([pairs_historique, impairs_historique], 
            labels=[f'Pairs\n{pairs_historique}', f'Impairs\n{impairs_historique}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90,
            textprops={'fontsize': 12})
    ax1.set_title("quatrieme de toutes les courses\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            quatrieme = arrivee.split('-')[3].strip()
            if quatrieme.isdigit():
                num = int(quatrieme)
                if num % 2 == 0:
                    pairs_30 += 1
                else:
                    impairs_30 += 1
                    
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("quatrieme des 30 dernières courses", pad=20)

    # 3. Graphique temporel (ancien en bas)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    valeurs = []
    couleurs = []
    
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            quatrieme = arrivee.split('-')[3].strip()
            if quatrieme.isdigit():
                num = int(quatrieme)
                valeurs.append(num)
                couleurs.append('#1f77b4' if num%2 ==0 else '#ff7f0e')
    
    # Création des barres horizontales (ancien en bas)
    bars = ax3.barh(dates, valeurs, color=couleurs, height=0.8, edgecolor='black')
    
    # Ajout des valeurs
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{width}', 
                ha='left', va='center',
                fontsize=10)
    
    # Configuration axes
    ax3.set_xlabel('Numéro quatrieme', fontsize=12)
    ax3.set_title("Évolution chronologique\n(ancien → récent)", pad=20)
    ax3.grid(axis='x', alpha=0.3)
    
    # Légende unifiée
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label=f'Pair ({pairs_30})'),
        Patch(facecolor='#ff7f0e', label=f'Impair ({impairs_30})')
    ]
    ax3.legend(handles=legende, 
               loc='lower center',
               bbox_to_anchor=(0.5, -0.25),
               ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Espace pour légende
    plt.show()

def analyser_cinquieme_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des premiers avec visualisation optimisée"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])  # Plus ancien d'abord
    derniers_30 = courses_triées[-30:]  # 30 plus récentes (toujours ordre chrono)
    
    # 1. Camembert global (tous premiers historiques)
    ax1 = plt.subplot(131)
    pairs_historique = 0
    impairs_historique = 0
    
    for course in courses_triées:
        arrivee = course.get('arrivee', '')
        if arrivee:
            cinquieme = arrivee.split('-')[4].strip()
            if cinquieme.isdigit():
                num = int(cinquieme)
                if num % 2 == 0:
                    pairs_historique += 1
                else:
                    impairs_historique += 1
                    
    ax1.pie([pairs_historique, impairs_historique], 
            labels=[f'Pairs\n{pairs_historique}', f'Impairs\n{impairs_historique}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90,
            textprops={'fontsize': 12})
    ax1.set_title("cinquieme de toutes les courses\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            cinquieme = arrivee.split('-')[4].strip()
            if cinquieme.isdigit():
                num = int(cinquieme)
                if num % 2 == 0:
                    pairs_30 += 1
                else:
                    impairs_30 += 1
                    
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("cinquieme des 30 dernières courses", pad=20)

    # 3. Graphique temporel (ancien en bas)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    valeurs = []
    couleurs = []
    
    for course in derniers_30:
        arrivee = course.get('arrivee', '')
        if arrivee:
            cinquieme = arrivee.split('-')[4].strip()
            if cinquieme.isdigit():
                num = int(cinquieme)
                valeurs.append(num)
                couleurs.append('#1f77b4' if num%2 ==0 else '#ff7f0e')
    
    # Création des barres horizontales (ancien en bas)
    bars = ax3.barh(dates, valeurs, color=couleurs, height=0.8, edgecolor='black')
    
    # Ajout des valeurs
    for bar in bars:
        width = bar.get_width()
        ax3.text(width + 0.5, 
                bar.get_y() + bar.get_height()/2, 
                f'{width}', 
                ha='left', va='center',
                fontsize=10)
    
    # Configuration axes
    ax3.set_xlabel('Numéro cinquieme', fontsize=12)
    ax3.set_title("Évolution chronologique\n(ancien → récent)", pad=20)
    ax3.grid(axis='x', alpha=0.3)
    
    # Légende unifiée
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label=f'Pair ({pairs_30})'),
        Patch(facecolor='#ff7f0e', label=f'Impair ({impairs_30})')
    ]
    ax3.legend(handles=legende, 
               loc='lower center',
               bbox_to_anchor=(0.5, -0.25),
               ncol=2,
               fontsize=12)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)  # Espace pour légende
    plt.show()

def analyser_tierce_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des paires/impairs dans les tiercés avec visualisation"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])
    derniers_30 = courses_triées[-30:]  # 30 dernières courses

    # 1. Camembert global (toutes les courses)
    ax1 = plt.subplot(131)
    pairs_total = 0
    impairs_total = 0
    
    for course in courses_triées:
        arrivees = list(map(int, course.get('arrivee', '').split('-')[:3]))  # 3 premiers
        for num in arrivees:
            if num % 2 == 0: 
                pairs_total += 1
            else:
                impairs_total += 1
                
    ax1.pie([pairs_total, impairs_total], 
            labels=[f'Pairs\n{pairs_total}', f'Impairs\n{impairs_total}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax1.set_title("Répartition dans tous les tiercés\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers tiercés
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    
    for course in derniers_30:
        arrivees = list(map(int, course.get('arrivee', '').split('-')[:3]))
        for num in arrivees:
            if num % 2 == 0: 
                pairs_30 += 1
            else:
                impairs_30 += 1
                
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("Répartition dans les 30 derniers tiercés", pad=20)

    # 3. Évolution temporelle (annotation unifiée)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    pairs_counts = []
    impairs_counts = []

    for course in derniers_30:
        arrivees = list(map(int, course.get('arrivee', '').split('-')[:3]))
        pairs = sum(1 for num in arrivees if num % 2 == 0)
        impairs = len(arrivees) - pairs
        pairs_counts.append(pairs)
        impairs_counts.append(impairs)

    # Graphique en barres empilées
    bars_pairs = ax3.barh(dates, pairs_counts, color='#1f77b4', edgecolor='black', height=0.8)
    bars_impairs = ax3.barh(dates, impairs_counts, left=pairs_counts, color='#ff7f0e', edgecolor='black', height=0.8)

    # Annotation unifiée au centre
    for i, (date, p, ip) in enumerate(zip(dates, pairs_counts, impairs_counts)):
        total = p + ip
        ax3.text(
            total / 2,  # Position horizontale centrée
            i,          # Position verticale alignée à la barre
            f"{p}/{ip}", 
            va='center', 
            ha='center',
            color='white',
            fontsize=9,
            fontweight='bold',
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]  # Contour noir
        )

    # Configuration
    ax3.set_xlim(0, 3)  # Maximum 3 numéros par course
    ax3.set_xticks([0, 1, 2, 3])
    ax3.set_xlabel('Nombre total de numéros')
    ax3.set_title("Répartition par course\n(format: pairs/impairs)", pad=20)

    # Légende
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label='Pairs'),
        Patch(facecolor='#ff7f0e', label='Impairs')
    ]
    ax3.legend(handles=legende, loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=2)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    plt.show()
def analyser_quinte_paire_impaire(courses: List[Dict[str, Any]]):
    """Analyse des paires/impairs dans les tiercés avec visualisation"""
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(18, 6))
    
    # Tri des données
    courses_triées = sorted(courses, key=lambda x: x['date_course'])
    derniers_30 = courses_triées[-30:]  # 30 dernières courses

    # 1. Camembert global (toutes les courses)
    ax1 = plt.subplot(131)
    pairs_total = 0
    impairs_total = 0
    
    for course in courses_triées:
        arrivees = list(map(int, course.get('arrivee', '').split('-')[:5]))  # 3 premiers
        for num in arrivees:
            if num % 2 == 0: 
                pairs_total += 1
            else:
                impairs_total += 1
                
    ax1.pie([pairs_total, impairs_total], 
            labels=[f'Pairs\n{pairs_total}', f'Impairs\n{impairs_total}'],
            colors=['#1f77b4', '#ff7f0e'],
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax1.set_title("Répartition dans tous les tiercés\n(historique complet)", pad=20)

    # 2. Camembert des 30 derniers tiercés
    ax2 = plt.subplot(132)
    pairs_30 = 0
    impairs_30 = 0
    
    for course in derniers_30:
        arrivees = list(map(int, course.get('arrivee', '').split('-')[:5]))
        for num in arrivees:
            if num % 2 == 0: 
                pairs_30 += 1
            else:
                impairs_30 += 1
                
    ax2.pie([pairs_30, impairs_30],
            labels=[f'Pairs\n{pairs_30}', f'Impairs\n{impairs_30}'],
            colors=['#1f77b4', '#ff7f0e'], 
            autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
            startangle=90)
    ax2.set_title("Répartition dans les 30 derniers tiercés", pad=20)

    # 3. Évolution temporelle (annotation unifiée)
    ax3 = plt.subplot(133)
    dates = [datetime.strptime(c['date_course'], "%Y-%m-%d").strftime("%d/%m/%Y") for c in derniers_30]
    pairs_counts = []
    impairs_counts = []

    for course in derniers_30:
        arrivees = list(map(int, course.get('arrivee', '').split('-')[:5]))
        pairs = sum(1 for num in arrivees if num % 2 == 0)
        impairs = len(arrivees) - pairs
        pairs_counts.append(pairs)
        impairs_counts.append(impairs)

    # Graphique en barres empilées
    bars_pairs = ax3.barh(dates, pairs_counts, color='#1f77b4', edgecolor='black', height=0.8)
    bars_impairs = ax3.barh(dates, impairs_counts, left=pairs_counts, color='#ff7f0e', edgecolor='black', height=0.8)

    # Annotation unifiée au centre
    for i, (date, p, ip) in enumerate(zip(dates, pairs_counts, impairs_counts)):
        total = p + ip
        ax3.text(
            total / 2,  # Position horizontale centrée
            i,          # Position verticale alignée à la barre
            f"{p}/{ip}", 
            va='center', 
            ha='center',
            color='white',
            fontsize=9,
            fontweight='bold',
            path_effects=[pe.withStroke(linewidth=2, foreground="black")]  # Contour noir
        )

    # Configuration
    ax3.set_xlim(0, 5)  # Maximum 3 numéros par course
    ax3.set_xticks([0, 1, 2, 3, 4, 5])
    ax3.set_xlabel('Nombre total de numéros')
    ax3.set_title("Répartition par course\n(format: pairs/impairs)", pad=20)

    # Légende
    from matplotlib.patches import Patch
    legende = [
        Patch(facecolor='#1f77b4', label='Pairs'),
        Patch(facecolor='#ff7f0e', label='Impairs')
    ]
    ax3.legend(handles=legende, loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=2)
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.2)
    plt.show()
def analyser_paire_impaire_par_tranche_synthese(courses: List[Dict[str, Any]]):
    """
    Analyse la répartition pair/impair des premiers de l'arrivée, classés par tranche selon la synthèse.
    Ajoute l'affichage des écarts actuels et maximums pour chaque catégorie, ainsi que le nombre de courses dans chaque colonne.
    """
    from collections import defaultdict
    import matplotlib.pyplot as plt
    import numpy as np
    from datetime import datetime

    # Tri chronologique des courses
    courses_triees = sorted(courses, key=lambda x: x['date_course'])
    total_courses = len(courses_triees)

    stats = defaultdict(lambda: {
        'Pair': {'count': 0, 'dernier_index': -1, 'ecart_max': 0, 'ecart_actuel': 0},
        'Impair': {'count': 0, 'dernier_index': -1, 'ecart_max': 0, 'ecart_actuel': 0}
    })

    for index, course in enumerate(courses_triees):
        # Extraction des données
        arrivee = course.get('arrivee', '').split('-')
        premier_arrivee = int(arrivee[0].strip()) if arrivee and arrivee[0].strip().isdigit() else None
        synthese = course.get('synthese', '').split('-')
        
        try:
            premier_synthese = int(synthese[0].strip().replace('e', ''))
        except (IndexError, ValueError, AttributeError):
            continue

        # Détermination de la tranche
        if 1 <= premier_synthese <= 2:
            tranche = '1-2'
        elif 3 <= premier_synthese <= 5:
            tranche = '3-5'
        elif 6 <= premier_synthese <= 10:
            tranche = '6-10'
        else:
            tranche = '11+'

        if premier_arrivee is None:
            continue

        parite = 'Pair' if premier_arrivee % 2 == 0 else 'Impair'
        stats[tranche][parite]['count'] += 1
        
        # Calcul des écarts
        dernier_index = stats[tranche][parite]['dernier_index']
        if dernier_index != -1:
            ecart = index - dernier_index
            if ecart > stats[tranche][parite]['ecart_max']:
                stats[tranche][parite]['ecart_max'] = ecart
        stats[tranche][parite]['dernier_index'] = index

    # Calcul final des écarts actuels
    for tranche in stats:
        for parite in ['Pair', 'Impair']:
            dernier_index = stats[tranche][parite]['dernier_index']
            stats[tranche][parite]['ecart_actuel'] = total_courses - dernier_index - 1 if dernier_index != -1 else total_courses
            if stats[tranche][parite]['ecart_max'] == 0 and stats[tranche][parite]['count'] > 0:
                stats[tranche][parite]['ecart_max'] = stats[tranche][parite]['ecart_actuel']

    # Préparation des données pour visualisation
    tranches = ['1-2', '3-5', '6-10', '11+']
    pair_counts = [stats[t]['Pair']['count'] for t in tranches]
    impair_counts = [stats[t]['Impair']['count'] for t in tranches]
    pair_ecarts = [f"Actuel: {stats[t]['Pair']['ecart_actuel']}\nMax: {stats[t]['Pair']['ecart_max']}" for t in tranches]
    impair_ecarts = [f"Actuel: {stats[t]['Impair']['ecart_actuel']}\nMax: {stats[t]['Impair']['ecart_max']}" for t in tranches]

    # Création du graphique
    fig, ax = plt.subplots(figsize=(12, 8))
    x = np.arange(len(tranches))
    width = 0.35

    # Barres pour les pairs
    bars_pair = ax.bar(x - width/2, pair_counts, width, label='Pair', color='skyblue')
    # Barres pour les impairs
    bars_impair = ax.bar(x + width/2, impair_counts, width, label='Impair', color='salmon')

    # Ajout des annotations avec le nombre de courses ET les écarts pour chaque barre
    for bars, ecarts in zip([bars_pair, bars_impair], [pair_ecarts, impair_ecarts]):
        for bar, ecart in zip(bars, ecarts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                    f"{int(height)}\n{ecart}",
                    ha='center', va='bottom',
                    fontsize=8,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    # Configuration du graphique
    ax.set_title("Répartition pair/impair par tranche avec écarts", pad=20)
    ax.set_ylabel("Nombre de courses")
    ax.set_xticks(x)
    ax.set_xticklabels(tranches)
    ax.legend()

    # Sous-titre informatif
    plt.suptitle(
        f"Analyse sur {total_courses} courses | Du {courses_triees[0]['date_course']} au {courses_triees[-1]['date_course']}",
        y=0.92,
        fontsize=10
    )

    plt.tight_layout()
    plt.show()


def calculer_ecarts_premiers_synthese(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """Version améliorée avec gestion complète des numéros"""
    ecarts = defaultdict(lambda: {'derniere_occurrence': -1, 
                                 'ecart_actuel': 0, 
                                 'ecart_max': 0,
                                 'occurrences': []})
    
    courses_valides = sorted(
        [c for c in courses 
         if c.get('date_course') and c.get('synthese')],
        key=lambda x: x['date_course']
    )

    for idx, course in enumerate(courses_valides):
        try:
            # Extraction et nettoyage du premier élément
            premier = course['synthese'].split('-')[0].strip().lower()
            num = int(''.join(filter(str.isdigit, premier)))  # Conversion robuste
            
            # Mise à jour des statistiques
            if ecarts[num]['derniere_occurrence'] != -1:
                ecart = idx - ecarts[num]['derniere_occurrence'] - 1
                ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecart)
            
            ecarts[num]['derniere_occurrence'] = idx
            ecarts[num]['occurrences'].append(course['date_course'])
            
        except (ValueError, IndexError, KeyError):
            continue

    # Calcul final pour tous les numéros
    total_courses = len(courses_valides)
    for num in ecarts:
        derniere_occ = ecarts[num]['derniere_occurrence']
        
        ecarts[num]['ecart_actuel'] = total_courses - derniere_occ - 1 if derniere_occ != -1 else total_courses
        ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecarts[num]['ecart_actuel'])
        
        # Ajout des données historiques complètes
        ecarts[num]['total_occurrences'] = len(ecarts[num]['occurrences'])
        ecarts[num]['frequence'] = len(ecarts[num]['occurrences']) / total_courses * 100 if total_courses > 0 else 0

    return dict(ecarts)

def calculer_ecarts_deuxiemes_synthese(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """Version améliorée avec gestion complète des numéros"""
    ecarts = defaultdict(lambda: {'derniere_occurrence': -1, 
                                 'ecart_actuel': 0, 
                                 'ecart_max': 0,
                                 'occurrences': []})
    
    courses_valides = sorted(
        [c for c in courses 
         if c.get('date_course') and c.get('synthese')],
        key=lambda x: x['date_course']
    )

    for idx, course in enumerate(courses_valides):
        try:
            # Extraction et nettoyage du deuxieme élément
            deuxieme = course['synthese'].split('-')[1].strip().lower()
            num = int(''.join(filter(str.isdigit, deuxieme)))  # Conversion robuste
            
            # Mise à jour des statistiques
            if ecarts[num]['derniere_occurrence'] != -1:
                ecart = idx - ecarts[num]['derniere_occurrence'] - 1
                ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecart)
            
            ecarts[num]['derniere_occurrence'] = idx
            ecarts[num]['occurrences'].append(course['date_course'])
            
        except (ValueError, IndexError, KeyError):
            continue

    # Calcul final pour tous les numéros
    total_courses = len(courses_valides)
    for num in ecarts:
        derniere_occ = ecarts[num]['derniere_occurrence']
        
        ecarts[num]['ecart_actuel'] = total_courses - derniere_occ - 1 if derniere_occ != -1 else total_courses
        ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecarts[num]['ecart_actuel'])
        
        # Ajout des données historiques complètes
        ecarts[num]['total_occurrences'] = len(ecarts[num]['occurrences'])
        ecarts[num]['frequence'] = len(ecarts[num]['occurrences']) / total_courses * 100 if total_courses > 0 else 0

    return dict(ecarts)

def calculer_ecarts_troisiemes_synthese(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """Version améliorée avec gestion complète des numéros"""
    ecarts = defaultdict(lambda: {'derniere_occurrence': -1, 
                                 'ecart_actuel': 0, 
                                 'ecart_max': 0,
                                 'occurrences': []})
    
    courses_valides = sorted(
        [c for c in courses 
         if c.get('date_course') and c.get('synthese')],
        key=lambda x: x['date_course']
    )

    for idx, course in enumerate(courses_valides):
        try:
            # Extraction et nettoyage du deuxieme élément
            troisieme = course['synthese'].split('-')[2].strip().lower()
            num = int(''.join(filter(str.isdigit, troisieme)))  # Conversion robuste
            
            # Mise à jour des statistiques
            if ecarts[num]['derniere_occurrence'] != -1:
                ecart = idx - ecarts[num]['derniere_occurrence'] - 1
                ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecart)
            
            ecarts[num]['derniere_occurrence'] = idx
            ecarts[num]['occurrences'].append(course['date_course'])
            
        except (ValueError, IndexError, KeyError):
            continue

    # Calcul final pour tous les numéros
    total_courses = len(courses_valides)
    for num in ecarts:
        derniere_occ = ecarts[num]['derniere_occurrence']
        
        ecarts[num]['ecart_actuel'] = total_courses - derniere_occ - 1 if derniere_occ != -1 else total_courses
        ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecarts[num]['ecart_actuel'])
        
        # Ajout des données historiques complètes
        ecarts[num]['total_occurrences'] = len(ecarts[num]['occurrences'])
        ecarts[num]['frequence'] = len(ecarts[num]['occurrences']) / total_courses * 100 if total_courses > 0 else 0

    return dict(ecarts)

def calculer_ecarts_quatriemes_synthese(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """Version améliorée avec gestion complète des numéros"""
    ecarts = defaultdict(lambda: {'derniere_occurrence': -1, 
                                 'ecart_actuel': 0, 
                                 'ecart_max': 0,
                                 'occurrences': []})
    
    courses_valides = sorted(
        [c for c in courses 
         if c.get('date_course') and c.get('synthese')],
        key=lambda x: x['date_course']
    )

    for idx, course in enumerate(courses_valides):
        try:
            # Extraction et nettoyage du deuxieme élément
            quatrieme = course['synthese'].split('-')[3].strip().lower()
            num = int(''.join(filter(str.isdigit, quatrieme)))  # Conversion robuste
            
            # Mise à jour des statistiques
            if ecarts[num]['derniere_occurrence'] != -1:
                ecart = idx - ecarts[num]['derniere_occurrence'] - 1
                ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecart)
            
            ecarts[num]['derniere_occurrence'] = idx
            ecarts[num]['occurrences'].append(course['date_course'])
            
        except (ValueError, IndexError, KeyError):
            continue

    # Calcul final pour tous les numéros
    total_courses = len(courses_valides)
    for num in ecarts:
        derniere_occ = ecarts[num]['derniere_occurrence']
        
        ecarts[num]['ecart_actuel'] = total_courses - derniere_occ - 1 if derniere_occ != -1 else total_courses
        ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecarts[num]['ecart_actuel'])
        
        # Ajout des données historiques complètes
        ecarts[num]['total_occurrences'] = len(ecarts[num]['occurrences'])
        ecarts[num]['frequence'] = len(ecarts[num]['occurrences']) / total_courses * 100 if total_courses > 0 else 0

    return dict(ecarts)

def calculer_ecarts_cinquiemes_synthese(courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
    """Version améliorée avec gestion complète des numéros"""
    ecarts = defaultdict(lambda: {'derniere_occurrence': -1, 
                                 'ecart_actuel': 0, 
                                 'ecart_max': 0,
                                 'occurrences': []})
    
    courses_valides = sorted(
        [c for c in courses 
         if c.get('date_course') and c.get('synthese')],
        key=lambda x: x['date_course']
    )

    for idx, course in enumerate(courses_valides):
        try:
            # Extraction et nettoyage du deuxieme élément
            cinquiemes = course['synthese'].split('-')[4].strip().lower()
            num = int(''.join(filter(str.isdigit, cinquiemes)))  # Conversion robuste
            
            # Mise à jour des statistiques
            if ecarts[num]['derniere_occurrence'] != -1:
                ecart = idx - ecarts[num]['derniere_occurrence'] - 1
                ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecart)
            
            ecarts[num]['derniere_occurrence'] = idx
            ecarts[num]['occurrences'].append(course['date_course'])
            
        except (ValueError, IndexError, KeyError):
            continue

    # Calcul final pour tous les numéros
    total_courses = len(courses_valides)
    for num in ecarts:
        derniere_occ = ecarts[num]['derniere_occurrence']
        
        ecarts[num]['ecart_actuel'] = total_courses - derniere_occ - 1 if derniere_occ != -1 else total_courses
        ecarts[num]['ecart_max'] = max(ecarts[num]['ecart_max'], ecarts[num]['ecart_actuel'])
        
        # Ajout des données historiques complètes
        ecarts[num]['total_occurrences'] = len(ecarts[num]['occurrences'])
        ecarts[num]['frequence'] = len(ecarts[num]['occurrences']) / total_courses * 100 if total_courses > 0 else 0

    return dict(ecarts)

def analyse_ecart_position_generique(courses, numero, position):
    """
    Analyse complète des écarts avec gestion de l'historique complet
    Version 2.0 - Prend en compte écart initial et actuel dans les stats
    """
    apparitions = []
    gaps = []
    first_index = None
    last_index = None
    total_courses = len(courses)

    for idx, course in enumerate(courses):
        try:
            # Extraction et validation de la position
            synthese = course.get('synthese', '')
            parts = synthese.split('-')
            
            if len(parts) <= position:
                continue
                
            # Nettoyage et conversion du numéro
            num_str = parts[position].strip().lower().rstrip('e')
            if not num_str.isdigit():
                continue
                
            current_num = int(num_str)
            
            if current_num == numero:
                # Première apparition
                if first_index is None:
                    first_index = idx
                    gaps.append(idx)  # Écart depuis le début
                
                # Calcul écart depuis dernière apparition
                if last_index is not None:
                    gaps.append(idx - last_index - 1)
                
                last_index = idx
                
                # Enregistrement des données
                apparitions.append({
                    'date': course['date_course'],
                    'course_id': idx + 1,
                    'depuis_derniere': idx - last_index - 1 if last_index != idx else None
                })

        except Exception as e:
            print(f"Erreur course {idx} : {str(e)}")
            continue

    # Calcul écart actuel
    ecart_actuel = total_courses - last_index - 1 if last_index is not None else total_courses
    if last_index is not None:
        gaps.append(ecart_actuel)

    # Validation des données
    if not apparitions:
        print(f"\n⚠️ Le numéro {numero} n'est jamais apparu en position {position + 1}")
        return None

    # Calcul des statistiques
    stats = {
        'numero': numero,
        'position': ['premier', 'deuxième', 'troisieme'][position],
        'total_apparitions': len(apparitions),
        'ecarts': Counter(gaps),
        'apparitions': apparitions,
        'ecart_initial': first_index if first_index is not None else 0,
        'ecart_actuel': ecart_actuel,
        'ecart_moyen_complet': sum(gaps)/len(gaps) if gaps else 0,
        'ecart_moyen_interne': sum(gaps[1:-1])/len(gaps[1:-1]) if len(gaps) > 2 else 0,
        'ecart_max': max(gaps) if gaps else 0,
        'ecart_min': min(gaps) if gaps else 0
    }

    # Affichage détaillé
    print(f"\n=== NUMÉRO {numero} EN {stats['position'].upper()} ===")
    print(f"Apparu {stats['total_apparitions']} fois sur {total_courses} courses analysées")
    print(f"Écart initial : {stats['ecart_initial']} courses")
    print(f"Écart actuel : {stats['ecart_actuel']} courses")
    print(f"Écart moyen complet : {stats['ecart_moyen_complet']:.1f} courses")
    print(f"Écart moyen entre apparitions : {stats['ecart_moyen_interne']:.1f} courses")
    print("\nDétail des écarts (courses entre chaque apparition) :")
    
    for ecart, count in sorted(stats['ecarts'].items()):
        prefix = ""
        if ecart == stats['ecart_initial']:
            prefix = "[INITIAL] "
        elif ecart == stats['ecart_actuel']:
            prefix = "[ACTUEL] "
        print(f"- {prefix}{ecart} courses : {count} occurrence{'s' if count > 1 else ''}")
    
    print("\nHistorique chronologique complet :")
    for app in stats['apparitions']:
        date_obj = datetime.strptime(app['date'], "%Y-%m-%d")
        print(f"- Course n°{app['course_id']} ({date_obj.strftime('%d/%m/%Y')})")

    return stats

def analyse_ecart_positions_combinees(courses, numero, positions):
    """
    Analyse combinée des écarts pour plusieurs positions avec affichage détaillé.
    """
    apparitions = []
    gaps = []
    first_index = None
    last_index = None
    total_courses = len(courses)

    for idx, course in enumerate(courses):
        try:
            # Extraction et validation de la position
            synthese = course.get('synthese', '')
            parts = synthese.split('-')

            # Vérifier chaque position
            for position in positions:
                if len(parts) <= position:
                    continue

                # Nettoyage et conversion du numéro
                num_str = parts[position].strip().lower().rstrip('e')
                if not num_str.isdigit():
                    continue

                current_num = int(num_str)

                if current_num == numero:
                    # Première apparition
                    if first_index is None:
                        first_index = idx
                        gaps.append(idx)  # Écart depuis le début

                    # Calcul écart depuis dernière apparition
                    if last_index is not None:
                        gaps.append(idx - last_index - 1)

                    last_index = idx

                    # Enregistrement des données
                    apparitions.append({
                        'date': course['date_course'],
                        'course_id': idx + 1,
                        'depuis_derniere': idx - last_index - 1 if last_index != idx else None
                    })
                    break  # Passer à la course suivante après avoir trouvé le numéro

        except Exception as e:
            print(f"Erreur course {idx} : {str(e)}")
            continue

    # Calcul écart actuel
    ecart_actuel = total_courses - last_index - 1 if last_index is not None else total_courses
    if last_index is not None:
        gaps.append(ecart_actuel)

    # Validation des données
    if not apparitions:
        print(f"\n⚠️ Le numéro {numero} n'est jamais apparu dans les positions {positions}")
        return None

    # Calcul des statistiques
    stats = {
        'numero': numero,
        'positions': positions,
        'total_apparitions': len(apparitions),
        'ecarts': Counter(gaps),
        'apparitions': apparitions,
        'ecart_initial': first_index if first_index is not None else 0,
        'ecart_actuel': ecart_actuel,
        'ecart_moyen_complet': sum(gaps)/len(gaps) if gaps else 0,
        'ecart_moyen_interne': sum(gaps[1:-1])/len(gaps[1:-1]) if len(gaps) > 2 else 0,
        'ecart_max': max(gaps) if gaps else 0,
        'ecart_min': min(gaps) if gaps else 0
    }

    # Affichage détaillé
    print(f"\n=== NUMÉRO {numero} EN positions {' ou '.join([str(p+1) for p in positions])} ===")
    print(f"Apparu {stats['total_apparitions']} fois sur {total_courses} courses analysées")
    print(f"Écart initial : {stats['ecart_initial']} courses")
    print(f"Écart actuel : {stats['ecart_actuel']} courses")
    print(f"Écart moyen complet : {stats['ecart_moyen_complet']:.1f} courses")
    print(f"Écart moyen entre apparitions : {stats['ecart_moyen_interne']:.1f} courses")
    print("\nDétail des écarts (courses entre chaque apparition) :")

    for ecart, count in sorted(stats['ecarts'].items()):
        prefix = ""
        if ecart == stats['ecart_initial']:
            prefix = "[INITIAL] "
        elif ecart == stats['ecart_actuel']:
            prefix = "[ACTUEL] "
        print(f"- {prefix}{ecart} courses : {count} occurrence{'s' if count > 1 else ''}")

    print("\nHistorique chronologique complet :")
    for app in stats['apparitions']:
        date_obj = datetime.strptime(app['date'], "%Y-%m-%d")
        print(f"- Course n°{app['course_id']} ({date_obj.strftime('%d/%m/%Y')})")

    return stats

def analyse_ecart_finissant_premier(courses, numero):
    """
    Analyse des écarts pour les numéros finissant premiers.
    
    :param courses: Liste des courses
    :return: Dictionnaire des écarts et leurs fréquences
    """
    return analyse_ecart_position_generique(courses, numero, position=0)

def analyse_ecart_finissant_deuxieme(courses, numero):
    """
    Analyse des écarts pour les numéros finissant deuxièmes.
    
    :param courses: Liste des courses
    :return: Dictionnaire des écarts et leurs fréquences
    """
    return analyse_ecart_position_generique(courses, numero, position=1)

def analyse_ecart_finissant_troisieme(courses, numero):
    """
    Analyse des écarts pour les numéros finissant deuxièmes.
    
    :param courses: Liste des courses
    :return: Dictionnaire des écarts et leurs fréquences
    """
    return analyse_ecart_position_generique(courses, numero, position=2)