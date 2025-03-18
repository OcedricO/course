# prediction_interactive.py
import os
import sqlite3
import logging
from typing import List, Tuple, Dict, Optional, Callable, Any
from itertools import combinations, permutations
from analyse import calculer_ecarts_numeros_arrivee_avec_participation
from database import Database
from collections import defaultdict
from math import comb
import pandas as pd
from pathlib import Path
import os
import sqlite3
import logging
from typing import List, Tuple, Dict, Optional, Callable, Any
from itertools import combinations, permutations
from collections import defaultdict
from math import comb

# ---------------------- Fonctions utilitaires d'interaction ---------------------- #

def ask_integer(prompt: str, condition: Callable[[int], bool], error_message: str = "Entrée invalide. Merci de réessayer.") -> int:
    """Demande à l'utilisateur de saisir un entier en respectant une condition donnée."""
    while True:
        try:
            value = int(input(prompt))
            if condition(value):
                return value
            else:
                print(error_message)
        except ValueError:
            print("Veuillez entrer un nombre entier valide.")

def ask_choice(prompt: str, choices: List[str]) -> str:
    """Demande à l'utilisateur de choisir parmi une liste de réponses possibles."""
    choices_lower = [choice.lower() for choice in choices]
    while True:
        answer = input(prompt).strip().lower()
        if answer in choices_lower:
            return answer
        else:
            print("Choix invalide, veuillez répondre par :", "/".join(choices))

def parse_group_input(group_input: str) -> List[int]:
    """Convertit une chaîne de caractères en liste d'entiers (ex: '1-5' ou '6,7,8')."""
    if '-' in group_input:
        try:
            start, end = map(int, group_input.split('-'))
            return list(range(start, end + 1))
        except Exception:
            pass
    elif ',' in group_input:
        try:
            return [int(x.strip()) for x in group_input.split(',')]
        except Exception:
            pass
    try:
        return [int(group_input)]
    except Exception:
        return []

# ---------------------- Classes principales ---------------------- #

# Supposons que la classe Database existe déjà dans votre projet.
class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_courses(self):
        # Implémentez ici la récupération des courses depuis votre base.
        return []

class PredictiveEngine:
    def __init__(self, db: Database):
        self.db = db
        self.current_constraints: Dict[str, Any] = {}
        self.historical_data = self.load_historical_patterns()
        
    def load_historical_patterns(self) -> Dict[str, Any]:
        """Charge les modèles historiques depuis la base."""
        conn = sqlite3.connect(self.db.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        patterns = {
            'frequence_arrivee': {},
            'ecarts_numeros': {},
            'couples_gagnants': defaultdict(int)
        }
        
        cur.execute("SELECT arrivee FROM courses")
        for row in cur.fetchall():
            if row['arrivee']:  # Vérifier que arrivee n'est pas None
                arrivee = list(map(int, row['arrivee'].split('-')))
                for num in arrivee:
                    patterns['frequence_arrivee'][num] = patterns['frequence_arrivee'].get(num, 0) + 1
                # Enregistrer les couples gagnants
                for couple in combinations(arrivee, 2):
                    patterns['couples_gagnants'][tuple(sorted(couple))] += 1
        
        # Exemple d'utilisation d'une fonction d'analyse (adaptable)
        # ecarts_data = calculer_ecarts_numeros_arrivee_avec_participation(self.db.get_courses())
        # Ici, on utilise des écarts fictifs pour l'exemple
        ecarts_data = {i: {'ecart_actuel': 3} for i in range(1, 21)}
        for num, data in ecarts_data.items():
            patterns['ecarts_numeros'][num] = data['ecart_actuel']
        
        return patterns

    def apply_dynamic_filters(self, partants: List[int]) -> List[int]:
        """Applique les filtres dynamiques basés sur les contraintes utilisateur."""
        if 'eliminated' in self.current_constraints:
            partants = [p for p in partants if p not in self.current_constraints['eliminated']]
        if self.current_constraints.get('filter_ecarts', False):
            partants = [p for p in partants if self.historical_data['ecarts_numeros'].get(p, 0) < 5]
        if 'forced_numbers' in self.current_constraints:
            # Ajout des numéros forcés (pour garantir leur présence)
            partants += self.current_constraints['forced_numbers']
        return sorted(list(set(partants)))
    
    def group_combinations(self, combinations_list: List[Tuple[int, ...]], top_n: int) -> List[Tuple[str, int]]:
        """
        Regroupe les combinaisons en motifs avec wildcards selon une tarification adaptative.
        Vous pouvez adapter le dictionnaire TARIFS selon vos besoins.
        """
        TARIFS = {
            1: {0: 2},
            2: {0: 2, 1: 3},
            3: {0: 2, 1: 6, 2: 12},
            4: {0: 2, 1: 4, 2: 8, 3: 16},
            5: {0: 2, 1: 5, 2: 10, 3: 20},
            6: {0: 2, 1: 6, 2: 12, 3: 24},
            7: {0: 2, 1: 7, 2: 14, 3: 28},
            8: {0: 2, 1: 8, 2: 16, 3: 32},
            9: {0: 2, 1: 9, 2: 18, 3: 36}
        }
        MAX_WILDCARDS = 3
        results = []
        patterns = defaultdict(set)
        for combo in combinations_list:
            possible_wildcards = min(MAX_WILDCARDS, top_n)
            for wildcards in range(0, possible_wildcards + 1):
                fixed = top_n - wildcards
                if fixed < 0:
                    continue
                for fixed_positions in combinations(range(top_n), fixed):
                    pattern = []
                    variables = []
                    for i in range(top_n):
                        if i in fixed_positions:
                            pattern.append(str(combo[i]))
                        else:
                            pattern.append('x')
                            variables.append(combo[i])
                    key = (tuple(pattern), tuple(sorted(variables)))
                    patterns[key].add(tuple(sorted(combo)))
        for (pattern, variables), combos in patterns.items():
            wildcards = pattern.count('x')
            try:
                cout = len(combos) * TARIFS[top_n][wildcards]
            except KeyError:
                continue
            display = (
                f"{'-'.join(pattern).replace('-x', '', wildcards)} "
                f"({wildcards} wildcards)/[{' '.join(map(str, variables))}]"
            )
            results.append((display, cout))
        return sorted(results, key=lambda x: (x[0].count('x'), x[1]))

    def _calculate_combination_score(self, combo: Tuple[int, ...]) -> float:
        """Calcule un score pour une combinaison à partir des données historiques."""
        score = 0.0
        for num in combo:
            score += self.historical_data['frequence_arrivee'].get(num, 0) * 0.5
        for pair in combinations(combo, 2):
            score += self.historical_data['couples_gagnants'].get(tuple(sorted(pair)), 0) * 0.3
        for num in combo:
            score -= self.historical_data['ecarts_numeros'].get(num, 0) * 0.2
        return score

    def _meets_group_conditions(self, combo: Tuple[int, ...], conditions: List[Dict[str, Any]]) -> bool:
        """Vérifie si une combinaison respecte toutes les conditions de groupe."""
        if not conditions:
            return True
        for condition in conditions:
            groupe = condition.get('groupe', [])
            type_cond = condition.get('type', '')
            valeur = condition.get('valeur', 0)
            count = sum(1 for num in combo if num in groupe)
            if type_cond == 'exactement' and count != valeur:
                return False
            elif type_cond == 'minimum' and count < valeur:
                return False
            elif type_cond == 'maximum' and count > valeur:
                return False
        return True

class InteractivePredictor:
    def __init__(self, engine: PredictiveEngine):
        self.engine = engine
        self.current_session = {}

    def get_initial_partants(self) -> List[int]:
        n = ask_integer("Combien de partants initiaux pour cette course ? ", lambda x: x > 0, "Veuillez entrer un nombre positif.")
        return list(range(1, n + 1))

    def get_parity_condition(self) -> Optional[bool]:
        choix = ask_choice("Le numéro gagnant doit-il être pair, impair ou sans condition ? (pair/impair/aucun) ", ['pair', 'impair', 'aucun'])
        if choix == 'pair':
            return False  # False pour pair
        elif choix == 'impair':
            return True   # True pour impair
        return None

    def get_group_condition(self, partants_initiaux: List[int], top_n: int) -> Optional[Dict[str, Any]]:
        choix = ask_choice(f"Souhaitez-vous définir une condition sur des groupes de numéros dans le Top {top_n} ? (oui/non) ", ['oui', 'non'])
        if choix == 'oui':
            while True:
                group_input = input("Veuillez entrer le groupe de numéros concerné (ex: 1-5 ou 6,7,8) : ")
                nombres_groupe = parse_group_input(group_input)
                nombres_groupe_valides = [num for num in nombres_groupe if num in partants_initiaux]
                if not nombres_groupe_valides:
                    print(f"Aucun des numéros entrés n'est parmi les partants initiaux {partants_initiaux}. Veuillez réessayer.")
                    continue
                type_condition = ask_choice("Type de condition (exactement/minimum/maximum) ? ", ['exactement', 'minimum', 'maximum'])
                valeur_condition = ask_integer(f"Nombre de numéros du groupe dans le Top {top_n} (pour '{type_condition}') ? ", 
                                               lambda x: x >= 0, "Veuillez entrer un nombre positif ou nul.")
                print(f"Condition de groupe dans le Top {top_n} définie avec succès.")
                return {
                    'groupe': nombres_groupe_valides,
                    'type': type_condition,
                    'valeur': valeur_condition,
                    'top_n': top_n
                }
        else:
            print(f"Aucune condition de groupe de numéros dans le Top {top_n} ne sera appliquée.")
        return None

    def generate_combinations(self, partants: List[int], top_n: int, with_order: bool, forced_numbers: List[int],
                              group_conditions: List[Dict[str, Any]], parity_condition: Optional[bool]) -> List[Tuple[int, ...]]:
        """
        Génère toutes les combinaisons ou permutations possibles en appliquant successivement :
         1. Le filtre pour que chaque combinaison contienne les numéros forcés.
         2. Le filtre par conditions de groupe.
         3. Le filtre sur la parité (du numéro gagnant, ici le premier élément).
        """
        generator = permutations if with_order else combinations
        all_possible = list(generator(partants, top_n))
        
        # Filtrage 1 : Conserver uniquement les combinaisons contenant tous les numéros forcés.
        if forced_numbers:
            filtered = [combo for combo in all_possible if all(num in combo for num in forced_numbers)]
        else:
            filtered = all_possible

        # Filtrage 2 : Appliquer les conditions de groupe.
        filtered = [combo for combo in filtered if self.engine._meets_group_conditions(combo, group_conditions)]
        
        # Filtrage 3 : Appliquer la condition de parité sur le "numéro gagnant".
        # Ici, nous considérons le premier élément de la combinaison (ou le plus petit si non ordonné).
        if parity_condition is not None:
            if parity_condition:  # Si condition impair
                filtered = [combo for combo in filtered if combo[0] % 2 == 1]
            else:  # Condition pair
                filtered = [combo for combo in filtered if combo[0] % 2 == 0]
                
        return filtered

    def group_combinations(self, combinations_list: List[Tuple[int, ...]], top_n: int) -> List[Tuple[str, int]]:
        return self.engine.group_combinations(combinations_list, top_n)

    def save_combinations_to_file(self, grouped_combinations: List[Tuple[str, int]], filename: str):
        print(f"Enregistrement des combinaisons dans {filename}...")
        try:
            with open(filename, 'w') as file:
                total_cost = 0
                for combo, cost in grouped_combinations:
                    file.write(f"{combo} - Coût: {cost} euros\n")
                    total_cost += cost
                file.write(f"\nCoût total minimum : {total_cost} euros\n")
            print("Combinaisons enregistrées avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'enregistrement des combinaisons: {e}")

    def save_combinations_to_excel(self, grouped_combinations: List[Tuple[str, int]], filename: str):
        """Enregistre les combinaisons dans un fichier Excel avec formatage avancé"""
        try:
            # Création d'un DataFrame structuré
            data = []
            for combo, cost in grouped_combinations:
                # Extraction des composants
                parts = combo.split('/')
                pattern = parts[0].strip()
                variables = parts[1].replace('[', '').replace(']', '').strip() if len(parts) > 1 else ''
                
                data.append({
                    'Modèle': pattern,
                    'Variables': variables,
                    'Coût (€)': cost,
                    'Nombre de Wildcards': pattern.count('x'),
                    'Combinaisons Possibles': combo.count('x') + 1
                })

            df = pd.DataFrame(data)
            
            # Ordonner les colonnes
            df = df[['Modèle', 'Variables', 'Nombre de Wildcards', 'Combinaisons Possibles', 'Coût (€)']]
            
            # Création du writer Excel
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Prédictions')
            
            # Accès au workbook et worksheet pour le formatage
            workbook = writer.book
            worksheet = writer.sheets['Prédictions']
            
            # Formatage automatique des colonnes
            header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#4F81BD',  # Couleur de fond
            'border': 1,
            'font_color': 'white'  # Couleur du texte
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                max_len = max(df[value].astype(str).apply(len).max(), len(value)) + 2
                worksheet.set_column(col_num, col_num, max_len)
            
            # Sauvegarde finale
            writer.close()
            print(f"Fichier Excel enregistré : {filename}")
            
        except Exception as e:
            print(f"Erreur lors de l'export Excel : {str(e)}")
            logging.error("Erreur Excel", exc_info=True)

    def _ask_order_preference(self) -> bool:
        choix = ask_choice("Souhaitez-vous des résultats avec ordre (permutations) ou sans ordre (combinaisons) ? (ordre/desordre) ", ['ordre', 'desordre'])
        return choix == 'ordre'

    def _apply_interactive_filters(self, partants: List[int]) -> List[int]:
        filtered = partants.copy()
        while True:
            print(f"\nPartants actuels: {filtered}")
            print("1. Éliminer des numéros")
            print("2. Forcer des numéros")
            print("3. Activer filtre d'écart")
            print("4. Valider la configuration")
            choix = input("Choix: ").strip()
            if choix == '1':
                to_eliminate = self._select_numbers(filtered, "éliminer")
                self.engine.current_constraints['eliminated'] = to_eliminate
                filtered = [p for p in filtered if p not in to_eliminate]
            elif choix == '2':
                to_force = self._select_numbers(partants, "forcer")
                self.engine.current_constraints['forced_numbers'] = to_force
                for num in to_force:
                    if num not in filtered:
                        filtered.append(num)
                filtered.sort()
            elif choix == '3':
                self.engine.current_constraints['filter_ecarts'] = True
                print("Filtre des écarts actifs!")
            elif choix == '4':
                return filtered
            else:
                print("Choix invalide")

    def _select_numbers(self, available: List[int], action: str) -> List[int]:
        selected = []
        while True:
            print(f"\nNuméros disponibles: {available}")
            print(f"Numéros sélectionnés pour {action}: {selected}")
            choix = input("Entrez un numéro (ou 'fin' pour terminer) : ").strip().lower()
            if choix == 'fin':
                return selected
            try:
                num = int(choix)
                if num in available and num not in selected:
                    selected.append(num)
                else:
                    print("Numéro invalide ou déjà sélectionné")
            except ValueError:
                print("Entrée invalide")

    def _display_predictions(self, predictions: List[Tuple[Tuple[int, ...], float]], with_order: bool, group_conditions: List[Dict[str, Any]]):
        print(f"\n=== Résultats ({'avec ordre' if with_order else 'sans ordre'}) ===")
        if group_conditions:
            print("\nConditions de groupe actives :")
            for idx, cond in enumerate(group_conditions, 1):
                print(f"{idx}. {cond['type']} {cond['valeur']} dans {cond['groupe']}")
        print("\nTop 10 des combinaisons :")
        for idx, (combo, score) in enumerate(predictions[:10], 1):
            proba = self._convert_score_to_proba(score, predictions)
            print(f"{idx}. {combo} - Score: {score:.2f} - Probabilité: {proba:.1f}%")
        print(f"\nNombre total de combinaisons valides : {len(predictions)}")

    def _convert_score_to_proba(self, score: float, all_predictions: List[Tuple[Tuple[int, ...], float]]) -> float:
        max_score = max(s for _, s in all_predictions) if all_predictions else 1
        total_score = sum(s for _, s in all_predictions) if all_predictions else 1
        return (score / total_score) * 100 if total_score > 0 else 0

    def start_interactive_session(self):
        try:
            n_partants = ask_integer("\nNombre total de partants ? ", lambda x: x > 0, "Veuillez entrer un nombre positif.")
            partants = list(range(1, n_partants + 1))
            top_n = ask_integer("Prédire combien de numéros (1-9) ? ", lambda x: 1 <= x <= 9, "Erreur : choisir entre 1 et 9")
            
            filtered_partants = self._apply_interactive_filters(partants)
            parity_condition = self.get_parity_condition()
            with_order = self._ask_order_preference()
            
            # Remplacer cette partie :
            #group_conditions = []
            #if ask_choice("Voulez-vous ajouter des conditions de groupe ? (oui/non) ", ["oui", "non"]) == "oui":
            #    condition = self.get_group_condition(filtered_partants, top_n)
            #    if condition:
            #        group_conditions.append(condition)

            # Remplacer cette partie :
            group_conditions = self.get_group_conditions(filtered_partants, top_n)

            forced_numbers = self.engine.current_constraints.get('forced_numbers', [])
            valid_combinations = self.generate_combinations(filtered_partants, top_n, with_order, forced_numbers, group_conditions, parity_condition)
            
            if not valid_combinations:
                print("Aucune combinaison ne respecte toutes les contraintes.")
                return
            
            predictions = [(combo, self.engine._calculate_combination_score(combo)) for combo in valid_combinations]
            predictions.sort(key=lambda x: x[1], reverse=True)
            self._display_predictions(predictions, with_order, group_conditions)
            
            grouped = self.group_combinations(valid_combinations, top_n)
            self.save_combinations_to_file(grouped, 'resultats.txt')
            print(f"\nSuccès : {len(grouped)} groupes générés")
            self.save_combinations_to_excel(grouped, 'resultats.xlsx')
            print(f"\nSuccès : {len(grouped)} groupes générés")
        except Exception as e:
            print(f"\nErreur critique dans la session interactive : {str(e)}")
            logging.error(f"Session interactive échouée : {str(e)}")

    def get_group_conditions(self, partants: List[int], top_n: int) -> List[Dict[str, Any]]:
        """Permet d'ajouter MULTIPLES conditions de groupe interactivement."""
        conditions = []
        
        while True:
            choix = ask_choice(
                f"\nAjouter une condition de groupe pour le Top {top_n} ? (oui/non) ", 
                ["oui", "non"]
            )
            
            if choix != "oui":
                break
                
            # Saisie du groupe
            group_input = input("Numéros du groupe (ex: 1-5 ou 6,7,8) : ")
            groupe = parse_group_input(group_input)
            groupe_valide = [num for num in groupe if num in partants]
            
            if not groupe_valide:
                print(f"❌ Aucun numéro valide parmi {partants}")
                continue
                
            # Saisie du type de condition
            type_cond = ask_choice(
                "Type de condition (exactement/minimum/maximum) : ",
                ["exactement", "minimum", "maximum"]
            )
            
            # Saisie de la valeur avec contrôle
            valeur = ask_integer(
                f"Nombre de numéros du groupe dans le Top {top_n} : ",
                lambda x: 0 <= x <= len(groupe_valide),
                "Valeur incohérente avec le groupe"
            )
            
            conditions.append({
                "groupe": groupe_valide,
                "type": type_cond,
                "valeur": valeur
            })
            print(f"✅ Condition {len(conditions)} ajoutée")

        return conditions


