# prediction_avancee.py
import pandas as pd
import numpy as np
import logging
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List

# --- Configuration ---
CONFIG = {
    "coefficients": {
        "historique": 0.3,
        "tendance": 0.25,
        "risques": 0.25,
        "patterns": 0.2,
    },
    "rolling_window": 5,
    "risk_threshold": 0.8
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Modules d'analyse ---

class AnalyseTemporelle:
    """
    Module d'analyse temporelle.
    Convertit la date, trie les données et fournit une tendance de la position.
    """
    def __init__(self, data):
        self.data = data.copy()
        # Conversion de la date et tri
        self.data['date_course'] = pd.to_datetime(self.data['date'], errors='coerce')
        self.data.sort_values(by='date', inplace=True)
    
    def analyser_evolution(self, numero_joueur):
        """
        Analyse l'évolution temporelle pour un joueur donné.
        Retourne un dictionnaire avec la tendance (moyenne des 5 dernières courses).
        """
        data_joueur = self.data[self.data['numero_joueur'] == numero_joueur]
        if data_joueur.empty:
            logger.warning("Aucune donnée pour le joueur %s dans l'analyse temporelle.", numero_joueur)
            return {"tendance_position": 0}
        tendance = data_joueur['position_arrivee'].tail(CONFIG['rolling_window']).mean()
        return {"tendance_position": tendance}


class AnalyseEcarts:
    """
    Module d'analyse des écarts et d'évaluation des risques.
    """
    def __init__(self, data):
        self.data = data.copy()
        
    def analyser_risques(self, numero_joueur):
        """
        Analyse les écarts pour déterminer le niveau de risque.
        Retourne un dictionnaire avec 'niveau_risque' et le ratio moyen.
        """
        data_joueur = self.data[self.data['numero_joueur'] == numero_joueur]
        if data_joueur.empty:
            logger.warning("Aucune donnée pour le joueur %s dans l'analyse des écarts.", numero_joueur)
            return {"niveau_risque": "inconnu", "ratio": 0}
        # Calcul d'un ratio moyen (dummy)
        moyenne_ecart_max = data_joueur['ecart_max'].mean()
        ratio = data_joueur['ecart_actuel'].mean() / moyenne_ecart_max if moyenne_ecart_max != 0 else 0
        niveau = "faible"
        if ratio > 0.8:
            niveau = "élevé"
        elif ratio > 0.5:
            niveau = "moyen"
        return {
        'niveau_risque': niveau,  # ✅ Clé obligatoire
        'ratio': ratio,
        'valeur_absolue': data_joueur['ecart_actuel'].mean() 
    }


class CalculConfiance:
    """
    Module de calcul de l'intervalle de confiance.
    """
    def __init__(self, data):
        self.data = data.copy()
        
    def calculer_intervalles_confiance(self, numero_joueur, prediction_principale):
        """
        Calcule un intervalle de confiance simple basé sur l'écart-type des positions.
        Retourne un dictionnaire avec un intervalle (exemple : intervalle à 90%).
        """
        data_joueur = self.data[self.data['numero_joueur'] == numero_joueur]
        if data_joueur.empty:
            logger.warning("Aucune donnée pour le joueur %s dans le calcul de confiance.", numero_joueur)
            return {"intervalle_90": {"min": prediction_principale - 1, "max": prediction_principale + 1}}
        ecart = data_joueur['position_arrivee'].std()
        return {"intervalle_90": {"min": round(prediction_principale - ecart, 1),
                                   "max": round(prediction_principale + ecart, 1)}}


class AnalyseSequences:
    """
    Module d'analyse des patterns et séquences.
    Fournit une position attendue basée sur l'historique.
    """
    def __init__(self, data):
        self.data = data.copy()
        
    def patterns_position(self):
        """
        Retourne un dictionnaire : clé = numéro de joueur, valeur = position attendue (dummy).
        """
        patterns = {}
        for joueur in self.data['numero_joueur'].unique():
            data_joueur = self.data[self.data['numero_joueur'] == joueur]
            patterns[joueur] = data_joueur['position_arrivee'].mean() if not data_joueur.empty else None
        return patterns

# --- Système de Prédiction Global ---

class SystemePredictionGlobal:
    """
    Système global de prédiction qui intègre toutes les analyses.
    """
    def __init__(self, data, config=CONFIG):
        self.data = data.copy()
        self.config = config
        self.analyses = self._initialiser_analyses()
    
    def _initialiser_analyses(self):
        """
        Initialise tous les modules d'analyse et retourne un dictionnaire.
        """
        return {
            'temporelle': AnalyseTemporelle(self.data),
            'ecarts': AnalyseEcarts(self.data),
            'confiance': CalculConfiance(self.data),
            'patterns': AnalyseSequences(self.data)
        }
    
    def generer_prediction_complete(self, numero_joueur):
        """
        Génère une prédiction complète pour un joueur donné en combinant
        l'analyse temporelle, des écarts, des patterns et les statistiques de base.
        """
        data_joueur = self.data[self.data['numero_joueur'] == numero_joueur]
        # 1. Collecte des données de base
        donnees_base = self._collecter_donnees_base(numero_joueur)
        if donnees_base['historique'].empty:
            logger.error("Aucune donnée pour le joueur %s.", numero_joueur)
            return None
        
        # 2. Analyse temporelle et tendances
        analyse_temps = self.analyses['temporelle'].analyser_evolution(numero_joueur)
        
        # 3. Analyse des écarts et risques
        analyse_risques = self.analyses['ecarts'].analyser_risques(numero_joueur)
        
        # 4. Calcul de la prédiction principale en combinant les analyses
        prediction_principale = self._calculer_prediction_principale(donnees_base, analyse_temps, analyse_risques)
        
        # 5. Calcul des intervalles de confiance
        intervalles = self.analyses['confiance'].calculer_intervalles_confiance(
            numero_joueur, prediction_principale['position_plus_probable']
        )
        
        # 6. Assemblage du rapport final
        return self._assembler_rapport_final(numero_joueur, prediction_principale, intervalles)
    
    def _collecter_donnees_base(self, numero_joueur):
        """
        Collecte et prépare les données de base pour un joueur donné.
        """
        historique = self.data[self.data['numero_joueur'] == numero_joueur]
        performances_recentes = historique.tail(self.config['rolling_window'])
        stats = self._calculer_stats_globales(numero_joueur)
        return {
            'historique': historique,
            'performances_recentes': performances_recentes,
            'statistiques_globales': self._calculer_stats_globales(numero_joueur)
        }
    
    def _calculer_stats_globales(self, numero_joueur):
        """
        Calcule des statistiques globales pour un joueur.
        """
        data_joueur = self.data[self.data['numero_joueur'] == numero_joueur]
        return {
            'moyenne_position': round(data_joueur['position_arrivee'].mean(), 1) if not data_joueur.empty else None,
            'meilleure_position': data_joueur['position_arrivee'].min() if not data_joueur.empty else None,
            'pire_position': data_joueur['position_arrivee'].max() if not data_joueur.empty else None,
            'ecart_type': round(data_joueur['position_arrivee'].std(), 1) if not data_joueur.empty else None
        }
    
    def _convertir_risque_position(self, analyse_risques):
        """
        Convertit le niveau de risque en une valeur numérique pour la pondération.
        Par exemple : faible = 1, moyen = 2, élevé = 3.
        """
        mapping = {"faible": 1, "moyen": 2, "élevé": 3, "inconnu": 2}
        return mapping.get(analyse_risques.get("niveau_risque", "inconnu"), 2)
    
    def _analyser_patterns_recents(self, donnees_base):
        """
        Analyse les patterns récents à partir des données de base.
        Retourne une position attendue (dummy) basée sur l'analyse des patterns.
        """
        patterns = self.analyses['patterns'].patterns_position()
        numero_joueur = donnees_base['historique']['numero_joueur'].iloc[0]
        return patterns.get(numero_joueur, donnees_base['statistiques_globales']['moyenne_position'])
    
    def _calculer_prediction_principale(self, donnees_base, analyse_temps, analyse_risques):
        """
        Calcule la prédiction principale en combinant l'historique, la tendance,
        le risque et les patterns récents.
        """
        poids = self.config['coefficients']
        prediction_value = (
            donnees_base['statistiques_globales']['moyenne_position'] * poids['historique'] +
            analyse_temps['tendance_position'] * poids['tendance'] +
            self._convertir_risque_position(analyse_risques) * poids['risques'] +
            self._analyser_patterns_recents(donnees_base) * poids['patterns']
        )
        return {
            'position_plus_probable': round(prediction_value, 1),
            'facteurs_influence': {
                'historique': donnees_base['statistiques_globales']['moyenne_position'],
                'tendance': analyse_temps['tendance_position'],
                'niveau_risque': analyse_risques.get("niveau_risque", "inconnu"),
                'patterns': self._analyser_patterns_recents(donnees_base)
            }
        }
    
    def _calculer_probabilites_positions(self, prediction, intervalles):
        """
        Génère une distribution de probabilités basée sur l'intervalle de confiance.
        (Implémentation d'exemple)
        """
        min_val = intervalles['intervalle_90']['min']
        max_val = intervalles['intervalle_90']['max']
        positions = np.linspace(min_val, max_val, 5)
        probabilites = np.random.dirichlet(np.ones(len(positions)), size=1)[0]
        return dict(zip(positions.round(1), np.round(probabilites * 100, 1)))
    
    def _identifier_facteurs_influence(self, donnees_base, analyse_temps, analyse_risques):
        """
        Identifie les principaux facteurs d'influence de la prédiction.
        """
        return {
            "niveau_risque": analyse_risques.get("niveau_risque", "inconnu"),
            "tendance": analyse_temps.get("tendance_position", None)
        }
    
    def _generer_recommandations(self, prediction, intervalles):
        """
        Génère des recommandations basées sur l'analyse.
        """
        recommandations = []
        niveau_risque = prediction['facteurs_influence'].get('niveau_risque', 'inconnu')
        if niveau_risque == 'élevé':
            recommandations.append("Attention au niveau de risque élevé")
        if intervalles['intervalle_90']['min'] == 1:
            recommandations.append("Bonne opportunité de victoire")
        return recommandations
    
    def _assembler_rapport_final(self, numero_joueur, prediction, intervalles):
        """
        Assemble le rapport final de prédiction en intégrant toutes les analyses.
        """
        rapport = {
            'joueur': numero_joueur,
            'prediction': {
                'position_prevue': prediction['position_plus_probable'],
                'intervalles_confiance': intervalles,
                'probabilites': self._calculer_probabilites_positions(prediction, intervalles)
            },
            'analyses': {
                'tendances': self.analyses['temporelle'].analyser_evolution(numero_joueur),
                'risques': self.analyses['ecarts'].analyser_risques(numero_joueur),
                'patterns': self.analyses['patterns'].patterns_position().get(numero_joueur, None)
            },
            'recommandations': self._generer_recommandations(prediction, intervalles)
        }
        return rapport

# --- Interface Utilisateur via Streamlit ---

class InterfaceUtilisateur:
    """
    Interface interactive pour l'utilisateur, basée sur Streamlit.
    """
    def __init__(self, systeme_prediction):
        self.predictor = systeme_prediction
        
    def afficher_interface(self):
        st.title("Système de Prédiction des Courses")
        
        # Sélection du joueur parmi les numéros disponibles
        numero_joueur = st.selectbox(
            "Sélectionnez un joueur",
            options=self.predictor.data['numero_joueur'].unique()
        )
        
        if st.button("Générer Prédiction"):
            rapport = self.predictor.generer_prediction_complete(numero_joueur)
            if rapport:
                self._afficher_rapport(rapport)
            else:
                st.error("Aucune donnée disponible pour ce joueur.")
    
    def _afficher_rapport(self, rapport):
        st.header(f"Prédiction pour le joueur {rapport['joueur']}")
        st.subheader("Position prévue")
        st.metric(label="Position prévue", value=rapport['prediction']['position_prevue'])
        
        st.subheader("Intervalle de confiance")
        intervalle = rapport['prediction']['intervalles_confiance']['intervalle_90']
        st.write(f"Min: {intervalle['min']} - Max: {intervalle['max']}")
        
        st.subheader("Probabilités des positions")
        for pos, prob in rapport['prediction']['probabilites'].items():
            st.write(f"Position {pos}: {prob}%")
        
        st.subheader("Analyses")
        st.write("Tendances:", rapport['analyses']['tendances'])
        st.write("Risques:", rapport['analyses']['risques'])
        st.write("Patterns:", rapport['analyses']['patterns'])
        
        st.subheader("Recommandations")
        for rec in rapport['recommandations']:
            st.write(f"- {rec}")