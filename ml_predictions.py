# ml_predictions.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from typing import List, Dict, Any, Tuple 

def preparer_donnees_ml(courses: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, List[int]]:
    """Version améliorée avec features temporelles"""
    X = []
    y = []
    
    for course in courses:
        try:
            date_course = pd.to_datetime(course['date_course'])
            features = [
                date_course.dayofweek,  # Jour de la semaine (0=lundi)
                date_course.month,      # Mois de l'année
                len(course.get('partants', [])),
                course.get('temperature', 20),
                date_course.year        # Année comme feature
            ]
            
            if course.get("arrivee") and len(course["arrivee"]) > 0:
                X.append(features)
                y.append(course["arrivee"][0])
                
        except KeyError as e:
            print(f"Donnée manquante : {str(e)}")
            continue
            
    return pd.DataFrame(X, columns=['jour_semaine', 'mois', 'nb_partants', 'temperature', 'annee']), y

def entrainer_modele(X, y):
    """Version corrigée avec encodage robuste"""
    # Convertir y en entiers
    y = [int(num) for num in y]
    
    # Créer et ajuster l'encodeur
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Entraînement du modèle
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    
    return model, label_encoder  # Retourner l'encodeur