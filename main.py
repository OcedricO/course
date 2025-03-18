 #main.py
import logging
import pandas as pd
import matplotlib as mpl
import os
import sys
import streamlit as st
import numpy as np
from gestionnaire_courses import GestionnaireCourses
from analyse import (
    afficher_courbe_numeros_communs, afficher_courbe_syntheses_communes, afficher_graphique_tranches_synthese,analyser_ecarts_synthese,calculer_ecarts_numeros_arrivee_avec_participation, analyser_premiers_paire_impaire, analyser_tierce_paire_impaire, analyser_deuxieme_paire_impaire, analyser_troisieme_paire_impaire, analyser_quatrieme_paire_impaire, analyser_cinquieme_paire_impaire, analyser_paire_impaire_par_tranche_synthese, analyser_quinte_paire_impaire, analyse_ecart_finissant_premier, analyse_ecart_finissant_deuxieme, analyse_ecart_finissant_troisieme, analyse_ecart_position_generique, analyse_ecart_positions_combinees)
from prediction import ( entrainer_modele, entrainer_modele_tranche_1_5, preparer_donnees_tranche_1_5, predire_tranche_1_5)
from database import Database
from statistiques import (AnalyseStatistiqueAvancee, AnalyseTemporelle)
from prediction_avancee import (InterfaceUtilisateur, SystemePredictionGlobal)
from matplotlib.lines import Line2D
from collections import defaultdict, Counter
from analyse_interactive import analyse_interactive_arrivees
from ml_predictions import preparer_donnees_ml, entrainer_modele
from prediction_interactive import InteractivePredictor, PredictiveEngine


logging.basicConfig(level=logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

def afficher_menu_principal():
    """Affiche le menu principal avec toutes les options."""
    print("\n=== Menu Principal ===")
    print("1. Traiter les nouveaux fichiers")
    print("2. Analyser les positions de synthèse")
    print("3. Analyser les positions de l'arrivée")
    print("4. Voir les statistiques globales")
    print("5. Analyse Synthèse")
    print("6. Analyse Arrivée")
    print("7. Prédire les résultats")
    print("8. Prédire les numéros dans la tranche 1-5")
    print("9. Concordance de numéros")
    print("10. Concordance avec 2 numéros")  
    print("11. Tiercé Synthèse")
    print("12. Analyses statistiques avancées")
    print("13. Prédictions Avancées")
    print("14. Paire ou Impaire")
    print("15. Fréquence écart synthèse par numéro")
    print("16. Analyse interactive des arrivées")  # Nouvelle option
    print("17. Quitter")

def afficher_sous_menu_analyse_arrivee(gestionnaire):
    while True:
        print("\n=== Sous-menu Analyse Arrivée ===")
        print("1. Fréquence des numéros dans l'arrivée")
        print("2. Fréquence des couples de numéros dans l'arrivée")
        print("3. Fréquence des triples de numéros dans l'arrivée")
        print("4. Fréquence des écarts entre les numéros dans l'arrivée")
        print("5. Écarts pour chaque numéro dans l'arrivée")
        print("6. Écarts pour chaque couple de numéros dans l'arrivée")
        print("7. Écarts pour chaque triple de numéros dans l'arrivée")
        print("8. Analyse par discipline")
        print("9. Analyse par discipline et distance")
        print("10. Comparer les deux dernières arrivées")
        print("11. Retour au menu principal")
        choix = input("Choix : ").strip()

        if choix == "1":
            gestionnaire.afficher_frequence_arrivee()
        elif choix == "2":
            gestionnaire.afficher_frequence_couples_arrivee()
        elif choix == "3":
            gestionnaire.afficher_frequence_triples_arrivee()
        elif choix == "4":
            gestionnaire.afficher_frequence_ecarts_arrivee()
        elif choix == "5":
            gestionnaire.afficher_ecarts_numeros_arrivee()
        elif choix == "6":
            gestionnaire.afficher_ecarts_couples_arrivee()
        elif choix == "7":
            gestionnaire.afficher_ecarts_triples_arrivee()
        elif choix == "8":
            discipline = gestionnaire.choisir_discipline()
            if discipline:
                gestionnaire.analyser_par_discipline(type_course=discipline, analyse_type="arrivée")
        elif choix == "9":
            discipline_distance = gestionnaire.choisir_discipline_et_distance()
            if discipline_distance:
                discipline, distance = discipline_distance
                gestionnaire.analyser_par_discipline(type_course=discipline, distance=distance, analyse_type="arrivée")
        elif choix == "10":
            courses = gestionnaire.db.get_courses()
            if len(courses) < 2:
                print("Pas assez de courses pour comparer les arrivées.")
            else:
                from analyse import afficher_courbe_numeros_communs
                afficher_courbe_numeros_communs(courses)
        elif choix == "11":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def afficher_sous_menu_analyse_filtree(gestionnaire, discipline: str, distance: str):
    """
    Affiche un sous-menu pour l'analyse des données filtrées par discipline et distance.
    :param gestionnaire: Instance du gestionnaire de courses.
    :param discipline: Discipline sélectionnée.
    :param distance: Distance sélectionnée.
    """
    while True:
        print(f"\n=== Analyse filtrée : {discipline} - {distance} ===")
        print("1. Fréquence des numéros dans la synthèse")
        print("2. Fréquence des couples de numéros dans la synthèse")
        print("3. Fréquence des triples de numéros dans la synthèse")
        print("4. Fréquence des écarts entre les numéros dans la synthèse")
        print("5. Écarts pour chaque numéro dans la synthèse")
        print("6. Écarts pour chaque couple de numéros dans la synthèse")
        print("7. Écarts pour chaque triple de numéros dans la synthèse")
        print("8. Retour au menu précédent")
        choix = input("Choix : ").strip()

        if choix == "1":
            gestionnaire.afficher_frequence_synthese(type_course=discipline, distance=distance)
        elif choix == "2":
            gestionnaire.afficher_frequence_couples(type_course=discipline, distance=distance)
        elif choix == "3":
            gestionnaire.afficher_frequence_triples(type_course=discipline, distance=distance)
        elif choix == "4":
            gestionnaire.analyser_ecarts_synthese(type_course=discipline, distance=distance)
        elif choix == "5":
            gestionnaire.afficher_frequence_ecarts(type_course=discipline, distance=distance)
        elif choix == "6":
            gestionnaire.afficher_ecarts_couples_filtres(type_course=discipline, distance=distance)
        elif choix == "7":
            gestionnaire.afficher_ecarts_triples_filtres(type_course=discipline, distance=distance)
        elif choix == "8":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def afficher_sous_menu_analyse_synthese(gestionnaire):
    """Affiche le sous-menu pour l'analyse de la synthèse."""
    while True:
        print("\n=== Sous-menu Analyse Synthèse ===")
        print("1. Fréquence des numéros dans la synthèse")
        print("2. Fréquence des couples de numéros dans la synthèse")
        print("3. Fréquence des triples de numéros dans la synthèse")
        print("4. Fréquence des écarts entre les numéros dans la synthèse")
        print("5. Écarts pour chaque numéro dans la synthèse")
        print("6. Écarts pour chaque couple de numéros dans la synthèse")
        print("7. Écarts pour chaque triple de numéros dans la synthèse")
        print("8. Analyse par discipline")
        print("9. Analyse par discipline et distance")
        print("10. Comparer les deux dernières synthèses")
        print("11. Analyse par tranche de 5-5-reste pour le quinte")  # Nouvelle option
        print("12. Analyse par tranche de 5-5-reste pour le tierce")  # Nouvelle option
        print("13. Retour au menu principal")  # Option "Retour" décalée
        choix = input("Choix : ").strip()

        if choix == "1":
            gestionnaire.afficher_frequence_synthese()
        elif choix == "2":
            gestionnaire.afficher_frequence_couples()
        elif choix == "3":
            gestionnaire.afficher_frequence_triples()
        elif choix == "4":
            gestionnaire.afficher_frequence_ecarts()
        elif choix == "5":
            gestionnaire.afficher_ecarts_numeros()
        elif choix == "6":
            gestionnaire.afficher_ecarts_couples_filtres()
        elif choix == "7":
            gestionnaire.afficher_ecarts_triples_filtres()
        elif choix == "8":
            discipline = gestionnaire.choisir_discipline()
            if discipline:
                gestionnaire.analyser_par_discipline(type_course=discipline, analyse_type="synthèse")
        elif choix == "9":
            discipline_distance = gestionnaire.choisir_discipline_et_distance()
            if discipline_distance:
                discipline, distance = discipline_distance
                gestionnaire.analyser_par_discipline(type_course=discipline, distance=distance, analyse_type="synthèse")
        elif choix == "10":
            courses = gestionnaire.db.get_courses()
            if len(courses) < 2:
                print("Pas assez de courses pour comparer les synthèses.")
            else:
                from analyse import afficher_courbe_syntheses_communes
                afficher_courbe_syntheses_communes(courses)
        elif choix == "11":  # Nouvelle option
            afficher_sous_menu_tranches_synthese(gestionnaire)
        elif choix == "12":  # Nouvelle option
            afficher_sous_menu_tranches_synthese_tierce(gestionnaire)
            #gestionnaire.analyser_tranches_synthese_tierce()
        elif choix == "13":  # Option "Retour" décalée
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def afficher_sous_menu_tranches_synthese(gestionnaire):
    """Affiche le sous-menu pour l'analyse par tranche de 5-5-reste."""
    while True:
        print("\n=== Sous-menu Analyse par tranche de 5-5-reste ===")
        print("1. Analyse globale (toutes les courses)")
        print("2. Analyse par discipline")
        print("3. Analyse par discipline et distance")
        print("4. Retour au menu précédent")
        choix = input("Choix : ").strip()

        if choix == "1":
            gestionnaire.analyser_tranches_synthese()
        elif choix == "2":
            discipline = gestionnaire.choisir_discipline()
            if discipline:
                gestionnaire.analyser_tranches_synthese_par_discipline(discipline)
        elif choix == "3":
            discipline_distance = gestionnaire.choisir_discipline_et_distance()
            if discipline_distance:
                discipline, distance = discipline_distance
                gestionnaire.analyser_tranches_synthese_par_discipline_et_distance(discipline, distance)
        elif choix == "4":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")
def afficher_sous_menu_tranches_synthese_tierce(gestionnaire):
    """Affiche le sous-menu pour l'analyse par tranche de 5-5-reste."""
    while True:
        print("\n=== Sous-menu Analyse par tranche de 5-5-reste ===")
        print("1. Analyse globale (toutes les courses)")
        print("2. Analyse par discipline")
        print("3. Analyse par discipline et distance")
        print("4. Retour au menu précédent")
        choix = input("Choix : ").strip()

        if choix == "1":
            gestionnaire.analyser_tranches_synthese_tierce()
        elif choix == "2":
            discipline = gestionnaire.choisir_discipline()
            if discipline:
                gestionnaire.analyser_tranches_synthese_tierce_par_discipline(discipline)
        elif choix == "3":
            discipline_distance = gestionnaire.choisir_discipline_et_distance()
            if discipline_distance:
                discipline, distance = discipline_distance
                gestionnaire.analyser_tranches_synthese_tierce_par_discipline_et_distance(discipline, distance)
        elif choix == "4":
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

def choisir_discipline(gestionnaire):
    """Permet à l'utilisateur de choisir une discipline."""
    disciplines = gestionnaire.obtenir_disciplines_disponibles()
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

def choisir_distance(gestionnaire):
    """Permet à l'utilisateur de choisir une distance."""
    distances = gestionnaire.obtenir_distances_disponibles()
    if not distances:
        print("Aucune distance disponible.")
        return None

    print("\n=== Choisir une distance ===")
    for i, distance in enumerate(distances, start=1):
        print(f"{i}. {distance}")
    print(f"{len(distances) + 1}. Retour au menu précédent")

    choix = input("Choix : ").strip()
    if choix.isdigit() and 1 <= int(choix) <= len(distances):
        return distances[int(choix) - 1]
    elif choix == str(len(distances) + 1):
        return None
    else:
        print("Choix invalide. Veuillez réessayer.")
        return None

def afficher_sous_menu_disciplines_et_distances(gestionnaire):
    """
    Affiche un sous-menu pour choisir une discipline et une distance.
    Retourne un tuple (discipline, distance) ou None si l'utilisateur annule.
    """
    disciplines = gestionnaire.obtenir_disciplines_disponibles()
    distances = gestionnaire.obtenir_distances_disponibles()

    if not disciplines or not distances:
        print("Aucune discipline ou distance disponible.")
        return None

    # Choix de la discipline
    print("\n=== Choisir une discipline ===")
    for i, discipline in enumerate(disciplines, start=1):
        print(f"{i}. {discipline}")
    print(f"{len(disciplines) + 1}. Retour au menu précédent")

    choix_discipline = input("Choix de la discipline : ").strip()
    if choix_discipline.isdigit() and 1 <= int(choix_discipline) <= len(disciplines):
        discipline_selectionnee = disciplines[int(choix_discipline) - 1]

        # Choix de la distance
        print("\n=== Choisir une distance ===")
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

def sous_menu_tierce_synthese(gestionnaire):
    """Sous-menu pour analyser un numéro spécifique"""
    try:
        numero = int(input("\nEntrez le numéro à analyser : "))
    except ValueError:
        print("❌ Le numéro doit être un entier")
        return
    filters = {}  # Initialisation cruciale

    print("\n=== Filtres Disponibles ===")
    print("1. Toutes courses")
    print("2. Par type de course")
    print("3. Type + distance")
    print("4. Par lieu")
    choix = input("Choix : ").strip()

    if choix == "2":
        discipline = gestionnaire.choisir_discipline()
        if discipline:
            filters['type_course'] = discipline
    elif choix == "3":
        discipline_distance = gestionnaire.choisir_discipline_et_distance()
        if discipline_distance:
            filters['type_course'], filters['distance'] = discipline_distance
    elif choix == "4":
        lieu = input("Entrez le lieu : ").strip()
        if lieu:
            filters['lieu'] = lieu
    # ... (logique des filtres identique)

    resultats = gestionnaire.analyser_numero_synthese(numero, filters)

    print(f"\n=== Analyse du numéro {numero} ===")
    print(f"Présence dans le top3 : {resultats['presence_top3']}/{resultats['total_courses']}")
    print(f"Écart actuel : {resultats['ecarts']['actuel']} courses")
    print(f"Écart maximum : {resultats['ecarts']['max']} courses")

    if resultats['presence_top3'] > 0:
        print("\n🔗 Combinaisons avec le numéro analysé :")
    print("Paires :")
    for (a, b), count in sorted(resultats['paires_avec_cible'].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {a}-{b} : {count}x")

    print("\nTriplets complets :")
    for (a, b, c), count in sorted(resultats['triplets'].items(), key=lambda x: (-x[1], x[0]))[:5]:
        print(f"  {a}-{b}-{c} : {count}x")

    # Appel de la nouvelle fonction pour l'analyse combinée
    courses = gestionnaire.obtenir_courses_filtrees(filters)  # Utilisation de la nouvelle méthode
    stats_combined = analyse_ecart_positions_combinees(courses, numero, positions=[0, 1, 2])
    if stats_combined:
        print(f"\n=== NUMÉRO {numero} EN positions {' ou '.join([str(p+1) for p in [0, 1, 2]])} ===")
        print(f"Apparu {stats_combined['total_apparitions']} fois sur {len(courses)} courses analysées")
        print(f"Écart initial : {stats_combined['ecart_initial']} courses")
        print(f"Écart actuel : {stats_combined['ecart_actuel']} courses")
        print(f"Écart moyen complet : {stats_combined['ecart_moyen_complet']:.1f} courses")
        print(f"Écart moyen entre apparitions : {stats_combined['ecart_moyen_interne']:.1f} courses")

        # Appel de la nouvelle fonction de visualisation
        gestionnaire.visualiser_resultats_combines(stats_combined, positions_description="1 ou 2 ou 3")

def sous_menu_statistiques_avancees(gestionnaire):
    from statistiques import AnalyseStatistiqueAvancee
    analyseur = AnalyseStatistiqueAvancee(gestionnaire)
    
    while True:
        print("\n=== Analyses Statistiques Avancées ===")
        print("1. Analyse par parité")
        print("2. Analyse par plages de numéros")
        print("3. Analyse des écarts critiques")
        print("4. Rapport complet avec visualisations")
        print("5. Analyses temporelles")  # Nouvelle option
        print("6. Retour au menu principal")
        choix = input("Choix : ").strip()
        
        try:
            if choix == "1":
                result = analyseur.analyser_parite()
                print("\n=== Résultats Analyse Parité ===")
                print(pd.DataFrame.from_dict(result, orient='index'))
                
            elif choix == "2":
                result = analyseur.analyser_plages()
                print("\n=== Analyse par Plages de Numéros ===")
                print(result)
                
            elif choix == "3":
                result = analyseur.analyser_ecarts()
                print("\n=== Analyse des Écarts Critiques ===")
                for k, v in result.items():
                    print(f"{k}: {v}")
                    
            elif choix == "4":
                rapport = analyseur.generer_rapport_complet()
                print("\n=== Rapport Consolidé ===")
                print("Données clés :")
                print(f"- Nombre total d'observations : {len(analyseur.data)}")
                correlation = rapport['ecarts'].get('correlation', 0.0)
                if not np.isnan(correlation):
                    print(f"- Corrélation écart/performance : {correlation:.2%}")
                else:
                    print("- Corrélation : données insuffisantes")
                
            elif choix == "5":  # Nouveau sous-menu temporel
                sous_menu_analyses_temporelles(analyseur)
                
            elif choix == "6":
                return
                
            else:
                print("Choix invalide. Veuillez réessayer.")
                
            #else:
            #    print("Choix invalide. Veuillez réessayer.")


        except KeyboardInterrupt:
            print("\nRetour au menu principal.")
            return  # Retour explicite
               
        except Exception as e:
            print(f"Erreur lors de l'analyse : {str(e)}")
            logging.error("Erreur dans les statistiques avancées", exc_info=True)
            break

def sous_menu_analyses_temporelles(analyseur):
    """Nouveau sous-menu pour les analyses temporelles"""
    while True:
        print("\n=== Analyses Temporelles ===")
        print("1. Évolution quotidienne d'un numéro")
        print("2. Tendances hebdomadaires")
        print("3. Périodes de performance")
        print("4. Visualiser l'évolution graphique")
        print("5. Retour au menu précédent")
        choix = input("Choix : ").strip()

        try:
            if choix == "1":
                num = int(input("Numéro à analyser : "))
                result = analyseur.analyse_temporelle.evolution_quotidienne(num)
                print("\nÉvolution quotidienne :")
                print(result.to_string(index=False))
                
            elif choix == "2":
                result = analyseur.analyse_temporelle.tendances_hebdomadaires()
                print("\nTendances hebdomadaires :")
                print(result.to_string(index=False))
                
            elif choix == "3":
                num = int(input("Numéro à analyser : "))
                result = analyseur.analyse_temporelle.periodes_performances(num)
                print("\nPériodes clés :")
                if num in result:
                    print(f"Meilleure période : {result[num]['meilleure_periode']}")
                    print(f"Pire période : {result[num]['pire_periode']}")
                else:
                    print("Pas assez de données pour ce numéro")
                    
            elif choix == "4":
                num = input("Numéro (laisser vide pour tous) : ")
                if num.isdigit():
                    analyseur.analyse_temporelle.visualiser_evolution(int(num))
                else:
                    analyseur.analyse_temporelle.visualiser_evolution()
                    
            elif choix == "5":
                break
                
            else:
                print("Choix invalide. Veuillez réessayer.")

        except ValueError:
            print("Erreur : Veuillez entrer un numéro valide")
        except Exception as e:
            print(f"Erreur d'analyse : {str(e)}")

def sous_menu_prediction_avancee(gestionnaire):
    """Nouveau sous-menu pour les prédictions avancées"""
    from statistiques import AnalyseStatistiqueAvancee
    analyseur = AnalyseStatistiqueAvancee(gestionnaire)
    
    while True:
        print("\n=== Prédictions Avancées ===")
        print("1. Prédire pour un numéro")
        print("2. Interface Avancée (Streamlit)")
        print("3. Retour")
        choix = input("Choix : ").strip()

        if choix == "1":
            num = int(input("Numéro à analyser : "))
            rapport = analyseur.generer_prediction(num)
            print(f"\nRapport de prédiction : {rapport}")
            
        elif choix == "2":
            lancer_interface_streamlit(gestionnaire)
            
        elif choix == "3":
            return
        
def afficher_sous_menu_paire_impaire(gestionnaire):
    while True:
        print("\n=== Sous-menu Paire/Impaire ===")
        print("1. Analyse du premier")  # Menu principal modifié
        print("2. Analyse des tiercés")
        print("3. Analyse des quintés")   
        print("4. Pair/Impair par tranche Synthèse")
        print("5. Retour au menu principal")
        choix = input("Choix : ").strip()

        if choix == "1":
            afficher_sous_menu_premier(gestionnaire)  # Nouveau sous-menu
        elif choix == "2":
            courses = gestionnaire.db.get_courses()
            analyser_tierce_paire_impaire(courses)
        elif choix == "3":
            courses = gestionnaire.db.get_courses()
            analyser_quinte_paire_impaire(courses)
        elif choix == "4":
            afficher_sous_menu_tranche_synthese(gestionnaire)
        elif choix == "5":
            break
        else:
            print("Choix invalide.")

def afficher_sous_menu_premier(gestionnaire):
    """Nouveau sous-menu pour les analyses de la première place"""
    while True:
        print("\n=== ANALYSE DU PREMIER ===")
        print("1. Analyse pair/impair arrivée")       
        print("2. Analyse premier en fonction de l ordre de la synthèse")
        print("3. Analyse deuxieme en fonction de l ordre de la synthèse")
        print("4. Analyse troisieme en fonction de l ordre de la synthèse")
        print("5. Analyse quatrieme en fonction de l ordre de la synthèse")
        print("6. Analyse cinquieme en fonction de l ordre de la synthèse")
        print("7. Retour au menu précédent")
        choix = input("Choix : ").strip()

        if choix == "1":
            courses = gestionnaire.db.get_courses()
            analyser_premiers_paire_impaire(courses)
            analyser_deuxieme_paire_impaire(courses)
            analyser_troisieme_paire_impaire(courses)
            analyser_quatrieme_paire_impaire(courses)
            analyser_cinquieme_paire_impaire(courses)


        elif choix == "2":
            gestionnaire.afficher_ecarts_premiers_synthese_filtres()
        elif choix == "3":
            gestionnaire.afficher_ecarts_deuxiemes_synthese_filtres()
        elif choix == "4":
            gestionnaire.afficher_ecarts_troisiemes_synthese_filtres()
        elif choix == "5":
            gestionnaire.afficher_ecarts_quatriemes_synthese_filtres()
        elif choix == "6":
            gestionnaire.afficher_ecarts_cinquiemes_synthese_filtres()
            
        elif choix == "7":
            break
        else:
            print("Choix invalide.")


def afficher_sous_menu_tranche_synthese(gestionnaire):
    """Sous-menu complet avec toutes les options"""
    while True:
        print("\n=== Analyse Pair/Impair par tranche Synthèse ===")
        print("1. Toutes les courses")
        print("2. 15 dernières courses")
        print("3. 30 dernières courses")
        print("4. Filtrer par type et distance")
        print("5. Retour au menu précédent")
        choix = input("Choix : ").strip()

        if choix == "1":
            courses = gestionnaire.db.get_courses()
            gestionnaire.analyser_paire_impaire_par_tranche_synthese(courses)
        elif choix == "2":
            gestionnaire.analyser_15_dernieres_courses()
        elif choix == "3":
            gestionnaire.analyser_30_dernieres_courses()
        elif choix == "4":
            gestionnaire.selectionner_type_et_distance()

        elif choix == "5":
            break
        else:
            print("Choix invalide.")
def lancer_interface_streamlit(gestionnaire):
    """Lancement de l'interface Streamlit"""
    from statistiques import AnalyseStatistiqueAvancee
    import subprocess

    analyseur = AnalyseStatistiqueAvancee(gestionnaire)
    systeme = SystemePredictionGlobal(analyseur.data)

    # Écriture d'un script temporaire
    with open("streamlit_app.py", "w") as f:
        f.write(f"""
from prediction_avancee import InterfaceUtilisateur, SystemePredictionGlobal
import pandas as pd
import sqlite3
# Connexion à la base de données SQLite
conn = sqlite3.connect('courses.db')
# Remplacez 'courses' par le nom réel de la table à lire
data = pd.read_sql_query("SELECT * FROM courses", conn)
conn.close()
systeme = SystemePredictionGlobal(data)
InterfaceUtilisateur(systeme).afficher_interface()
        """)
        
        subprocess.run(["streamlit", "run", "streamlit_app.py", "--server.port", "8502"])

def menu_frequence_ecart_synthese(gestionnaire):
    resultats = None  # Variable pour stocker les derniers résultats
    
    while True:
        print("\n=== Fréquence écart synthèse par numéro ===")
        print("1. Fréquence par numéro synthèse finissant premier")
        print("2. Numéro synthèse finissant deuxième")
        print("3. Numéro synthèse finissant troisième")
        print("4. Exporter les résultats")
        print("5. Retour au menu principal")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            numero = int(input("Entrez le numéro à analyser pour le premier : "))
            courses = gestionnaire.db.get_courses()
            resultats = analyse_ecart_position_generique(courses, numero, 0)
            gestionnaire.visualiser_resultats(resultats, "Premier")
        elif choix == "2":
            numero = int(input("Entrez le numéro à analyser pour le deuxième : "))
            courses = gestionnaire.db.get_courses()
            resultats = analyse_ecart_position_generique(courses, numero, 1)
            gestionnaire.visualiser_resultats(resultats, "Deuxième")
        elif choix == "3":
            numero = int(input("Entrez le numéro à analyser pour le troisieme : "))
            courses = gestionnaire.db.get_courses()
            resultats = analyse_ecart_position_generique(courses, numero, 2)
            gestionnaire.visualiser_resultats(resultats, "Troisième")
        elif choix == "4":
            if resultats:
                courses = gestionnaire.db.get_courses()
                gestionnaire.exporter_resultats(resultats)  # Passage des résultats
            else:
                print("⚠️ Veuillez d'abord effectuer une analyse (option 1 ou 2)")
        elif choix == "5":
            break
        else:
            print("Choix invalide, veuillez réessayer.")



def main():
    # Chemin du dossier contenant les fichiers texte
    dossier_notes = "c:/Users/Cedric/Desktop/geny/notes"

    # Créer une instance de Database
    db = Database('courses.db')

    # Initialisation du gestionnaire de courses avec l'instance de Database
    gestionnaire = GestionnaireCourses(dossier_notes, db)

    # Traiter les fichiers
    print("Début du traitement des fichiers...")
    gestionnaire.traiter_fichiers()
    print("Traitement des fichiers terminé.")

    # Utiliser la même instance de Database pour entrainer_modele_tranche_1_5
    model, label_encoders, label_encoder_numero = entrainer_modele_tranche_1_5(db)

    running = True
    while running:
        try:
            afficher_menu_principal()
            choix = input("Choix : ").strip()

            if choix == "1":
                try:
                    print("Début du traitement des fichiers...")
                    gestionnaire.traiter_fichiers()
                    print("Traitement des fichiers terminé avec succès.")
                except Exception as e:
                    print(f"Erreur lors du traitement des fichiers : {e}")
            elif choix == "2":
                pos1 = int(input("Position 1 (synthèse) : "))
                pos2 = int(input("Position 2 (synthèse) : "))
                resultats = gestionnaire.analyser_positions(pos1, pos2)
                print(resultats)
            elif choix == "3":
                num1 = int(input("Numéro 1 (arrivée) : "))
                num2 = int(input("Numéro 2 (arrivée) : "))
                resultats = gestionnaire.analyser_positions_arrivee(num1, num2)
                print(resultats)
            elif choix == "4":
                stats = gestionnaire.obtenir_statistiques_globales()
                print(stats)
            elif choix == "5":
                afficher_sous_menu_analyse_synthese(gestionnaire)
            elif choix == "6":
                afficher_sous_menu_analyse_arrivee(gestionnaire)
            elif choix == "7":
                try:
                    # Récupérer les données formatées
                    X, y = gestionnaire.preparer_donnees_prediction()
                    
                    # Vérifier la cohérence des données
                    if len(X) < 10 or len(y) < 10:
                        print("Données insuffisantes (minimum 10 courses)")
                        return
                        
                    # Exécuter la prédiction avec gestion des erreurs
                    gestionnaire.executer_prediction()
                    
                except Exception as e:
                    print(f"Échec du pipeline de prédiction : {str(e)}")
            elif choix == "8":
                # Afficher les disciplines disponibles
                disciplines = gestionnaire.obtenir_disciplines_disponibles()
                print("\n=== Disciplines disponibles ===")
                for i, discipline in enumerate(disciplines, start=1):
                    print(f"{i}. {discipline}")
                choix_discipline = int(input("Choisissez une discipline (numéro) : ")) - 1
                discipline = disciplines[choix_discipline]

                # Afficher les distances disponibles pour la discipline choisie
                distances = gestionnaire.obtenir_distances_disponibles_par_discipline(discipline)
                print(f"\n=== Distances disponibles pour '{discipline}' ===")
                for i, distance in enumerate(distances, start=1):
                    print(f"{i}. {distance}")
                choix_distance = int(input("Choisissez une distance (numéro) : ")) - 1
                distance = distances[choix_distance]

                # Afficher les lieux disponibles pour la discipline et la distance choisies
                lieux = db.obtenir_lieux_disponibles_par_discipline_et_distance(discipline, distance)
                print(f"\n=== Lieux disponibles pour '{discipline}' et '{distance}' ===")
                for i, lieu in enumerate(lieux, start=1):
                    print(f"{i}. {lieu}")
                choix_lieu = int(input("Choisissez un lieu (numéro) : ")) - 1
                lieu = lieux[choix_lieu]

                # Vérifier si la combinaison existe
                if not db.combinaison_existe(discipline, distance, lieu):
                    print(f"\nErreur : Aucune course de type '{discipline}' sur '{distance}' à '{lieu}' n'existe dans la base de données.")
                    continue  # Revenir au menu principal

                # Créer la nouvelle course
                nouvelle_course = {
                    'discipline': discipline,
                    'distance': distance,
                    'lieu': lieu
                }

                # Prédire les numéros dans la tranche 1-5 avec leurs probabilités
                predictions = predire_tranche_1_5(model, label_encoders, label_encoder_numero, nouvelle_course, top_n=3)
                print("\n=== Numéros prédits dans la tranche 1-5 ===")
                for num, proba in predictions:
                    print(f"Numéro {num} : {proba * 100:.1f}% de probabilité")

            elif choix == "9":
                numero = int(input("Quel numéro voulez-vous analyser ? "))
                concordance = gestionnaire.analyser_concordance_numero(numero)
                
                print(f"\n=== Concordance pour le numéro {numero} ===")
                for couple in sorted(concordance.keys()):
                    data = concordance[couple]
                    print(f"\nCouple {couple[0]}‑{couple[1]} :")
                    print(f"Participations conjointes : {data['total_participations']}")
                    print(f"Réussites communes        : {data['total_successes']}")
                    
                    # Nouveau : Détail des types de courses
                    if data['total_successes'] > 0:
                        print("Détail des réussites par type :")
                        for type_course, count in data['success_details'].items():
                            print(f"  - {type_course}: {count} fois")
                    else:
                        print("Aucune réussite commune")
                    
                    print(f"Écart actuel  : {data['ecart_actuel']} courses")
                    print(f"Écart maximum : {data['ecart_max']} courses")
                    print("-" * 50)
            elif choix == "10":  # Nouvelle option
                gestionnaire.afficher_sous_menu_concordance_deux_numeros()
            elif choix == "11":
                sous_menu_tierce_synthese(gestionnaire)
            elif choix == "12":
                sous_menu_statistiques_avancees(gestionnaire)
            elif choix == "13":
                sous_menu_prediction_avancee(gestionnaire)
            elif choix == "14":
               afficher_sous_menu_paire_impaire(gestionnaire)
            elif choix == "15":
                menu_frequence_ecart_synthese(gestionnaire)
            elif choix == "16":
                
                db = Database('courses.db')
                engine = PredictiveEngine(db)
                predictor = InteractivePredictor(engine)
                predictor.start_interactive_session()
                #analyse_interactive_arrivees('courses.db')  
            elif choix == "17":
                print("Au revoir!")
                break
        
        except KeyboardInterrupt:
            print("\nInterruption clavier. Retour au menu principal.")
            # Ne pas quitter, juste nettoyer l'entrée
            sys.stdin.readlines()  # Vide le buffer d'entrée

        except Exception as e:
            print(f"Erreur : {str(e)}")
            logging.error("Erreur non gérée", exc_info=True)
        
       

if __name__ == "__main__":
    main()
