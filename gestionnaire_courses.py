# gestionnaire_courses.py
import os
import sqlite3
import pandas as pd
import logging
import itertools
import matplotlib.pyplot as plt
import csv
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from itertools import combinations
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from database import Database
from file_parser import parse_file
from collections import defaultdict
from prediction import preparer_donnees, entrainer_modele, afficher_graphique_precision
from analyse import (
    analyse_positions,
    analyse_all_pairs,
    analyse_frequence_synthese,
    analyser_couples_synthese,
    analyser_triples_synthese,
    analyser_ecarts_synthese,
    calculer_ecarts_numeros,
    calculer_ecarts_combinaisons,
    afficher_graphique_frequence,
    afficher_graphique_ecarts,
    afficher_graphique_frequence_numeros,
    afficher_graphique_frequence_couples,
    afficher_graphique_frequence_triples,analyse_frequence_arrivee,
    analyser_couples_arrivee,
    analyser_triples_arrivee,
    analyser_ecarts_arrivee,
    calculer_ecarts_numeros_arrivee, calculer_ecarts_couples_arrivee, calculer_ecarts_triples_arrivee, analyser_par_discipline_et_distance_arrivee, analyse_positions_arrivee, extraire_partants, analyser_numero_synthese,calculer_ecarts_premiers_synthese, calculer_ecarts_deuxiemes_synthese, calculer_ecarts_troisiemes_synthese, calculer_ecarts_quatriemes_synthese, calculer_ecarts_cinquiemes_synthese, analyse_ecart_finissant_premier, analyse_ecart_finissant_deuxieme, analyse_ecart_finissant_troisieme 
)
from ml_predictions import preparer_donnees_ml

logging.basicConfig(level=logging.DEBUG)  # Active les logs de débogage
DATE_ACTUELLE_SIMULEE = datetime(2025, 2, 10)
DATE_ACTUELLE_SIMULEE += timedelta(days=1)  # Après chaque journée de courses

class GestionnaireCourses:
    
    def __init__(self, dossier_notes: str, db: Database):  # <-- Accepter une instance de Database
        self.dossier_notes = Path(dossier_notes)
        self.db = db  # Utiliser l'instance de Database passée en paramètre

    def scanner_nouveaux_fichiers(self) -> List[str]:
        """Scanne le dossier pour trouver les nouveaux fichiers non traités."""
        fichiers_existants = [f.name for f in self.dossier_notes.glob('*.txt')]
        fichiers_traites = self.db.get_processed_files()
        return [f for f in fichiers_existants if f not in fichiers_traites]

    def traiter_fichiers(self) -> None:
        """Traite tous les nouveaux fichiers et sauvegarde les données dans la base."""
        nouveaux_fichiers = self.scanner_nouveaux_fichiers()
        for fichier in nouveaux_fichiers:
            donnees = parse_file(self.dossier_notes / fichier)
            if donnees:
                self.db.save_course(fichier, donnees)
                print(f"Fichier {fichier} traité avec succès.")
            else:
                print(f"Erreur lors du traitement de {fichier}.")

    def afficher_frequence_arrivee(self, type_course: Optional[str] = None) -> None:
        """
        Affiche la fréquence des numéros dans l'arrivée, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        """
        courses = self.db.get_courses(type_course=type_course)
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence = analyse_frequence_arrivee(courses)
        print(f"\n=== Fréquence des numéros dans l'arrivée ===")
        for num in sorted(frequence.keys()):
            print(f"Numéro {num} : {frequence[num]:.1f}%")
        
        afficher_graphique_frequence_numeros(frequence)

    def afficher_frequence_couples_arrivee(self, type_course: Optional[str] = None) -> None:
        """
        Affiche la fréquence des couples de numéros dans l'arrivée, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        """
        courses = self.db.get_courses(type_course=type_course)
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence_couples = analyser_couples_arrivee(courses)
        print(f"\n=== Fréquence des couples de numéros dans l'arrivée ===")
        for couple, freq in sorted(frequence_couples.items(), key=lambda x: x[1], reverse=True):
            print(f"Couple {couple} : {freq:.1f}%")
        
        afficher_graphique_frequence_couples(frequence_couples)

    def afficher_frequence_triples_arrivee(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche la fréquence des triples de numéros dans l'arrivée, avec des filtres optionnels.
        """
        courses = self.db.get_courses()
        
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence_triples = analyser_triples_arrivee(courses)
        print(f"\n=== Fréquence des triples de numéros dans l'arrivée ===")
        for triple, freq in sorted(frequence_triples.items(), key=lambda x: x[1], reverse=True): # tous
            print(f"Triple {triple} : {freq:.1f}%")
        
        afficher_graphique_frequence_triples(frequence_triples)

    def afficher_frequence_ecarts_arrivee(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche la fréquence des écarts entre les numéros dans l'arrivée, avec des filtres optionnels.
        """
        courses = self.db.get_courses()
        
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence_ecarts = analyser_ecarts_arrivee(courses)
        print(f"\n=== Fréquence des écarts entre les numéros dans l'arrivée ===")
        for ecart, freq in sorted(frequence_ecarts.items(), key=lambda x: x[1], reverse=True):
            print(f"Écart de {ecart} : {freq:.1f}%")
        
        afficher_graphique_ecarts(frequence_ecarts)

    def afficher_ecarts_numeros_arrivee(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche l'écart et l'écart maximum pour chaque numéro dans l'arrivée, avec des filtres optionnels.
        """
        courses = self.db.get_courses()
        
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_numeros = calculer_ecarts_numeros_arrivee(courses)
        print("\n=== Écarts pour chaque numéro dans l'arrivée ===")
        for num in sorted(ecarts_numeros.keys()):
            print(f"Numéro {num} : Écart actuel = {ecarts_numeros[num]['ecart_actuel']}, Écart max = {ecarts_numeros[num]['ecart_max']}")


    def analyser_positions(self, pos1: int, pos2: int) -> Dict[str, Any]:
        """
        Analyse les positions dans la synthèse (wrapper pour analyse_positions du module analyse)
        """
        courses = self.db.get_courses()
        return analyse_positions(courses, pos1, pos2)

    def analyser_positions_arrivee(self, num1: int, num2: int, type_course: Optional[str] = None, 
                               date_debut: Optional[str] = None, date_fin: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse les numéros dans l'arrivée pour les numéros donnés (num1 et num2).
        """
        courses = self.db.get_courses(type_course, date_debut, date_fin)

        if not courses:
            return {"erreur": "Aucune donnée disponible pour les critères sélectionnés."}

        # Initialisation des compteurs
        num1_dans_arrivee = 0
        num2_dans_arrivee = 0
        double_reussite = 0
        num1_participations = 0
        num2_participations = 0
        courses_en_commun = 0  # Nombre de courses où les deux numéros ont participé ensemble
        courses_double_reussite = []

        total_courses = len(courses)

        for course in courses:
            arrivee = course.get('arrivee', '')
            arrivee_list = [x.strip() for x in arrivee.split('-') if x.strip()]
            
            # Extraction des partants
            partants_str = course.get('partants', '')
            partants = set(map(int, partants_str.split(','))) if partants_str else set()

            # Vérification des participations basées sur les partants
            if num1 in partants:
                num1_participations += 1
            if num2 in partants:
                num2_participations += 1
            if num1 in partants and num2 in partants:
                courses_en_commun += 1  # Les deux numéros ont participé à cette course

            # Vérification des numéros dans l'arrivée
            if str(num1) in arrivee_list:
                num1_dans_arrivee += 1
            if str(num2) in arrivee_list:
                num2_dans_arrivee += 1
            if str(num1) in arrivee_list and str(num2) in arrivee_list:
                double_reussite += 1
                courses_double_reussite.append(course.get('date_course', 'Date inconnue'))

        # Calcul des pourcentages
        num1_reussite = (num1_dans_arrivee / total_courses) * 100 if total_courses > 0 else 0
        num2_reussite = (num2_dans_arrivee / total_courses) * 100 if total_courses > 0 else 0
        double_reussite_pct = (double_reussite / total_courses) * 100 if total_courses > 0 else 0

        # Calcul des taux de réussite basés sur les participations
        num1_reussite_participations = (num1_dans_arrivee / num1_participations) * 100 if num1_participations > 0 else 0
        num2_reussite_participations = (num2_dans_arrivee / num2_participations) * 100 if num2_participations > 0 else 0

        # Calcul du pourcentage de double réussite par rapport aux courses en commun
        double_reussite_pct_commun = (double_reussite / courses_en_commun) * 100 if courses_en_commun > 0 else 0

        # Affichage des résultats
        print("\n=== Résultats de l'analyse des numéros dans l'arrivée ===")
        print(f"Numéro {num1} dans l'arrivée : {num1_reussite:.1f}% de réussite ({num1_dans_arrivee}/{total_courses})")
        print(f"Numéro {num2} dans l'arrivée : {num2_reussite:.1f}% de réussite ({num2_dans_arrivee}/{total_courses})")
        print(f"Double réussite : {double_reussite_pct:.1f}% des courses ({double_reussite}/{total_courses})")

        print("\n=== Résultats basés sur les participations ===")
        print(f"Numéro {num1} a participé à {num1_participations} courses et a réussi {num1_dans_arrivee} fois : {num1_reussite_participations:.1f}%")
        print(f"Numéro {num2} a participé à {num2_participations} courses et a réussi {num2_dans_arrivee} fois : {num2_reussite_participations:.1f}%")

        print("\n=== Résultats basés sur les courses en commun ===")
        print(f"Les deux numéros ont participé ensemble à {courses_en_commun} courses.")
        print(f"Double réussite par rapport aux courses en commun : {double_reussite_pct_commun:.1f}% ({double_reussite}/{courses_en_commun})")

        if courses_double_reussite:
            print("\nCourses où les deux numéros sont arrivés ensemble :")
            for date_course in courses_double_reussite:
                print(f"- {date_course}")
        else:
            print("\nAucune course où les deux numéros sont arrivés ensemble.")

        return {
            'total_courses': total_courses,
            'num1_reussite': num1_reussite,
            'num2_reussite': num2_reussite,
            'double_reussite': double_reussite_pct,
            'num1_participations': num1_participations,
            'num2_participations': num2_participations,
            'num1_reussite_participations': num1_reussite_participations,
            'num2_reussite_participations': num2_reussite_participations,
            'courses_en_commun': courses_en_commun,
            'double_reussite_pct_commun': double_reussite_pct_commun,
            'courses_double_reussite': courses_double_reussite
        }
    def analyser_toutes_paires(self, type_course: Optional[str] = None,
                              date_debut: Optional[str] = None, date_fin: Optional[str] = None) -> None:
        """Analyse toutes les paires de positions possibles."""
        courses = self.db.get_courses(type_course, date_debut, date_fin)
        analyse_all_pairs(courses)

    def obtenir_statistiques_globales(self) -> Dict[str, Any]:
        """Récupère les statistiques globales."""
        return self.db.get_global_stats()

    def obtenir_lieux_disponibles(self) -> List[str]:
        """Retourne la liste des lieux disponibles dans la base de données."""
        with sqlite3.connect(self.db.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT lieu FROM courses')
            return [row[0] for row in cur.fetchall()]

    def obtenir_distances_disponibles(self) -> List[str]:
        """Retourne la liste des distances disponibles dans la base de données."""
        with sqlite3.connect(self.db.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT distance FROM courses')
            return [row[0] for row in cur.fetchall()]

    def obtenir_distances_disponibles_par_discipline(self, discipline: str) -> List[str]:
        """
        Retourne la liste des distances disponibles pour une discipline donnée.
        :param discipline: La discipline pour laquelle obtenir les distances.
        :return: Une liste des distances disponibles.
        """
        with sqlite3.connect(self.db.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT distance FROM courses WHERE type_course = ?', (discipline,))
            return [row[0] for row in cur.fetchall()]

    def obtenir_disciplines_disponibles(self) -> List[str]:
        """Retourne la liste des disciplines disponibles dans la base de données."""
        with sqlite3.connect(self.db.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT type_course FROM courses')
            disciplines = [row[0] for row in cur.fetchall()]
            return disciplines
    def selectionner_type_et_distance(self):
        """Permet de sélectionner un type et une distance puis analyse"""
        discipline_distance = self.choisir_discipline_et_distance()
        if discipline_distance:
            discipline, distance = discipline_distance
            courses = self.db.get_courses(
                type_course=discipline, 
                distance=distance
            )
            if courses:
                self.analyser_paire_impaire_par_tranche_synthese(courses)
            else:
                print("Aucune course trouvée avec ces critères.")
    def obtenir_distances_disponibles_par_discipline(self, discipline: str) -> List[str]:
        """Retourne les distances disponibles pour une discipline."""
        with sqlite3.connect(self.db.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT distance FROM courses WHERE type_course = ?", (discipline,))
            return [row[0] for row in cur.fetchall() if row[0]]

    def afficher_frequence_synthese(self, type_course: Optional[str] = None) -> None:
        """
        Affiche la fréquence des numéros, des couples, des triples et des écarts dans la synthèse,
        avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        # Calcul des fréquences
        frequence = analyse_frequence_synthese(courses)
        #frequence_couples = analyser_couples_synthese(courses)
        #frequence_triples = analyser_triples_synthese(courses)
        #frequence_ecarts = analyser_ecarts_synthese(courses)
        
        # Affichage des résultats
        print(f"\n=== Fréquence des numéros dans la synthèse ===")
        for num in sorted(frequence.keys()):
            print(f"Numéro {num} : {frequence[num]:.1f}%")
        
        #print(f"\n=== Fréquence des couples de numéros dans la synthèse ===")
        #for couple, freq in sorted(frequence_couples.items(), key=lambda x: x[1], reverse=True):  # Tous
        #    print(f"Couple {couple} : {freq:.1f}%")
        
        #print(f"\n=== Fréquence des triples de numéros dans la synthèse ===")
        #for triple, freq in sorted(frequence_triples.items(), key=lambda x: x[1], reverse=True):  # Tous
        #    print(f"Triple {triple} : {freq:.1f}%")
        
        #print(f"\n=== Fréquence des écarts entre les numéros dans la synthèse ===")
        #for ecart, freq in sorted(frequence_ecarts.items(), key=lambda x: x[1], reverse=True):
        #    print(f"Écart de {ecart} : {freq:.1f}%")
        
        # Afficher les graphiques
        afficher_graphique_frequence_numeros(frequence)
        #afficher_graphique_frequence_couples(frequence_couples)
        #afficher_graphique_frequence_triples(frequence_triples)
        #afficher_graphique_ecarts(frequence_ecarts)

    def afficher_frequence_couples(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche la fréquence des couples de numéros dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence_couples = analyser_couples_synthese(courses)
        print(f"\n=== Fréquence des couples de numéros dans la synthèse ===")
        for couple, freq in sorted(frequence_couples.items(), key=lambda x: x[1], reverse=True):  # Tous
            print(f"Couple {couple} : {freq:.1f}%")
        
        # Afficher le graphique
        afficher_graphique_frequence_couples(frequence_couples)

    def afficher_frequence_triples(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche la fréquence des triples de numéros dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence_triples = analyser_triples_synthese(courses)
        print(f"\n=== Fréquence des triples de numéros dans la synthèse ===")
        for triple, freq in sorted(frequence_triples.items(), key=lambda x: x[1], reverse=True):  # Tous
            print(f"Triple {triple} : {freq:.1f}%")
        
        # Afficher le graphique
        afficher_graphique_frequence_triples(frequence_triples)

    def afficher_frequence_ecarts(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche la fréquence des écarts entre les numéros dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        frequence_ecarts = analyser_ecarts_synthese(courses)
        print(f"\n=== Fréquence des écarts entre les numéros dans la synthèse ===")
        for ecart, freq in sorted(frequence_ecarts.items(), key=lambda x: x[1], reverse=True):
            print(f"Écart de {ecart} : {freq:.1f}%")
        
        # Afficher le graphique
        afficher_graphique_ecarts(frequence_ecarts)

    def afficher_ecarts_numeros(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche l'écart et l'écart maximum pour chaque numéro dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_numeros = calculer_ecarts_numeros(courses)
        print("\n=== Écarts pour chaque numéro dans la synthèse ===")
        for num in sorted(ecarts_numeros.keys()):
            print(f"Numéro {num} : Écart actuel = {ecarts_numeros[num]['ecart_actuel']}, Écart max = {ecarts_numeros[num]['ecart_max']}")

    def afficher_ecarts_numeros_filtres(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche l'écart et l'écart maximum pour chaque numéro dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_numeros = calculer_ecarts_numeros(courses)
        print("\n=== Écarts pour chaque numéro dans la synthèse ===")
        for num in sorted(ecarts_numeros.keys()):
            print(f"Numéro {num} : Écart actuel = {ecarts_numeros[num]['ecart_actuel']}, Écart max = {ecarts_numeros[num]['ecart_max']}")

    def afficher_ecarts_couples_filtres(self, type_course: Optional[str] = None, distance: Optional[str] = None):
        """
        Affiche l'écart et l'écart maximum pour chaque couple de numéros dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_couples = calculer_ecarts_combinaisons(courses, taille_combinaison=2)
        print("\n=== Écarts pour chaque couple de numéros dans la synthèse ===")
        for couple in sorted(ecarts_couples.keys()):
            print(f"Couple {couple} : Écart actuel = {ecarts_couples[couple]['ecart_actuel']}, Écart max = {ecarts_couples[couple]['ecart_max']}")

    def afficher_ecarts_triples_filtres(self, type_course: Optional[str] = None, distance: Optional[str] = None):
        """
        Affiche l'écart et l'écart maximum pour chaque triple de numéros dans la synthèse, avec des filtres optionnels.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_triples = calculer_ecarts_combinaisons(courses, taille_combinaison=3)
        print("\n=== Écarts pour chaque triple de numéros dans la synthèse ===")
        for triple in sorted(ecarts_triples.keys()):
            print(f"Triple {triple} : Écart actuel = {ecarts_triples[triple]['ecart_actuel']}, Écart max = {ecarts_triples[triple]['ecart_max']}")

    def afficher_ecarts_couples_arrivee(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche l'écart et l'écart maximum pour chaque couple de numéros dans l'arrivée.
        """
        courses = self.db.get_courses()
        
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_couples = calculer_ecarts_couples_arrivee(courses)
        print("\n=== Écarts pour chaque couple de numéros dans l'arrivée ===")
        for couple in sorted(ecarts_couples.keys()):
            print(f"Couple {couple} : Écart actuel = {ecarts_couples[couple]['ecart_actuel']}, Écart max = {ecarts_couples[couple]['ecart_max']}")

    def afficher_ecarts_triples_arrivee(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche l'écart et l'écart maximum pour chaque triple de numéros dans l'arrivée.
        """
        courses = self.db.get_courses()
        
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        ecarts_triples = calculer_ecarts_triples_arrivee(courses)
        print("\n=== Écarts pour chaque triple de numéros dans l'arrivée ===")
        for triple in sorted(ecarts_triples.keys()):
            print(f"Triple {triple} : Écart actuel = {ecarts_triples[triple]['ecart_actuel']}, Écart max = {ecarts_triples[triple]['ecart_max']}")

    def choisir_discipline(self) -> Optional[str]:
        """
        Permet à l'utilisateur de choisir une discipline parmi celles disponibles.
        :return: La discipline choisie ou None si l'utilisateur annule.
        """
        disciplines = self.obtenir_disciplines_disponibles()
        if not disciplines:
            print("Aucune discipline disponible.")
            return None

        print("\n=== Choisir une discipline ===")
        for i, discipline in enumerate(disciplines, start=1):
            print(f"{i}. {discipline}")
        print(f"{len(disciplines) + 1}. Retour au menu précédent")

        choix = input("Choix : ").strip()
        if choix.isdigit() and 1 <= int(choix) <= len(disciplines):
            return disciplines[int(choix) - 1]
        elif choix == str(len(disciplines) + 1):
            return None
        else:
            print("Choix invalide. Veuillez réessayer.")
            return None

    def choisir_discipline_et_distance(self) -> Optional[Tuple[str, str]]:
        """
        Permet à l'utilisateur de choisir une discipline et une distance.
        :return: Un tuple (discipline, distance) ou None si l'utilisateur annule.
        """
        disciplines = self.obtenir_disciplines_disponibles()
        if not disciplines:
            print("Aucune discipline disponible.")
            return None

        print("\n=== Choisir une discipline ===")
        for i, discipline in enumerate(disciplines, start=1):
            print(f"{i}. {discipline}")
        print(f"{len(disciplines) + 1}. Retour au menu précédent")

        choix_discipline = input("Choix de la discipline : ").strip()
        if choix_discipline.isdigit() and 1 <= int(choix_discipline) <= len(disciplines):
            discipline_selectionnee = disciplines[int(choix_discipline) - 1]

            # Obtenir les distances disponibles pour la discipline sélectionnée
            distances = self.obtenir_distances_disponibles_par_discipline(discipline_selectionnee)
            if not distances:
                print(f"Aucune distance disponible pour la discipline '{discipline_selectionnee}'.")
                return None

            print(f"\n=== Choisir une distance pour '{discipline_selectionnee}' ===")
            for i, distance in enumerate(distances, start=1):
                print(f"{i}. {distance}")
            print(f"{len(distances) + 1}. Retour au menu précédent")

            choix_distance = input("Choix de la distance : ").strip()
            if choix_distance.isdigit() and 1 <= int(choix_distance) <= len(distances):
                distance_selectionnee = distances[int(choix_distance) - 1]
                return (discipline_selectionnee, distance_selectionnee)
            elif choix_distance == str(len(distances) + 1):
                return None
            else:
                print("Choix invalide. Veuillez réessayer.")
                return None
        elif choix_discipline == str(len(disciplines) + 1):
            return None
        else:
            print("Choix invalide. Veuillez réessayer.")
            return None

    def analyser_par_discipline(self, type_course: Optional[str] = None, distance: Optional[str] = None, analyse_type: str = "synthèse") -> None:
        """
        Analyse les données filtrées par discipline et distance.
        :param type_course: Type de course (discipline) pour filtrer les résultats.
        :param distance: Distance pour filtrer les résultats.
        :param analyse_type: Type d'analyse ("synthèse" ou "arrivée").
        """
        courses = self.db.get_courses()
        
        # Filtrage des courses
        if type_course:
            courses = [course for course in courses if course.get('type_course') == type_course]
        if distance:
            courses = [course for course in courses if course.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour les critères sélectionnés.")
            return
        
        # Afficher le nombre de courses trouvées
        print(f"\n=== Nombre de courses trouvées ===")
        if type_course and distance:
            print(f"Discipline : {type_course}, Distance : {distance} -> {len(courses)} courses")
        elif type_course:
            print(f"Discipline : {type_course} -> {len(courses)} courses")
        elif distance:
            print(f"Distance : {distance} -> {len(courses)} courses")
        else:
            print(f"Total des courses : {len(courses)}")
        
        if analyse_type == "synthèse":
            # Analyse des écarts dans la synthèse
            ecarts_numeros = calculer_ecarts_numeros(courses)
            ecarts_couples = calculer_ecarts_combinaisons(courses, taille_combinaison=2)
            ecarts_triples = calculer_ecarts_combinaisons(courses, taille_combinaison=3)
            
            print(f"\n=== Écarts pour chaque numéro dans la synthèse ===")
            for num in sorted(ecarts_numeros.keys()):
                print(f"Numéro {num} : Écart actuel = {ecarts_numeros[num]['ecart_actuel']}, Écart max = {ecarts_numeros[num]['ecart_max']}")

            print(f"\n=== Écarts pour chaque couple de numéros dans la synthèse ===")
            for couple in sorted(ecarts_couples.keys()):
                print(f"Couple {couple} : Écart actuel = {ecarts_couples[couple]['ecart_actuel']}, Écart max = {ecarts_couples[couple]['ecart_max']}")
            
            print(f"\n=== Écarts pour chaque triple de numéros dans la synthèse ===")
            for triple in sorted(ecarts_triples.keys()):
                print(f"Triple {triple} : Écart actuel = {ecarts_triples[triple]['ecart_actuel']}, Écart max = {ecarts_triples[triple]['ecart_max']}")
        
        elif analyse_type == "arrivée":
            # Analyse des écarts dans l'arrivée
            ecarts_numeros_arrivee = calculer_ecarts_numeros_arrivee(courses)
            ecarts_couples_arrivee = calculer_ecarts_couples_arrivee(courses)
            ecarts_triples_arrivee = calculer_ecarts_triples_arrivee(courses)
            
            print(f"\n=== Écarts pour chaque numéro dans l'arrivée ===")
            for num in sorted(ecarts_numeros_arrivee.keys()):
                print(f"Numéro {num} : Écart actuel = {ecarts_numeros_arrivee[num]['ecart_actuel']}, Écart max = {ecarts_numeros_arrivee[num]['ecart_max']}")
            
            print(f"\n=== Écarts pour chaque couple de numéros dans l'arrivée ===")
            for couple in sorted(ecarts_couples_arrivee.keys()):
                print(f"Couple {couple} : Écart actuel = {ecarts_couples_arrivee[couple]['ecart_actuel']}, Écart max = {ecarts_couples_arrivee[couple]['ecart_max']}")
            
            print(f"\n=== Écarts pour chaque triple de numéros dans l'arrivée ===")
            for triple in sorted(ecarts_triples_arrivee.keys()):
                print(f"Triple {triple} : Écart actuel = {ecarts_triples_arrivee[triple]['ecart_actuel']}, Écart max = {ecarts_triples_arrivee[triple]['ecart_max']}")
        
        else:
            print("Type d'analyse non reconnu. Choisissez 'synthèse' ou 'arrivée'.")

    def analyser_par_discipline_et_distance_arrivee(self) -> None:
        """
        Analyse les données d'arrivée filtrées par discipline et distance.
        Affiche les disciplines et distances disponibles avant de demander à l'utilisateur de choisir.
        """
        # Afficher les disciplines disponibles
        disciplines = self.obtenir_disciplines_disponibles()
        if not disciplines:
            print("Aucune discipline disponible.")
            return
        
        print("\n=== Disciplines disponibles ===")
        for i, discipline in enumerate(disciplines, start=1):
            print(f"{i}. {discipline}")
        
        # Demander à l'utilisateur de choisir une discipline
        choix_discipline = input("Choisissez une discipline (numéro) : ").strip()
        if not choix_discipline.isdigit() or int(choix_discipline) < 1 or int(choix_discipline) > len(disciplines):
            print("Choix invalide.")
            return
        
        discipline_selectionnee = disciplines[int(choix_discipline) - 1]
        
        # Afficher les distances disponibles pour la discipline sélectionnée
        distances = self.obtenir_distances_disponibles_par_discipline(discipline_selectionnee)
        if not distances:
            print(f"Aucune distance disponible pour la discipline '{discipline_selectionnee}'.")
            return
        
        print(f"\n=== Distances disponibles pour '{discipline_selectionnee}' ===")
        for i, distance in enumerate(distances, start=1):
            print(f"{i}. {distance}")
        
        # Demander à l'utilisateur de choisir une distance
        choix_distance = input("Choisissez une distance (numéro) : ").strip()
        if not choix_distance.isdigit() or int(choix_distance) < 1 or int(choix_distance) > len(distances):
            print("Choix invalide.")
            return
        
        distance_selectionnee = distances[int(choix_distance) - 1]
        
        # Effectuer l'analyse
        courses = self.db.get_courses()
        resultats = analyser_par_discipline_et_distance_arrivee(courses, discipline_selectionnee, distance_selectionnee)
        
        if "erreur" in resultats:
            print(resultats["erreur"])
            return
        
        print("\n=== Analyse par discipline et distance ===")
        print(f"Discipline : {discipline_selectionnee}, Distance : {distance_selectionnee}")
        print(f"Nombre de courses : {resultats['total_courses']}")
        
        print("\nFréquence des numéros dans l'arrivée :")
        for num, freq in resultats['frequence_arrivee'].items():
            print(f"Numéro {num} : {freq:.1f}%")
        
        print("\nÉcarts pour chaque numéro dans l'arrivée :")
        for num, ecarts in resultats['ecarts_numeros_arrivee'].items():
            print(f"Numéro {num} : Écart actuel = {ecarts['ecart_actuel']}, Écart max = {ecarts['ecart_max']}")
        
        print("\nÉcarts pour chaque couple de numéros dans l'arrivée :")
        for couple, ecarts in resultats['ecarts_couples_arrivee'].items():
            print(f"Couple {couple} : Écart actuel = {ecarts['ecart_actuel']}, Écart max = {ecarts['ecart_max']}")
        
        print("\nÉcarts pour chaque triple de numéros dans l'arrivée :")
        for triple, ecarts in resultats['ecarts_triples_arrivee'].items():
            print(f"Triple {triple} : Écart actuel = {ecarts['ecart_actuel']}, Écart max = {ecarts['ecart_max']}")
    
    def obtenir_distances_disponibles_par_discipline(self, discipline: str) -> List[str]:
        """
        Retourne la liste des distances disponibles pour une discipline donnée.
        """
        with sqlite3.connect(self.db.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT DISTINCT distance FROM courses WHERE type_course = ?', (discipline,))
            return [row[0] for row in cur.fetchall()]
        
    def obtenir_courses_filtrees(self, filters):
        """
        Retourne la liste des courses filtrées selon les critères spécifiés.
        """
        courses = self.db.get_courses()  # Assurez-vous que cette méthode existe

        # Appliquer les filtres
        if 'type_course' in filters:
            courses = [c for c in courses if c.get('type_course') == filters['type_course']]
        if 'distance' in filters:
            courses = [c for c in courses if c.get('distance') == filters['distance']]
        if 'lieu' in filters:
            courses = [c for c in courses if c.get('lieu') == filters['lieu']]

        return courses

    def analyser_tranches_synthese(self):
        """
        Analyse les numéros de la synthèse en trois tranches et affiche un graphique.
        """
        courses = self.db.get_courses()
        if not courses:
            print("Aucune donnée disponible pour l'analyse.")
            return

        print("\n=== Analyse par tranche de 5-5-reste ===")
        for course in courses:
            synthese = course.get('synthese', '')
            synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
            numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

            # Initialisation des compteurs pour chaque tranche
            tranche_1 = 0  # 1 à 5
            tranche_2 = 0  # 6 à 10
            tranche_3 = 0  # 11 et au-delà

            for num in numeros:
                if 1 <= num <= 5:
                    tranche_1 += 1
                elif 6 <= num <= 10:
                    tranche_2 += 1
                else:
                    tranche_3 += 1

            # Affichage des résultats pour chaque course
            print(f"\nCourse du {course['date_course']} à {course['lieu']} :")
            print(f"Tranche 1 (1-5) : {tranche_1} numéros")
            print(f"Tranche 2 (6-10) : {tranche_2} numéros")
            print(f"Tranche 3 (11+) : {tranche_3} numéros")

        # Affichage du graphique
        from analyse import afficher_graphique_tranches_synthese
        afficher_graphique_tranches_synthese(courses)
    def analyser_tranches_synthese_tierce(self):
        """
        Analyse les numéros de la synthèse en trois tranches et affiche un graphique.
        """
        courses = self.db.get_courses()
        if not courses:
            print("Aucune donnée disponible pour l'analyse.")
            return

        print("\n=== Analyse par tranche de 5-5-reste ===")
        for course in courses:
            synthese = course.get('synthese', '')
            synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
            numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

            # Limiter l'analyse aux trois premiers numéros
            numeros = numeros[:3]

            # Initialisation des compteurs pour chaque tranche
            tranche_1 = 0  # 1 à 5
            tranche_2 = 0  # 6 à 10
            tranche_3 = 0  # 11 et au-delà

            for num in numeros:
                if 1 <= num <= 5:
                    tranche_1 += 1
                elif 6 <= num <= 10:
                    tranche_2 += 1
                else:
                    tranche_3 += 1

            # Affichage des résultats pour chaque course
            print(f"\nCourse du {course['date_course']} à {course['lieu']} :")
            print(f"Tranche 1 (1-5) : {tranche_1} numéros")
            print(f"Tranche 2 (6-10) : {tranche_2} numéros")
            print(f"Tranche 3 (11+) : {tranche_3} numéros")

        # Affichage du graphique
        from analyse import afficher_graphique_tranches_synthese_tierce
        afficher_graphique_tranches_synthese_tierce(courses)

    def analyser_tranches_synthese_par_discipline(self, discipline: str):
        """
        Analyse les tranches de 5-5-reste pour une discipline donnée.
        :param discipline: La discipline à filtrer (par exemple, "Plat", "Attelé").
        """
        courses = self.db.get_courses(type_course=discipline)
        if not courses:
            print(f"Aucune donnée disponible pour la discipline '{discipline}'.")
            return

        print(f"\n=== Analyse par tranche de 5-5-reste pour la discipline '{discipline}' ===")
        self._afficher_tranches_synthese(courses)
    def analyser_tranches_synthese_tierce_par_discipline(self, discipline: str):
        """
        Analyse les tranches de 5-5-reste pour une discipline donnée.
        :param discipline: La discipline à filtrer (par exemple, "Plat", "Attelé").
        """
        courses = self.db.get_courses(type_course=discipline)
        if not courses:
            print(f"Aucune donnée disponible pour la discipline '{discipline}'.")
            return

        print(f"\n=== Analyse par tranche de 5-5-reste pour la discipline '{discipline}' ===")
        self._afficher_tranches_synthese_tierce(courses)

    def analyser_tranches_synthese_par_discipline_et_distance(self, discipline: str, distance: str):
        """
        Analyse les tranches de 5-5-reste pour une discipline et une distance données.
        :param discipline: La discipline à filtrer (par exemple, "Plat", "Attelé").
        :param distance: La distance à filtrer (par exemple, "2700m", "3800m").
        """
        courses = self.db.get_courses(type_course=discipline, distance=distance)
        if not courses:
            print(f"Aucune donnée disponible pour la discipline '{discipline}' et la distance '{distance}'.")
            return

        print(f"\n=== Analyse par tranche de 5-5-reste pour la discipline '{discipline}' et la distance '{distance}' ===")
        self._afficher_tranches_synthese(courses)
    def analyser_tranches_synthese_tierce_par_discipline_et_distance(self, discipline: str, distance: str):
        """
        Analyse les tranches de 5-5-reste pour une discipline et une distance données.
        :param discipline: La discipline à filtrer (par exemple, "Plat", "Attelé").
        :param distance: La distance à filtrer (par exemple, "2700m", "3800m").
        """
        courses = self.db.get_courses(type_course=discipline, distance=distance)
        if not courses:
            print(f"Aucune donnée disponible pour la discipline '{discipline}' et la distance '{distance}'.")
            return

        print(f"\n=== Analyse par tranche de 5-5-reste pour la discipline '{discipline}' et la distance '{distance}' ===")
        self._afficher_tranches_synthese_tierce(courses)

    def _afficher_tranches_synthese(self, courses):
            """
            Affiche les résultats de l'analyse par tranche de 5-5-reste pour une liste de courses donnée.
            :param courses: Liste des courses à analyser.
            """
            for course in courses:
                synthese = course.get('synthese', '')
                synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
                numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

                # Initialisation des compteurs pour chaque tranche
                tranche_1 = 0  # 1 à 5
                tranche_2 = 0  # 6 à 10
                tranche_3 = 0  # 11 et au-delà

                for num in numeros:
                    if 1 <= num <= 5:
                        tranche_1 += 1
                    elif 6 <= num <= 10:
                        tranche_2 += 1
                    else:
                        tranche_3 += 1

                # Affichage des résultats pour chaque course
                print(f"\nCourse du {course['date_course']} à {course['lieu']} :")
                print(f"Tranche 1 (1-5) : {tranche_1} numéros")
                print(f"Tranche 2 (6-10) : {tranche_2} numéros")
                print(f"Tranche 3 (11+) : {tranche_3} numéros")

            # Affichage du graphique
            from analyse import afficher_graphique_tranches_synthese
            afficher_graphique_tranches_synthese(courses)
    def _afficher_tranches_synthese_tierce(self, courses):
            """
            Affiche les résultats de l'analyse par tranche de 5-5-reste pour une liste de courses donnée.
            :param courses: Liste des courses à analyser.
            """
            for course in courses:
                synthese = course.get('synthese', '')
                synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
                numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

                # Initialisation des compteurs pour chaque tranche
                tranche_1 = 0  # 1 à 5
                tranche_2 = 0  # 6 à 10
                tranche_3 = 0  # 11 et au-delà

                for num in numeros:
                    if 1 <= num <= 5:
                        tranche_1 += 1
                    elif 6 <= num <= 10:
                        tranche_2 += 1
                    else:
                        tranche_3 += 1

                # Affichage des résultats pour chaque course
                print(f"\nCourse du {course['date_course']} à {course['lieu']} :")
                print(f"Tranche 1 (1-5) : {tranche_1} numéros")
                print(f"Tranche 2 (6-10) : {tranche_2} numéros")
                print(f"Tranche 3 (11+) : {tranche_3} numéros")

            # Affichage du graphique
            from analyse import afficher_graphique_tranches_synthese_tierce
            afficher_graphique_tranches_synthese_tierce(courses)

    def analyser_numero_synthese(self, numero: int, filters: dict) -> Dict[str, Any]:
        """Méthode de classe pour gérer les filtres"""
        courses = self.db.get_courses(
            type_course=filters.get('type_course'),
            distance=filters.get('distance'),
            date_debut=filters.get('date_debut'),
            date_fin=filters.get('date_fin')
        )
        
        if 'lieu' in filters:
            courses = [c for c in courses if c.get('lieu') == filters['lieu']]
            
        return analyser_numero_synthese(courses, numero)  # Appel à la fonction externe

    def analyser_concordance_numero(self, numero_cheval: int) -> Dict[Tuple[int, int], Dict[str, Any]]:
        concordance = {}
        courses = self.db.get_courses()
        
        required_keys = ['date_course', 'partants', 'arrivee']
        for course in courses:
            for key in required_keys:
                if key not in course:
                    raise ValueError(f"Données incomplètes : colonne '{key}' manquante dans la course du {course.get('date_course', 'date inconnue')}")


        # Filtrer et trier les courses par date
        courses_filtrees = sorted(
            [c for c in courses if datetime.strptime(c["date_course"], "%Y-%m-%d") <= DATE_ACTUELLE_SIMULEE],
            key=lambda x: datetime.strptime(x["date_course"], "%Y-%m-%d")
        )
        
        for index, course in enumerate(courses_filtrees):
            partants = list(map(int, course.get('partants', '').split(',')))
            arrivee = list(map(int, course.get('arrivee', '').split('-')))
            
            if numero_cheval in partants:
                autres_chevaux = [x for x in partants if x != numero_cheval]
                
                for cheval in autres_chevaux:
                    couple = tuple(sorted((numero_cheval, cheval)))
                    
                    if couple not in concordance:
                        concordance[couple] = {
                            "participations": [],  # Stocke les dates des participations
                            "success_indices": [],  # Positions des réussites dans participations
                            "success_details": defaultdict(int)  # Détail par type de course
                        }
                    
                    # Enregistrer la participation
                    concordance[couple]["participations"].append(course["date_course"])
                    
                    # Vérifier l'arrivée commune
                    if numero_cheval in arrivee and cheval in arrivee:
                        success_index = len(concordance[couple]["participations"]) - 1
                        concordance[couple]["success_indices"].append(success_index)
                        
                        # Enregistrer le type de course
                        course_type = course.get('type_course', 'Inconnu')
                        concordance[couple]["success_details"][course_type] += 1
        
        # Calculer les statistiques finales
            for couple, data in concordance.items():
                total_participations = len(data["participations"])
                success_indices = data["success_indices"]
                
                if not success_indices:
                    # Jamais réussi
                    ecart_actuel = total_participations
                    ecart_max = total_participations
                else:
                    # Calcul de tous les écarts
                    gaps = []
                    
                    # Écart avant la première réussite
                    gaps.append(success_indices[0])
                    
                    # Écarts entre les réussites successives
                    for i in range(1, len(success_indices)):
                        gaps.append(success_indices[i] - success_indices[i-1] - 1)
                    
                    # Écart après la dernière réussite
                    gaps.append(total_participations - success_indices[-1] - 1)
                    
                    # Écart maximum
                    ecart_max = max(gaps) if gaps else 0
                    
                    # Écart actuel
                    ecart_actuel = gaps[-1]

                # Mise à jour des données
                data.update({
                    "total_participations": total_participations,
                    "total_successes": len(success_indices),
                    "ecart_actuel": ecart_actuel,
                    "ecart_max": ecart_max
                })
        
        return concordance
    
    def concordance_deux_numeros(self, num1: int, num2: int) -> Dict[Tuple[int, int, int], Dict[str, Any]]:
        """
        Analyse la concordance entre deux numéros fixes (num1 et num2) avec tous les autres numéros.
        Retourne les statistiques pour chaque combinaison triple.
        """
        concordance = defaultdict(lambda: {
            "participations": [],
            "success_indices": [],
            "success_details": defaultdict(int),
            "total_participations": 0,
            "total_successes": 0,
            "ecart_actuel": 0,
            "ecart_max": 0
        })
        
        courses = self.db.get_courses()
        courses_triees = sorted(
            [c for c in courses if datetime.strptime(c["date_course"], "%Y-%m-%d") <= DATE_ACTUELLE_SIMULEE],
            key=lambda x: datetime.strptime(x["date_course"], "%Y-%m-%d")
        )

        for idx, course in enumerate(courses_triees):
            partants = list(map(int, course.get('partants', '').split(',')))
            arrivee = list(map(int, course.get('arrivee', '').split('-')))

            if num1 in partants and num2 in partants:
                for autre_num in (n for n in partants if n not in {num1, num2}):
                    triple = tuple(sorted((num1, num2, autre_num)))

                    # Enregistrement participation
                    concordance[triple]["participations"].append(course["date_course"])
                    
                    # Vérification réussite
                    if num1 in arrivee and num2 in arrivee and autre_num in arrivee:
                        concordance[triple]["success_indices"].append(len(concordance[triple]["participations"]) - 1)
                        concordance[triple]["success_details"][course.get('type_course', 'Inconnu')] += 1

        # Calcul des écarts
        for triple, data in concordance.items():
            participations = data["participations"]
            successes = data["success_indices"]
            data["total_participations"] = len(participations)
            data["total_successes"] = len(successes)

            if not successes:
                data["ecart_actuel"] = data["total_participations"]
                data["ecart_max"] = data["total_participations"]
            else:
                gaps = []
                # Écart avant première réussite
                gaps.append(successes[0])
                # Écarts entre réussites
                for i in range(1, len(successes)):
                    gaps.append(successes[i] - successes[i-1] - 1)
                # Écart après dernière réussite
                gaps.append((data["total_participations"] - 1) - successes[-1])
                
                data["ecart_max"] = max(gaps)
                data["ecart_actuel"] = max(0, gaps[-1])  # Correction ici

        return concordance

    def afficher_sous_menu_concordance_deux_numeros(self):
        """Affiche le sous-menu interactif pour l'analyse à deux numéros."""
        while True:
            print("\n=== Analyse de Concordance pour 2 Numéros ===")
            print("1. Saisir deux numéros")
            print("2. Retour au menu principal")
            choix = input("Choix : ").strip()

            if choix == "1":
                try:
                    num1 = int(input("Premier numéro : "))
                    num2 = int(input("Deuxième numéro : "))
                    resultats = self.concordance_deux_numeros(num1, num2)
                    
                    print(f"\n=== Résultats pour {num1} & {num2} avec tous les tiers ===")
                    for triple, stats in sorted(resultats.items()):
                        print(f"\nTriple {triple[0]}‑{triple[1]}‑{triple[2]} :")
                        print(f"Participations conjointes : {stats['total_participations']}")
                        print(f"Réussites communes        : {stats['total_successes']}")
                        
                        if stats['total_successes'] > 0:
                            print("Détail des réussites par type :")
                            for type_course, count in stats['success_details'].items():
                                print(f"  - {type_course}: {count} fois")
                        else:
                            print("Aucune réussite commune")
                        
                        print(f"Écart actuel  : {stats['ecart_actuel']} courses")
                        print(f"Écart maximum : {stats['ecart_max']} courses")
                        print("-" * 50)
                        
                except ValueError:
                    print("Saisie invalide. Veuillez entrer des numéros.")
            elif choix == "2":
                break
            else:
                print("Choix invalide.")

    
    def _maj_ecarts(self, data, date_course, idx):
        """Met à jour les écarts pour une combinaison."""
        if data['last_date'] is not None:
            ecart = idx - data['last_date']
            data['ecart_max'] = max(data['ecart_max'], ecart)
        data['last_date'] = idx

    def _calcul_final_ecarts(self, stats, total_courses):
        """Calcule les écarts actuels."""
        for combo_type in ['triples', 'paires']:
            for combo, data in stats['combinaisons'][combo_type].items():
                if data['last_date'] is not None:
                    data['ecart_actuel'] = total_courses - data['last_date'] - 1
                else:
                    data['ecart_actuel'] = total_courses

    def exporter_resultats_csv(self, resultats: Dict[str, Any], fichier_sortie: str):
        """
        Exporte les résultats d'analyse en CSV.
        :param resultats: Dictionnaire contenant les résultats.
        :param fichier_sortie: Chemin du fichier de sortie.
        """
        df = pd.DataFrame.from_dict(resultats, orient='index')
        df.to_csv(fichier_sortie, index_label='Numéro')
        print(f"Résultats exportés dans {fichier_sortie}")

    def predire_resultats(self):
        """
        Entraîne un modèle de prédiction et affiche les résultats.
        """
        courses = self.db.get_courses()
        if not courses:
            print("Aucune donnée disponible pour l'entraînement.")
            return
        
        X, y_encoded, label_encoder = preparer_donnees(courses)
        if len(X) == 0:
            print("Pas assez de données pour l'entraînement.")
            return
        
        if len(set(y_encoded)) < 2:  # Vérifier s'il y a au moins deux classes différentes
            print("Pas assez de variabilité dans les données pour entraîner un modèle.")
            return
        
        model = entrainer_modele(X, y_encoded)
        
        # Exemple de prédiction avec les mêmes features que pendant l'entraînement
        if X.shape[1] == 5:  # Si le modèle a été entraîné avec 5 features
            prediction_encoded = model.predict([[5, 1, 3800, -1, 1]])  # Prédire avec les mêmes features
        else:
            print(f"Nombre de features inattendu : {X.shape[1]}. Impossible de faire une prédiction.")
            return
        
        # Décoder la prédiction pour obtenir le numéro original
        prediction = label_encoder.inverse_transform(prediction_encoded)
        print(f"Prédiction du troisième numéro : {prediction[0]}")
        
        # Afficher un graphique de la précision du modèle
        precisions = [0.0, 33.3, 50.0]  # Exemple de précisions
        labels = ['Modèle 1', 'Modèle 2', 'Modèle 3']  # Exemple de labels
        afficher_graphique_precision(precisions, labels)

    def analyser_paire_impaire_par_tranche_synthese(self, courses: List[Dict[str, Any]], last_n: Optional[int] = None) -> None:
        """
        Analyse la répartition pair/impair des premiers de l'arrivée, classés par tranche selon la synthèse.
        :param courses: Liste des courses à analyser.
        :param last_n: Nombre de dernières courses à analyser (optionnel).
        """
        from analyse import analyser_paire_impaire_par_tranche_synthese
        analyser_paire_impaire_par_tranche_synthese(courses)

        # Filtrer les dernières courses si nécessaire
        if last_n:
            courses = sorted(courses, key=lambda x: x['date_course'], reverse=True)[:last_n]

        # Appeler la fonction d'analyse
        analyser_paire_impaire_par_tranche_synthese(courses)
    def analyser_15_dernieres_courses(self):
        """Analyse sur les 15 dernières courses"""
        courses = sorted(self.db.get_courses(), key=lambda x: x['date_course'], reverse=True)[:15]
        if not courses:
            print("Aucune course disponible.")
            return
        self.analyser_paire_impaire_par_tranche_synthese(courses)

    def analyser_30_dernieres_courses(self):
        """Analyse sur les 30 dernières courses"""
        courses = sorted(self.db.get_courses(), key=lambda x: x['date_course'], reverse=True)[:30]
        if not courses:
            print("Aucune course disponible.")
            return
        self.analyser_paire_impaire_par_tranche_synthese(courses)

    
    def afficher_ecarts_premiers_arrivee(self, type_course: Optional[str] = None, distance: Optional[str] = None) -> None:
        """
        Affiche les écarts spécifiques aux numéros ayant terminé premiers
        avec possibilité de filtrer par discipline et distance
        """
        courses = self.db.get_courses()
        
        # Application des filtres
        if type_course:
            courses = [c for c in courses if c.get('type_course') == type_course]
        if distance:
            courses = [c for c in courses if c.get('distance') == distance]
        
        if not courses:
            print("Aucune donnée disponible pour ces critères")
            return
        
        ecarts = calculer_ecarts_premiers_synthese(courses)
        
        print(f"\n=== ÉCARTS POUR LES VAINQUEURS ({len(courses)} courses analysées) ===")
        for num in sorted(ecarts.keys()):
            stats = ecarts[num]
            print(f"Numéro {num}:")
            print(f"  Dernière victoire: {stats['derniere_occurrence'] + 1} courses ago")
            print(f"  Écart actuel: {stats['ecart_actuel']}")
            print(f"  Écart max historique: {stats['ecart_max']}")
            print("-" * 30)

    def afficher_ecarts_premiers_synthese_filtres(self):
        """Version améliorée avec gestion des erreurs et meilleur parsing"""
        try:
            # Récupération dynamique des options
            disciplines = ['Toutes'] + self.obtenir_disciplines_disponibles()
            distances = ['Toutes'] + self.obtenir_distances_disponibles()

            # Sélection discipline
            print("\n=== DISCIPLINES DISPONIBLES ===")
            for i, d in enumerate(disciplines):
                print(f"{i}. {d}")
            choix_d = int(input("Choix (numéro) : "))
            discipline = None if choix_d == 0 else disciplines[choix_d]

            # Sélection distance
            print("\n=== DISTANCES DISPONIBLES ===")
            for i, d in enumerate(distances):
                print(f"{i}. {d}")
            choix_dist = int(input("Choix (numéro) : "))
            distance = None if choix_dist == 0 else distances[choix_dist]

            # Filtrage des courses
            courses = self.db.get_courses()
            if discipline:
                courses = [c for c in courses if c.get('type_course') == discipline]
            if distance:
                courses = [c for c in courses if c.get('distance') == distance]

            if not courses:
                print("\n⚠️ Aucune course correspondante")
                return

            # Calcul des écarts
            ecarts = calculer_ecarts_premiers_synthese(courses)
            
            if not ecarts:
                print("\nℹ️ Aucun numéro n'a terminé premier dans ces courses")
                return

            # Affichage détaillé
            print(f"\n📊 ANALYSE DES VAINQUEURS - {len(courses)} courses")
            print(f"Discipline: {discipline or 'Toutes'} | Distance: {distance or 'Toutes'}")
            print("-" * 60)
            
            # Tri par numéro avec gestion des plages complètes
            for num in sorted(ecarts.keys()):
                stats = ecarts[num]
                print(f"▶ Numéro {num}:")
                print(f"   Occurrences totales : {stats['total_occurrences']}")
                print(f"   Fréquence relative : {stats['frequence']:.1f}%")
                print(f"   Dernière apparition : {stats['ecart_actuel']} courses")
                print(f"   Écart maximum       : {stats['ecart_max']} courses")
                
                # Affichage des 3 dernières dates d'apparition
                if stats['occurrences']:
                    derniers_dates = ", ".join(stats['occurrences'][-3:])
                    print(f"   Dernières apparitions: {derniers_dates}")
                
                print("-" * 60)

        except (ValueError, IndexError):
            print("\n❌ Sélection invalide - Veuillez entrer un numéro de la liste")
        except Exception as e:
            print(f"\n⚠️ Erreur inattendue : {str(e)}")

    def afficher_ecarts_deuxiemes_synthese_filtres(self):
        """Version améliorée avec gestion des erreurs et meilleur parsing"""
        try:
            # Récupération dynamique des options
            disciplines = ['Toutes'] + self.obtenir_disciplines_disponibles()
            distances = ['Toutes'] + self.obtenir_distances_disponibles()

            # Sélection discipline
            print("\n=== DISCIPLINES DISPONIBLES ===")
            for i, d in enumerate(disciplines):
                print(f"{i}. {d}")
            choix_d = int(input("Choix (numéro) : "))
            discipline = None if choix_d == 0 else disciplines[choix_d]

            # Sélection distance
            print("\n=== DISTANCES DISPONIBLES ===")
            for i, d in enumerate(distances):
                print(f"{i}. {d}")
            choix_dist = int(input("Choix (numéro) : "))
            distance = None if choix_dist == 0 else distances[choix_dist]

            # Filtrage des courses
            courses = self.db.get_courses()
            if discipline:
                courses = [c for c in courses if c.get('type_course') == discipline]
            if distance:
                courses = [c for c in courses if c.get('distance') == distance]

            if not courses:
                print("\n⚠️ Aucune course correspondante")
                return

            # Calcul des écarts pour les deuxièmes places
            ecarts = calculer_ecarts_deuxiemes_synthese(courses)

            if not ecarts:
                print("\nℹ️ Aucun numéro n'a terminé deuxième dans ces courses")
                return

            # Affichage détaillé
            print(f"\n📊 ANALYSE DES DEUXIÈMES - {len(courses)} courses")
            print(f"Discipline: {discipline or 'Toutes'} | Distance: {distance or 'Toutes'}")
            print("-" * 60)

            # Tri par numéro avec gestion des plages complètes
            for num in sorted(ecarts.keys()):
                stats = ecarts[num]
                print(f"▶ Numéro {num}:")
                print(f"   Occurrences totales : {stats['total_occurrences']}")
                print(f"   Fréquence relative : {stats['frequence']:.1f}%")
                print(f"   Dernière apparition : {stats['ecart_actuel']} courses")
                print(f"   Écart maximum       : {stats['ecart_max']} courses")

                # Affichage des 3 dernières dates d'apparition
                if stats['occurrences']:
                    derniers_dates = ", ".join(stats['occurrences'][-3:])
                    print(f"   Dernières apparitions: {derniers_dates}")

                print("-" * 60)

        except (ValueError, IndexError):
            print("\n❌ Sélection invalide - Veuillez entrer un numéro de la liste")
        except Exception as e:
            print(f"\n⚠️ Erreur inattendue : {str(e)}")
    def afficher_ecarts_troisiemes_synthese_filtres(self):
        """Version améliorée avec gestion des erreurs et meilleur parsing"""
        try:
            # Récupération dynamique des options
            disciplines = ['Toutes'] + self.obtenir_disciplines_disponibles()
            distances = ['Toutes'] + self.obtenir_distances_disponibles()

            # Sélection discipline
            print("\n=== DISCIPLINES DISPONIBLES ===")
            for i, d in enumerate(disciplines):
                print(f"{i}. {d}")
            choix_d = int(input("Choix (numéro) : "))
            discipline = None if choix_d == 0 else disciplines[choix_d]

            # Sélection distance
            print("\n=== DISTANCES DISPONIBLES ===")
            for i, d in enumerate(distances):
                print(f"{i}. {d}")
            choix_dist = int(input("Choix (numéro) : "))
            distance = None if choix_dist == 0 else distances[choix_dist]

            # Filtrage des courses
            courses = self.db.get_courses()
            if discipline:
                courses = [c for c in courses if c.get('type_course') == discipline]
            if distance:
                courses = [c for c in courses if c.get('distance') == distance]

            if not courses:
                print("\n⚠️ Aucune course correspondante")
                return

            # Calcul des écarts pour les deuxièmes places
            ecarts = calculer_ecarts_troisiemes_synthese(courses)

            if not ecarts:
                print("\nℹ️ Aucun numéro n'a terminé deuxième dans ces courses")
                return

            # Affichage détaillé
            print(f"\n📊 ANALYSE DES TROISIEMES - {len(courses)} courses")
            print(f"Discipline: {discipline or 'Toutes'} | Distance: {distance or 'Toutes'}")
            print("-" * 60)

            # Tri par numéro avec gestion des plages complètes
            for num in sorted(ecarts.keys()):
                stats = ecarts[num]
                print(f"▶ Numéro {num}:")
                print(f"   Occurrences totales : {stats['total_occurrences']}")
                print(f"   Fréquence relative : {stats['frequence']:.1f}%")
                print(f"   Dernière apparition : {stats['ecart_actuel']} courses")
                print(f"   Écart maximum       : {stats['ecart_max']} courses")

                # Affichage des 3 dernières dates d'apparition
                if stats['occurrences']:
                    derniers_dates = ", ".join(stats['occurrences'][-3:])
                    print(f"   Dernières apparitions: {derniers_dates}")

                print("-" * 60)

        except (ValueError, IndexError):
            print("\n❌ Sélection invalide - Veuillez entrer un numéro de la liste")
        except Exception as e:
            print(f"\n⚠️ Erreur inattendue : {str(e)}")

    def afficher_ecarts_quatriemes_synthese_filtres(self):
        """Version améliorée avec gestion des erreurs et meilleur parsing"""
        try:
            # Récupération dynamique des options
            disciplines = ['Toutes'] + self.obtenir_disciplines_disponibles()
            distances = ['Toutes'] + self.obtenir_distances_disponibles()

            # Sélection discipline
            print("\n=== DISCIPLINES DISPONIBLES ===")
            for i, d in enumerate(disciplines):
                print(f"{i}. {d}")
            choix_d = int(input("Choix (numéro) : "))
            discipline = None if choix_d == 0 else disciplines[choix_d]

            # Sélection distance
            print("\n=== DISTANCES DISPONIBLES ===")
            for i, d in enumerate(distances):
                print(f"{i}. {d}")
            choix_dist = int(input("Choix (numéro) : "))
            distance = None if choix_dist == 0 else distances[choix_dist]

            # Filtrage des courses
            courses = self.db.get_courses()
            if discipline:
                courses = [c for c in courses if c.get('type_course') == discipline]
            if distance:
                courses = [c for c in courses if c.get('distance') == distance]

            if not courses:
                print("\n⚠️ Aucune course correspondante")
                return

            # Calcul des écarts pour les deuxièmes places
            ecarts = calculer_ecarts_quatriemes_synthese(courses)

            if not ecarts:
                print("\nℹ️ Aucun numéro n'a terminé deuxième dans ces courses")
                return

            # Affichage détaillé
            print(f"\n📊 ANALYSE DES QUATRIEMES - {len(courses)} courses")
            print(f"Discipline: {discipline or 'Toutes'} | Distance: {distance or 'Toutes'}")
            print("-" * 60)

            # Tri par numéro avec gestion des plages complètes
            for num in sorted(ecarts.keys()):
                stats = ecarts[num]
                print(f"▶ Numéro {num}:")
                print(f"   Occurrences totales : {stats['total_occurrences']}")
                print(f"   Fréquence relative : {stats['frequence']:.1f}%")
                print(f"   Dernière apparition : {stats['ecart_actuel']} courses")
                print(f"   Écart maximum       : {stats['ecart_max']} courses")

                # Affichage des 3 dernières dates d'apparition
                if stats['occurrences']:
                    derniers_dates = ", ".join(stats['occurrences'][-3:])
                    print(f"   Dernières apparitions: {derniers_dates}")

                print("-" * 60)

        except (ValueError, IndexError):
            print("\n❌ Sélection invalide - Veuillez entrer un numéro de la liste")
        except Exception as e:
            print(f"\n⚠️ Erreur inattendue : {str(e)}")

    def afficher_ecarts_cinquiemes_synthese_filtres(self):
        """Version améliorée avec gestion des erreurs et meilleur parsing"""
        try:
            # Récupération dynamique des options
            disciplines = ['Toutes'] + self.obtenir_disciplines_disponibles()
            distances = ['Toutes'] + self.obtenir_distances_disponibles()

            # Sélection discipline
            print("\n=== DISCIPLINES DISPONIBLES ===")
            for i, d in enumerate(disciplines):
                print(f"{i}. {d}")
            choix_d = int(input("Choix (numéro) : "))
            discipline = None if choix_d == 0 else disciplines[choix_d]

            # Sélection distance
            print("\n=== DISTANCES DISPONIBLES ===")
            for i, d in enumerate(distances):
                print(f"{i}. {d}")
            choix_dist = int(input("Choix (numéro) : "))
            distance = None if choix_dist == 0 else distances[choix_dist]

            # Filtrage des courses
            courses = self.db.get_courses()
            if discipline:
                courses = [c for c in courses if c.get('type_course') == discipline]
            if distance:
                courses = [c for c in courses if c.get('distance') == distance]

            if not courses:
                print("\n⚠️ Aucune course correspondante")
                return

            # Calcul des écarts pour les deuxièmes places
            ecarts = calculer_ecarts_cinquiemes_synthese(courses)

            if not ecarts:
                print("\nℹ️ Aucun numéro n'a terminé deuxième dans ces courses")
                return

            # Affichage détaillé
            print(f"\n📊 ANALYSE DES CINQUIEMES - {len(courses)} courses")
            print(f"Discipline: {discipline or 'Toutes'} | Distance: {distance or 'Toutes'}")
            print("-" * 60)

            # Tri par numéro avec gestion des plages complètes
            for num in sorted(ecarts.keys()):
                stats = ecarts[num]
                print(f"▶ Numéro {num}:")
                print(f"   Occurrences totales : {stats['total_occurrences']}")
                print(f"   Fréquence relative : {stats['frequence']:.1f}%")
                print(f"   Dernière apparition : {stats['ecart_actuel']} courses")
                print(f"   Écart maximum       : {stats['ecart_max']} courses")

                # Affichage des 3 dernières dates d'apparition
                if stats['occurrences']:
                    derniers_dates = ", ".join(stats['occurrences'][-3:])
                    print(f"   Dernières apparitions: {derniers_dates}")

                print("-" * 60)

        except (ValueError, IndexError):
            print("\n❌ Sélection invalide - Veuillez entrer un numéro de la liste")
        except Exception as e:
            print(f"\n⚠️ Erreur inattendue : {str(e)}")

    

    def visualiser_resultats(self, resultats, position):
        """Visualisation avancée avec gestion des écarts spéciaux"""
        if not resultats or 'ecarts' not in resultats:
            print("Aucune donnée à visualiser")
            return

        try:
            plt.figure(figsize=(14, 7))
            ax = plt.gca()
            
            # Configuration des couleurs
            colors = []
            labels = []
            ecarts = sorted(resultats['ecarts'].items())
            
            for gap, count in ecarts:
                if gap == resultats['ecart_initial']:
                    colors.append('orange')
                    labels.append('Écart initial')
                elif gap == resultats['ecart_actuel']:
                    colors.append('red')
                    labels.append('Écart actuel')
                else:
                    colors.append('skyblue')
                    labels.append('Écart intermédiaire')

            # Création du graphique
            x = np.arange(len(ecarts))
            bars = ax.bar(x, [count for gap, count in ecarts], color=colors)
            
            # Configuration des axes
            ax.set_xticks(x)
            ax.set_xticklabels([str(gap) for gap, count in ecarts])
            ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
            
            # Ajout des annotations
            for rect in bars:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height,
                        f'{int(height)}', 
                        ha='center', va='bottom')

            # Légende personnalisée
            legend_elements = [
                Line2D([0], [0], color='orange', lw=4, label='Écart initial'),
                Line2D([0], [0], color='red', lw=4, label='Écart actuel'),
                Line2D([0], [0], color='skyblue', lw=4, label='Écarts intermédiaires')
            ]
            
            ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
            
            # Titre et labels
            plt.title(
                f"Analyse complète du numéro {resultats['numero']}\n"
                f"Position : {resultats['position']} | "
                f"Écart actuel: {resultats['ecart_actuel']} courses", 
                pad=20, fontsize=14
            )
            
            plt.xlabel("Valeurs des écarts (en nombre de courses)", fontsize=12)
            plt.ylabel("Nombre d'occurrences", fontsize=12)
            
            # Grille et présentation
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Erreur de visualisation : {str(e)}")
            import traceback
            traceback.print_exc()

    def visualiser_resultats_combines(self, resultats, positions_description):
        """Visualisation avancée pour les résultats combinés des écarts"""
        if not resultats or 'ecarts' not in resultats:
            print("Aucune donnée à visualiser")
            return

        try:
            plt.figure(figsize=(14, 7))
            ax = plt.gca()

            # Configuration des couleurs
            colors = []
            labels = []
            ecarts = sorted(resultats['ecarts'].items())

            for gap, count in ecarts:
                if gap == resultats['ecart_initial']:
                    colors.append('orange')
                    labels.append('Écart initial')
                elif gap == resultats['ecart_actuel']:
                    colors.append('red')
                    labels.append('Écart actuel')
                else:
                    colors.append('skyblue')
                    labels.append('Écart intermédiaire')

            # Création du graphique
            x = np.arange(len(ecarts))
            bars = ax.bar(x, [count for gap, count in ecarts], color=colors)

            # Configuration des axes
            ax.set_xticks(x)
            ax.set_xticklabels([str(gap) for gap, count in ecarts])
            ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

            # Ajout des annotations
            for rect in bars:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')

            # Légende personnalisée
            legend_elements = [
                Line2D([0], [0], color='orange', lw=4, label='Écart initial'),
                Line2D([0], [0], color='red', lw=4, label='Écart actuel'),
                Line2D([0], [0], color='skyblue', lw=4, label='Écarts intermédiaires')
            ]

            ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

            # Titre et labels
            plt.title(
                f"Analyse combinée du numéro {resultats['numero']}\n"
                f"Positions : {positions_description} | "
                f"Écart actuel: {resultats['ecart_actuel']} courses",
                pad=20, fontsize=14
            )

            plt.xlabel("Valeurs des écarts (en nombre de courses)", fontsize=12)
            plt.ylabel("Nombre d'occurrences", fontsize=12)

            # Grille et présentation
            plt.grid(axis='y', alpha=0.3, linestyle='--')
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Erreur de visualisation : {str(e)}")
            import traceback
            traceback.print_exc()

    def exporter_resultats(self, resultats, nom_fichier=None):
        """
        Exporte les résultats d'analyse au format CSV avec des améliorations
        
        :param resultats: Dictionnaire des résultats à exporter
        :param nom_fichier: Nom du fichier de sortie (optionnel)
        """
        if not resultats or 'apparitions' not in resultats:
            print("❌ Aucune donnée valide à exporter")
            return 
        
        # Génération dynamique du nom de fichier si non fourni
        if nom_fichier is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = r"C:\Users\Cedric\Desktop\geny\export_ecarts_numero_{resultats['numero']}_{timestamp}.csv"
        

        try:
            with open(nom_fichier, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                
                # En-tête principal avec informations résumées
                writer.writerow([
                    '=== RÉSUMÉ DE L\'ANALYSE ===',
                    f"Numéro: {resultats['numero']}",
                    f"Position: {resultats['position']}",
                    f"Total Apparitions: {resultats['total_apparitions']}"
                ])
                writer.writerow([]) # Ligne vide pour séparation
                
                # En-tête des colonnes détaillées
                writer.writerow([
                    'Numéro', 'Position', 'Date', 'Course ID', 
                    'Écart depuis dernière', 'Écart initial', 
                    'Écart actuel', 'Écart moyen'
                ])
                
                # Ajout de statistiques supplémentaires
                writer.writerow([
                    resultats['numero'],
                    resultats['position'],
                    'STATISTIQUES',
                    f"Écart max: {resultats.get('ecart_max', 'N/A')}",
                    f"Écart min: {resultats.get('ecart_min', 'N/A')}",
                    f"Écart moyen interne: {resultats.get('ecart_moyen_interne', 'N/A')}",
                    f"Écart actuel: {resultats['ecart_actuel']}",
                    f"Écart moyen complet: {round(resultats['ecart_moyen_complet'], 2)}"
                ])
                writer.writerow([]) # Ligne vide pour séparation
                
                # Données des apparitions
                for app in resultats['apparitions']:
                    writer.writerow([
                        resultats['numero'],
                        resultats['position'],
                        app['date'],
                        app['course_id'],
                        app.get('depuis_derniere', 'N/A'),
                        resultats['ecart_initial'],
                        resultats['ecart_actuel'],
                        round(resultats['ecart_moyen_complet'], 2)
                    ])
                
                # Ajout de la distribution des écarts
                writer.writerow([]) # Ligne vide pour séparation
                writer.writerow(['=== DISTRIBUTION DES ÉCARTS ==='])
                writer.writerow(['Écart', 'Nombre d\'occurrences'])
                
                for ecart, count in sorted(resultats['ecarts'].items()):
                    writer.writerow([ecart, count])

            # Ajout d'informations supplémentaires dans le log
            logging.info(f"Export réussi pour le numéro {resultats['numero']} en position {resultats['position']}")
            
            print(f"✅ Données exportées avec succès dans {nom_fichier}")
            
            # Option d'ouverture du fichier (selon votre environnement)
            try:
                import os
                if input("Voulez-vous ouvrir le fichier ? (o/n) ").lower() == 'o':
                    os.startfile(nom_fichier)
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Erreur lors de l'export : {str(e)}")
            logging.error("Erreur export CSV", exc_info=True)

        return nom_fichier  # Retourne le nom du fichier pour une utilisation ultérieure si nécessaire
    
    def preparer_donnees_prediction(self):
        """Prépare les données pour le modèle de prédiction"""
        courses = self.db.recuperer_courses()  # Utilise la méthode existante
        return preparer_donnees_ml(courses)

    def executer_prediction(self):
        """Version corrigée avec gestion d'erreur améliorée"""
        try:
            X, y = self.preparer_donnees_prediction()
            if len(X) == 0:
                print("Aucune donnée disponible pour l'entraînement")
                return

            # Entraîner avec le nouvel encodage
            model, encoder = entrainer_modele(X, y)
            
            # Vérifier la cohérence des données
            if not hasattr(model, 'classes_'):
                print("Erreur: Modèle non entraîné correctement")
                return
            print("\n=== Prédictions en temps réel ===")
            self.afficher_prediction_interactive(model)
            
        except ValueError as e:
            print(f"Erreur de conversion : {str(e)}")
        except Exception as e:
            print(f"Erreur générale : {str(e)}")