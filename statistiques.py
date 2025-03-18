# statistiques.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List
from datetime import datetime
from database import Database
from analyse import calculer_ecarts_numeros_arrivee_avec_participation
from prediction_avancee import (
    AnalyseTemporelle,
    SystemePredictionGlobal,
    InterfaceUtilisateur
)

class AnalyseStatistiqueAvancee:
    def __init__(self, gestionnaire):
        self.gestionnaire = gestionnaire
        self.data = self._preparer_donnees()
        self.analyse_temporelle = AnalyseTemporelle(self.data)
        self.systeme_prediction = SystemePredictionGlobal(self.data)
        required_columns = ['numero_joueur', 'date', 'position_arrivee']
        for col in required_columns:
            if col not in self.data.columns:
                raise ValueError(f"Colonne manquante : {col}. Vérifiez la préparation des données.")
    
    def _preparer_donnees(self) -> pd.DataFrame:
        """Version corrigée avec gestion temporelle des écarts"""
        courses = sorted(self.gestionnaire.db.get_courses(), key=lambda x: x['date_course'])
        
        data = []
        historique_courses = []
        for course in courses:
            # Accumuler les courses dans l'ordre chronologique
            historique_courses.append(course)
            
            # Traitement de l'arrivée
            arrivee = [x.strip() for x in course['arrivee'].split('-') if x.strip()]
            arrivee = list(map(int, arrivee))
            
            # Traitement de la synthèse
            synthese = [x.strip().replace('e', '') 
                       for x in course['synthese'].split('-') if x.strip()]
            synthese = list(map(int, synthese))
            
            # Traitement des partants
            partants = list(map(int, course['partants'].split(','))) if course['partants'] else []
            
            # Calcul des écarts
            ecarts = calculer_ecarts_numeros_arrivee_avec_participation(historique_courses)
            
            for num in set(arrivee + synthese + partants):
                entry = {
                    'numero_joueur': num,
                    'date': datetime.strptime(course['date_course'], '%Y-%m-%d'),
                    'position_arrivee': arrivee.index(num)+1 if num in arrivee else np.nan,
                    'present_synthese': num in synthese,
                    'partant': num in partants,
                    'ecart_actuel': ecarts.get(num, {}).get('ecart_actuel', 0),
                    'ecart_max': ecarts.get(num, {}).get('ecart_max', 0),
                    'participations': ecarts.get(num, {}).get('courses_participées', 0)
                }
                data.append(entry)
        
        df = pd.DataFrame(data)
        df['ratio_ecart'] = df.apply(lambda x: x['ecart_actuel']/x['ecart_max'] if x['ecart_max'] > 0 else 0, axis=1)
        df['plage_numeros'] = pd.cut(df['numero_joueur'], 
                                   bins=[0, 5, 10, 15, 20],
                                   labels=['1-5', '5-10', '10-15', '15-20'])
        
        # Vérification finale des colonnes
        required_columns = ['numero_joueur', 'date', 'position_arrivee', 
                        'present_synthese', 'partant', 
                        'ecart_actuel', 'ecart_max']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Colonne manquante : {col}")    
        return df

    def analyser_parite(self) -> Dict[str, Any]:
        """Analyse avancée de la parité avec tests statistiques"""
        df = self.data.copy()
        df['parite'] = np.where(df['numero_joueur'] % 2 == 0, 'Pair', 'Impair')
        
        # Calcul des statistiques
        stats = {
            'distribution': df['parite'].value_counts().to_dict(),
            'taux_victoire': df.groupby('parite')['position_arrivee'].apply(
                lambda x: (x == 1).mean()).to_dict(),
            'ecart_moyen': df.groupby('parite')['ratio_ecart'].mean().to_dict()
        }
        
        # Visualisation
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x='parite', y='position_arrivee', hue='present_synthese')
        plt.title('Performance par parité et présence en synthèse')
        plt.tight_layout()
        plt.show()
        
        return stats

    def analyser_plages(self) -> pd.DataFrame:
        """Analyse détaillée par plages de numéros avec intervalle de confiance"""
        df = self.data.copy()
        
        # Calcul des métriques CORRIGÉ
        analysis = df.groupby('plage_numeros').agg(
            nombre=('numero_joueur', 'count'),
            taux_victoire=('position_arrivee', lambda x: (x == 1).mean()),
            ecart_moyen=('ratio_ecart', 'mean'),
            presence_synthese=('present_synthese', 'mean')
        ).reset_index()

        # Visualisation interactive CORRIGÉE
        plt.figure(figsize=(14, 7))
        ax = sns.barplot(
        data=analysis,
        x='plage_numeros',
        y='taux_victoire',
        hue='plage_numeros',  # Ajouté
        palette='viridis',
        edgecolor='black',
        legend=False  # Ajouté
        )
        
        # Ajout des valeurs sur les barres
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.1%}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points')
            
        plt.title('Taux de victoire par plage de numéros')
        plt.xlabel('Plage de numéros')
        plt.ylabel('Taux de victoire (%)')
        plt.ylim(0, 0.5)
        plt.show()
        
        return analysis
    def analyser_ecarts(self) -> Dict[str, Any]:
        """Analyse des écarts avec gestion des cas limites"""
        try:
            # Vérification des données
            print("Données initiales :")
            print(self.data[['ratio_ecart', 'position_arrivee', 'ecart_max']].head())
            print(f"Nombre de lignes : {len(self.data)}")
            print(f"Valeurs manquantes dans 'ratio_ecart' : {self.data['ratio_ecart'].isna().sum()}")
            print(f"Valeurs manquantes dans 'position_arrivee' : {self.data['position_arrivee'].isna().sum()}")
            print(f"Valeurs uniques dans 'ratio_ecart' : {self.data['ratio_ecart'].nunique()}")
            print(f"Valeurs uniques dans 'position_arrivee' : {self.data['position_arrivee'].nunique()}")

            # Filtrer les joueurs qui ont terminé la course
            df = self.data.dropna(subset=['position_arrivee']).copy()
            print(f"Nombre de joueurs ayant terminé la course : {len(df)}")

            # Gestion des cas limites
            if len(df) < 2 or df['ratio_ecart'].nunique() == 1 or df['position_arrivee'].nunique() == 1:
                print("Cas limite détecté : données insuffisantes ou non variées.")
                return {
                    'distribution_zones': {"Sûr": 0, "Modéré": 0, "Critique": 0},
                    'performance_zone': {"Sûr": 0, "Modéré": 0, "Critique": 0},
                    'correlation': 0.0
                }

            # Découpage en zones de risque
            df['zone_risque'] = pd.cut(
                df['ratio_ecart'],
                bins=[-0.1, 0.3, 0.7, 1.1],
                labels=['Sûr', 'Modéré', 'Critique'],
                ordered=False
            )

            # Vérification des zones de risque
            print("Répartition des zones de risque :")
            print(df['zone_risque'].value_counts())

            # Calcul sécurisé de la corrélation
            corr_matrix = df[['ratio_ecart', 'position_arrivee']].corr(numeric_only=True)
            correlation = corr_matrix.iloc[0, 1] if not corr_matrix.empty else 0.0

            # Visualisation conditionnelle
            if not df.empty and len(df) > 10:  # Seulement si suffisamment de données
                fig = plt.figure(figsize=(14, 10))
                ax = fig.add_subplot(111, projection='3d')
                
                sc = ax.scatter(
                    df['ratio_ecart'], 
                    df['ecart_max'], 
                    df['position_arrivee'],
                    c=df['position_arrivee'], 
                    cmap='viridis', 
                    s=50
                )
                
                ax.set_xlabel('Ratio Écart')
                ax.set_ylabel('Écart Max Historique')
                ax.set_zlabel('Position Arrivée')
                plt.title('Relation 3D entre les écarts et la performance')
                fig.colorbar(sc)
                plt.show()
            else:
                print("Pas assez de données pour la visualisation 3D")

            return {
                'distribution_zones': df['zone_risque'].value_counts().to_dict(),
                'performance_zone': df.groupby('zone_risque')['position_arrivee'].mean().to_dict(),
                'correlation': correlation
            }

        except Exception as e:
            print(f"Erreur dans l'analyse des écarts : {str(e)}")
            return {
                'distribution_zones': {"Sûr": 0, "Modéré": 0, "Critique": 0},
                'performance_zone': {"Sûr": 0, "Modéré": 0, "Critique": 0},
                'correlation': 0.0
            }
    def analyser_abandons(self) -> Dict[str, Any]:
        """Analyse des joueurs qui n'ont pas terminé la course"""
        try:
            # Filtrer les joueurs qui n'ont pas terminé la course
            df_abandons = self.data[self.data['position_arrivee'].isna()].copy()
            print(f"Nombre de joueurs n'ayant pas terminé la course : {len(df_abandons)}")

            # Calculer des indicateurs pour les abandons
            taux_abandons = len(df_abandons) / len(self.data)
            ecart_moyen_abandons = df_abandons['ratio_ecart'].mean()

            return {
                'taux_abandons': taux_abandons,
                'ecart_moyen_abandons': ecart_moyen_abandons
            }

        except Exception as e:
            print(f"Erreur dans l'analyse des abandons : {str(e)}")
            return {
                'taux_abandons': 0.0,
                'ecart_moyen_abandons': 0.0
            }

    def generer_rapport_complet(self):
        """Génère un rapport consolidé avec gestion des données manquantes"""
        try:
            # Initialisation des variables
            self.data['parite'] = np.where(self.data['numero_joueur'] % 2 == 0, 'Pair', 'Impair')
            self.data['taux_victoire'] = (self.data['position_arrivee'] == 1).astype(int)

            # Génération sécurisée des composants du rapport
            rapport = {
                'parite': self.analyser_parite(),
                'plages': self.analyser_plages().to_dict(),
                'ecarts': self.analyser_ecarts(),
                'tendances': self.analyser_tendances()
            }

            # Configuration de la visualisation
            plt.figure(figsize=(16, 12))
            
            # Graphique 1 - Boxplot parité (inchangé)
            plt.subplot(2, 2, 1)
            sns.boxplot(data=self.data, x='parite', y='position_arrivee')
            plt.title('Distribution des positions par parité')

            # Graphique 2 - Heatmap interactions (inchangé)
            plt.subplot(2, 2, 2)
            cross_tab = pd.crosstab(self.data['plage_numeros'], self.data['parite'])
            sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlGnBu')
            plt.title('Interaction Plages/Parité')

            # Graphique 3 - Relation écart/performance (inchangé)
            plt.subplot(2, 2, 3)
            sns.scatterplot(
                data=self.data,
                x='ratio_ecart', 
                y='position_arrivee',
                hue='plage_numeros',
                palette='deep',
                size='ecart_max',
                sizes=(20, 200)
            )
            plt.title('Relation Écart/Performance (taille = écart max)')

            # Graphique 4 - Résumé statistique (corrigé)
            plt.subplot(2, 2, 4)
            stats_summary = pd.DataFrame({
                'Métrique': ['Taux victoire', 'Ecart moyen', 'Présence synthèse'],
                'Valeur': [
                    rapport['parite'].get('taux_victoire', {}).get('Pair', 0),
                    rapport['ecarts'].get('performance_zone', {}).get('Modéré', 0),
                    self.data['present_synthese'].mean()
                ]
            })
            sns.barplot(
                data=stats_summary,
                x='Métrique',
                y='Valeur',
                hue='Métrique',
                palette='rocket',
                legend=False
            )
            plt.title('Indicateurs Clés')
            plt.ylim(0, 1)

            plt.tight_layout()
            plt.show()

            # Affichage texte sécurisé
            print("\n=== Rapport Consolidé ===")
            print(f"Données clés :")
            print(f"- Nombre total d'observations : {len(self.data)}")
            
            correlation = rapport['ecarts'].get('correlation', 0)
            print(f"- Corrélation écart/performance : {correlation:.2%}" if not np.isnan(correlation) else "- Corrélation : non calculable")

            # Affichage détaillé sécurisé
            print("\nPerformance par zone de risque :")
            zones = ['Sûr', 'Modéré', 'Critique']
            for zone in zones:
                valeur = rapport['ecarts'].get('performance_zone', {}).get(zone, 'N/A')
                print(f"  - {zone}: {valeur if isinstance(valeur, str) else f'{valeur:.2f}'}")

            return rapport

        except Exception as e:
            print(f"Erreur lors de la génération du rapport : {str(e)}")
            return {}

    def analyser_tendances(self):
        """Nouvelle méthode pour l'analyse temporelle"""
        return {
            'quotidien': self.analyse_temporelle.evolution_quotidienne().to_dict(),
            'hebdomadaire': self.analyse_temporelle.tendances_hebdomadaires().to_dict(),
            'performances': self.analyse_temporelle.periodes_performances()
        }

    def visualiser_evolution(self, numero_joueur=None):
        """Wrapper pour la visualisation temporelle"""
        self.analyse_temporelle.visualiser_evolution(numero_joueur)

    def generer_prediction(self, numero_joueur):
        """Intégration avec le système existant"""
        return self.systeme_prediction.generer_prediction_complete(numero_joueur)  
    
class AnalyseTemporelle:
    def __init__(self, donnees):
            """Adaptation aux noms de colonnes existants"""
            self.data = donnees.copy()
            # Conversion et tri des dates
            self.data['date'] = pd.to_datetime(self.data['date'], errors="coerce")
            self.data.sort_values(by='date', inplace=True)
            
    def evolution_quotidienne(self, numero_joueur=None):
        """Analyse l'évolution quotidienne avec le nom de colonne corrigé"""
        data = self.data if numero_joueur is None else self.data[self.data['numero_joueur'] == numero_joueur]  # 🔄
        
        return data.groupby(['numero_joueur', 'date']).agg({  # 🔄
            'position_arrivee': 'mean',
            'ecart_actuel': 'mean',
            'ratio_ecart': 'mean'
        }).reset_index()

    def tendances_hebdomadaires(self):
            """Analyse hebdomadaire avec gestion des données manquantes"""
            if self.data.empty:
                return pd.DataFrame()
                
            data_temp = self.data.copy()
            data_temp['semaine'] = data_temp['date'].dt.isocalendar().week
            return data_temp.groupby(['numero_joueur', 'semaine']).agg({
                'position_arrivee': ['mean', 'min', 'max', 'count'],
                'ecart_actuel': 'mean'
            }).reset_index()

    def analyse_progression(self):
            """Analyse de progression avec vérification des données"""
            resultats = {}
            unique_numeros = self.data['numero_joueur'].unique()
            
            for num in unique_numeros:
                donnees_num = self.data[self.data['numero_joueur'] == num].copy()
                if len(donnees_num) < 2:
                    continue
                    
                donnees_num.sort_values(by='date', inplace=True)
                
                # Calcul des moyennes mobiles avec gestion des NaN
                donnees_num['moyenne_mobile_position'] = (
                    donnees_num['position_arrivee']
                    .rolling(window=5, min_periods=1)
                    .mean()
                )
                
                donnees_num['moyenne_mobile_ecart'] = (
                    donnees_num['ecart_actuel']
                    .rolling(window=5, min_periods=1)
                    .mean()
                )

                resultats[num] = {
                    'donnees': donnees_num,
                    'amelioration': self._calculer_amelioration(donnees_num)
                }
            return resultats

    def _calculer_amelioration(self, donnees):
            """Calcul sécurisé de l'amélioration"""
            if len(donnees) >= 10:
                return (
                    donnees['moyenne_mobile_position'].iloc[-5:].mean() - 
                    donnees['moyenne_mobile_position'].iloc[:5].mean()
                )
            return None

    def periodes_performances(self, numero_joueur=None):
        """Analyse des périodes de performance avec filtre optionnel"""
        data = self.data if numero_joueur is None else self.data[self.data['numero_joueur'] == numero_joueur]
        resultats = {}
        
        for num in data['numero_joueur'].unique():
            donnees_num = data[data['numero_joueur'] == num].copy()
            if len(donnees_num) < 5:
                continue
                
            donnees_num['moyenne_mobile'] = (
                donnees_num['position_arrivee']
                .rolling(window=5, min_periods=1)
                .mean()
            )
            
            meilleure = donnees_num.nsmallest(1, 'moyenne_mobile')
            pire = donnees_num.nlargest(1, 'moyenne_mobile')
            
            resultats[num] = {
                'meilleure_periode': self._formater_periode(meilleure),
                'pire_periode': self._formater_periode(pire)
            }
        return resultats

    def _formater_periode(self, periode):
            """Formatage cohérent des dates de période"""
            if not periode.empty:
                return {
                    'debut': periode['date'].iloc[0].strftime('%Y-%m-%d'),
                    'moyenne': round(periode['moyenne_mobile'].iloc[0], 2)
                }
            return None

    def visualiser_evolution(self, numero_joueur=None):
            """Visualisation adaptée avec gestion des couleurs"""
            plt.figure(figsize=(15, 10))
            data = self.data if numero_joueur is None else self.data[self.data['numero_joueur'] == numero_joueur]
            
            # Configuration des palettes
            palette = 'viridis' if numero_joueur is None else None
            hue = None if numero_joueur else 'numero_joueur'
            
            # Graphique des positions
            plt.subplot(2, 1, 1)
            sns.lineplot(
                data=data,
                x='date',
                y='position_arrivee',
                hue=hue,
                palette=palette,
                estimator=None,
                marker='o'
            )
            plt.title(f'Évolution des positions - {"Tous" if numero_joueur is None else f"Numéro {numero_joueur}"}')
            
            # Graphique des écarts
            plt.subplot(2, 1, 2)
            sns.lineplot(
                data=data,
                x='date',
                y='ecart_actuel',
                hue=hue,
                palette=palette,
                estimator=None,
                marker='o'
            )
            plt.title('Évolution des écarts actuels')
            
            plt.tight_layout()
            plt.show()