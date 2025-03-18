# analyse_interactive.py
import itertools
from itertools import permutations
from typing import Callable, List, Dict, Any, Optional, Tuple
import sqlite3
from datetime import datetime
import json
import matplotlib.pyplot as plt


# Fonctions utilitaires pour les saisies validées
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
    # Si aucune de ces séparations ne fonctionne, tenter de convertir directement
    try:
        return [int(group_input)]
    except Exception:
        return []

# Fonctions de collecte des paramètres
def get_initial_partants() -> List[int]:
    n = ask_integer("Combien de partants initiaux pour cette course ? ", 
                   lambda x: x > 0, 
                   "Veuillez entrer un nombre positif.")
    return list(range(1, n + 1))

def get_elimination_numbers(partants: List[int]) -> List[int]:
    max_elimination = len(partants) - 1
    nombre_a_eliminer = ask_integer(
        f"Combien de partants souhaitez-vous éliminer ? (0 à {max_elimination}) ",
        lambda x: 0 <= x < len(partants),
        f"Veuillez entrer un nombre entre 0 et {max_elimination}."
    )
    eliminated: List[int] = []
    if nombre_a_eliminer > 0:
        print("Veuillez spécifier les numéros à éliminer parmi :", partants)
        while len(eliminated) < nombre_a_eliminer:
            num = ask_integer(
                f"Numéro à éliminer {len(eliminated) + 1} : ",
                lambda x: x in partants and x not in eliminated,
                f"Le numéro doit être dans {partants} et non déjà éliminé."
            )
            eliminated.append(num)
    return eliminated

def get_top_n(partants_disponibles: List[int]) -> int:
    return ask_integer(
        f"Combien de premiers numéros souhaitez-vous considérer (Top N) ? ",
        lambda x: 1 <= x <= len(partants_disponibles),
        f"Veuillez entrer un nombre entre 1 et {len(partants_disponibles)}."
    )

def get_parity_condition() -> Optional[bool]:
    choix = ask_choice("Le numéro gagnant doit-il être pair, impair ou sans condition ? (pair/impair/aucun) ", 
                      ['pair', 'impair', 'aucun'])
    if choix == 'pair':
        return False
    elif choix == 'impair':
        return True
    return None

def get_forced_number(partants_disponibles: List[int], top_n: int) -> Optional[int]:
    choix = ask_choice(f"Souhaitez-vous forcer un numéro spécifique à être dans le Top {top_n} ? (oui/non) ", 
                      ['oui', 'non'])
    if choix == 'oui':
        return ask_integer(
            f"Quel numéro souhaitez-vous forcer à être dans le Top {top_n} ? ",
            lambda x: x in partants_disponibles,
            f"Le numéro doit être dans la liste des partants disponibles : {partants_disponibles}"
        )
    else:
        print(f"Aucun numéro ne sera forcé dans le Top {top_n}.")
        return None

def get_group_condition(partants_initiaux: List[int], top_n: int) -> Optional[Dict[str, Any]]:
    choix = ask_choice(f"Souhaitez-vous définir une condition sur des groupes de numéros dans le Top {top_n} ? (oui/non) ", 
                      ['oui', 'non'])
    if choix == 'oui':
        while True:
            group_input = input("Veuillez entrer le groupe de numéros concerné (ex: 1-5 ou 6,7,8) : ")
            nombres_groupe = parse_group_input(group_input)
            nombres_groupe_valides = [num for num in nombres_groupe if num in partants_initiaux]
            if not nombres_groupe_valides:
                print(f"Aucun des numéros entrés n'est parmi les partants initiaux {partants_initiaux}. Veuillez réessayer.")
                continue
            type_condition = ask_choice("Type de condition (exactement/minimum/maximum) ? ", 
                                      ['exactement', 'minimum', 'maximum'])
            valeur_condition = ask_integer(
                f"Nombre de numéros de ce groupe dans le Top {top_n} (pour '{type_condition}') ? ",
                lambda x: x >= 0,
                "Veuillez entrer un nombre positif ou nul."
            )
            print(f"Condition de groupe dans le Top {top_n} définie avec succès.")
            return {
                'nombres_groupe': nombres_groupe_valides,
                'type_condition': type_condition,
                'valeur_condition': valeur_condition,
                'top_n': top_n
            }
    else:
        print(f"Aucune condition de groupe de numéros dans le Top {top_n} ne sera appliquée.")
    return None

# Fonction de calcul des combinaisons en filtrant selon les conditions
def compute_valid_combinations(
    partants_disponibles: List[int],
    top_n: int,
    parity_condition: Optional[bool],
    forced_number: Optional[int],
    group_condition: Optional[Dict[str, Any]]
) -> List[Tuple[int, ...]]:
    valid_combinations: List[Tuple[int, ...]] = []
    for combinaison in permutations(partants_disponibles, top_n):
        # Condition 1 : Parité du gagnant (premier de la combinaison)
        if parity_condition is not None:
            if parity_condition and combinaison[0] % 2 == 0:
                continue
            elif not parity_condition and combinaison[0] % 2 != 0:
                continue
        # Condition 2 : Numéro forcé dans le Top N
        if forced_number is not None and forced_number not in combinaison:
            continue
        # Condition 3 : Condition de groupe dans le Top N
        if group_condition is not None:
            count_in_group = sum(1 for num in combinaison if num in group_condition['nombres_groupe'])
            cond_type = group_condition['type_condition']
            cond_value = group_condition['valeur_condition']
            if cond_type == 'exactement' and count_in_group != cond_value:
                continue
            elif cond_type == 'minimum' and count_in_group < cond_value:
                continue
            elif cond_type == 'maximum' and count_in_group > cond_value:
                continue
        valid_combinations.append(combinaison)
    return valid_combinations

# Fonctions d'analyse statistique adaptées à SQLite
def analyser_statistiques_courses(db_path: str) -> Dict[str, Any]:
    """Analyse les données historiques pour en extraire des statistiques utiles."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            # Récupérer toutes les courses
            cur.execute("""
                SELECT date_course, arrivee, partants
                FROM courses
                ORDER BY date(date_course) ASC
            """)
            courses = [dict(row) for row in cur.fetchall()]
            
            if not courses:
                return {"message": "Aucune donnée disponible pour l'analyse."}
            
            stats = {}
            
            # Convertir les données de string à liste
            for course in courses:
                if isinstance(course['arrivee'], str):
                    course['arrivee'] = [int(x) for x in course['arrivee'].split(',') if x.strip().isdigit()]
                if isinstance(course['partants'], str):
                    course['partants'] = [int(x) for x in course['partants'].split(',') if x.strip().isdigit()]
            
            # Fréquence d'apparition des numéros gagnants
            winners = [course["arrivee"][0] for course in courses if course.get("arrivee")]
            stats["frequence_gagnants"] = {}
            for winner in winners:
                if winner not in stats["frequence_gagnants"]:
                    stats["frequence_gagnants"][winner] = 0
                stats["frequence_gagnants"][winner] += 1
            
            # Calculer les écarts pour chaque numéro
            all_partants = []
            for course in courses:
                all_partants.extend(course.get("partants", []))
            max_numero = max(all_partants) if all_partants else 1
            
            ecarts = {i: [] for i in range(1, max_numero + 1)}
            derniere_apparition = {i: None for i in range(1, max_numero + 1)}
            
            for idx, course in enumerate(courses):
                arrivee = course.get("arrivee", [])
                for num in range(1, max_numero + 1):
                    if num in arrivee:
                        if derniere_apparition[num] is not None:
                            ecarts[num].append(idx - derniere_apparition[num])
                        derniere_apparition[num] = idx
            
            stats["ecarts_moyens"] = {}
            for num, ecarts_list in ecarts.items():
                if ecarts_list:
                    stats["ecarts_moyens"][num] = sum(ecarts_list) / len(ecarts_list)
                else:
                    stats["ecarts_moyens"][num] = 0
            
            # Analyse des numéros pairs/impairs
            pairs_impairs = {"pair": 0, "impair": 0}
            for gagnant in winners:
                if gagnant % 2 == 0:
                    pairs_impairs["pair"] += 1
                else:
                    pairs_impairs["impair"] += 1
            
            total = pairs_impairs["pair"] + pairs_impairs["impair"]
            if total > 0:
                stats["ratio_pairs_impairs"] = {
                    "pair": pairs_impairs["pair"] / total,
                    "impair": pairs_impairs["impair"] / total
                }
            
            return stats
    except sqlite3.Error as e:
        print(f"Erreur SQLite : {str(e)}")
        return {"error": f"Erreur d'analyse: {str(e)}"}

def calculer_score_combinaison(combinaison: Tuple[int, ...], statistiques: Dict[str, Any]) -> float:
    """Calcule un score de probabilité pour une combinaison donnée."""
    score = 0.0
    
    # Points pour le gagnant basés sur sa fréquence historique
    gagnant = combinaison[0]
    freq_gagnants = statistiques.get("frequence_gagnants", {})
    score += freq_gagnants.get(gagnant, 0) * 2  # Le gagnant a plus d'importance
    
    # Points basés sur les écarts moyens
    ecarts_moyens = statistiques.get("ecarts_moyens", {})
    for num in combinaison:
        # Un petit écart moyen est favorable
        ecart = ecarts_moyens.get(num, 0)
        if ecart > 0:
            score += 10 / ecart  # Inverse de l'écart
    
    # Points pour la tendance pair/impair
    ratio_pairs_impairs = statistiques.get("ratio_pairs_impairs", {"pair": 0.5, "impair": 0.5})
    if gagnant % 2 == 0:  # Pair
        score += ratio_pairs_impairs.get("pair", 0.5) * 5
    else:  # Impair
        score += ratio_pairs_impairs.get("impair", 0.5) * 5
    
    # Bonus pour les combinaisons avec une bonne répartition
    pairs = sum(1 for num in combinaison if num % 2 == 0)
    impairs = len(combinaison) - pairs
    # Favoriser un équilibre ou suivre la tendance historique
    equilibre = min(pairs, impairs) / max(pairs, impairs) if max(pairs, impairs) > 0 else 0
    score += equilibre * 3
    
    return score

# Fonction principale d'analyse interactive
def analyse_interactive_arrivees(db_path: str):
    """Version optimisée avec gestion des contraintes complexes"""
    
    # Phase 1 - Configuration de la course
    print("\n=== Configuration de la course ===")
    partants = get_initial_partants()
    elimines = get_elimination_numbers(partants)
    disponibles = [p for p in partants if p not in elimines]
    
    if not disponibles:
        print("Aucun partant disponible après élimination!")
        return

    # Phase 2 - Définition des contraintes
    top_n = get_top_n(disponibles)
    parite = get_parity_condition()
    force = get_forced_number(disponibles, top_n)
    groupe = get_group_condition(partants, top_n)
    
    # Vérification cohérence des contraintes
    if force and force in elimines:
        print("Erreur: Le numéro forcé ne peut pas être éliminé!")
        return

    # Phase 3 - Génération des combinaisons
    print("\n=== Génération des combinaisons ===")
    max_combinations = 10_000  # Sécurité anti-bouclage
    combinations = generate_combinations(
        disponibles,
        top_n,
        max_combinations,
        parite,
        force,
        groupe
    )
    
    if not combinations:
        print("Aucune combinaison valide trouvée!")
        return

    # Phase 4 - Analyse prédictive
    stats = analyser_statistiques_courses(db_path)
    scored_combinations = sorted(
        [(c, calculer_score_combinaison(c, stats)) for c in combinations],
        key=lambda x: x[1],
        reverse=True
    )

    # Phase 5 - Affichage des résultats
    print("\n=== Top 10 des combinaisons probables ===")
    for idx, (combinaison, score) in enumerate(scored_combinations[:10], 1):
        print(f"{idx}. {combinaison} - Score: {score:.2f}")

def generate_combinations(
    disponibles: List[int],
    top_n: int,
    max_comb: int = 1000,  # Valeur par défaut ajoutée
    *conditions: Callable[[Tuple[int, ...]], bool]
) -> List[Tuple[int, ...]]:
    """Génère des combinaisons valides avec sécurité intégrée"""
    
    # Validation des conditions en premier
    print("\n=== Vérification des conditions ===")
    print(f"Nombre de conditions: {len(conditions)}")
    for i, cond in enumerate(conditions, 1):
        if not callable(cond):
            raise TypeError(f"Condition {i} n'est pas une fonction (type: {type(cond)})")
    
    # Validation des paramètres
    if top_n <= 0 or top_n > len(disponibles):
        raise ValueError(f"top_n invalide: {top_n} (disponibles: {len(disponibles)})")
    
    if max_comb < 1:
        raise ValueError(f"max_comb doit être ≥ 1 (reçu: {max_comb})")

    # Génération des combinaisons
    valides = []
    for comb in itertools.permutations(disponibles, top_n):
        if all(cond(comb) for cond in conditions):
            valides.append(comb)
            if len(valides) >= max_comb:
                break
                
    return valides

def exemple_utilisation():
    partants = list(range(1, 16))  # 15 partants
    top_n = 3
    max_comb = 1000  # Définition explicite
    
    # Définition des conditions
    conditions = (
        lambda c: c[0] % 2 == 0,  # Premier numéro pair
        lambda c: 5 in c           # Doit contenir le numéro 5
    )
    
    # Appel sécurisé
    try:
        resultats = generate_combinations(
            disponibles=partants,
            top_n=top_n,
            max_comb=max_comb,
            *conditions
        )
        print(f"\nCombinaisons générées: {len(resultats)}")
        print("Exemples:", resultats[:5])
        
    except Exception as e:
        print(f"\nErreur: {str(e)}")

exemple_utilisation()

# Exemples de conditions d'utilisation
def check_parity(combinaison: Tuple[int, ...], parity: str) -> bool:
    """Vérifie la parité du premier élément"""
    if parity == 'pair':
        return combinaison[0] % 2 == 0
    elif parity == 'impair':
        return combinaison[0] % 2 == 1
    return False

def check_forced_number(combinaison: Tuple[int, ...], nombre: int) -> bool:
    """Vérifie la présence d'un numéro obligatoire"""
    return nombre in combinaison

    analyser_possibilites()
# Utilisation avec pipeline complet
def analyser_possibilites():
    # Paramètres de configuration
    partants = list(range(1, 16))  # 15 partants
    top_n = 3  # Tiercé
    max_comb = 1000  # Définition du paramètre manquant
    
    # Création des conditions de validation
    conditions = [
        lambda c: check_parity(c, 'pair'),  # Première condition
        lambda c: check_forced_number(c, 5)  # Deuxième condition
    ]
    
    # Vérification préalable des conditions
    print("Vérification des conditions:")
    for i, condition in enumerate(conditions, 1):
        print(f"Condition {i}: {'Valide' if callable(condition) else 'Invalide'}")
    
    # Appel sécurisé avec unpacking
    try:
        combinaisons = generate_combinations(
            disponibles=partants,
            top_n=top_n,
            max_comb=max_comb,  # Utilisation du paramètre défini
            *conditions
        )
        
        print(f"\nRésultats pour {len(partants)} partants (max {max_comb} combinaisons):")
        print(f"Combinaisons valides trouvées : {len(combinaisons)}")
        print("Exemples :", combinaisons[:5])
        
    except Exception as e:
        print(f"\nErreur lors de la génération : {str(e)}")


def afficher_histogramme_scores(scores: List[float]):
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=20, alpha=0.7, color='blue')
    plt.title('Distribution des scores des combinaisons')
    plt.xlabel('Score de probabilité')
    plt.ylabel('Nombre de combinaisons')
    plt.show()

def sauvegarder_prediction(combinaison: Tuple[int,...], score: float):
    with open('predictions.txt', 'a') as f:
        f.write(f"{datetime.now().isoformat()} | {combinaison} | {score:.2f}\n")

def analyser_risque(combinaison: Tuple[int,...], stats: Dict) -> float:
    """Calcule un indice de risque basé sur l'historique"""
    risques = []
    for num in combinaison:
        freq = stats['frequence_gagnants'].get(num, 0)
        ecart = stats['ecarts_moyens'].get(num, 0)
        risques.append(1/(freq + 0.1) * (ecart + 1))
    return sum(risques) / len(risques)