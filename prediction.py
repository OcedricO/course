#prediction.py
from typing import List, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (train_test_split, cross_val_score)
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from database import Database
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def preparer_donnees(courses: List[Dict[str, Any]]):
    """
    Prépare les données pour l'entraînement du modèle.
    :param courses: Liste des courses.
    :return: X (features), y_encoded (labels encodés), label_encoder (pour inverser la transformation).
    """
    X, y = [], []
    for course in courses:
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]
        
        if len(numeros) >= 2:  # On utilise les deux premiers numéros pour l'exemple
            # Ajouter les deux premiers numéros comme features
            features = numeros[:2]
            
            # Ajouter la distance de la course (si disponible)
            distance = course.get('distance', 'Inconnu')
            if distance != 'Inconnu':
                features.append(int(distance.replace('m', '')))  # Convertir la distance en entier
            
            # Ajouter le type de course comme feature (encodé en entier)
            type_course = course.get('type', 'Inconnu')
            if type_course == 'Attelé':
                features.append(0)
            elif type_course == 'Plat':
                features.append(1)
            elif type_course == 'Haies':
                features.append(2)
            elif type_course == 'Steeple-chase':
                features.append(3)
            else:
                features.append(-1)  # Valeur par défaut pour les types inconnus
            
            # Ajouter le lieu de la course comme feature (encodé en entier)
            lieu = course.get('lieu', 'Inconnu')
            if lieu == 'Vincennes':
                features.append(0)
            elif lieu == 'Pau':
                features.append(1)
            elif lieu == 'Cagnes-sur-Mer':
                features.append(2)
            elif lieu == 'Deauville':
                features.append(3)
            else:
                features.append(-1)  # Valeur par défaut pour les lieux inconnus
            
            X.append(features)
            y.append(numeros[2])  # On prédit le troisième numéro
    
    # Transformer les labels pour qu'ils soient des entiers consécutifs commençant à 0
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Afficher les classes uniques dans y_encoded
    unique_classes = np.unique(y_encoded)
    print(f"Classes uniques dans y_encoded : {unique_classes}")
    
    # Forcer les classes à être consécutives
    y_encoded = np.arange(len(y_encoded)) % len(unique_classes)
    
    print(f"Classes forcées à être consécutives : {np.unique(y_encoded)}")
    print(f"Données préparées : X = {X}, y = {y}, y_encoded = {y_encoded}")  # Afficher les données
    return np.array(X), y_encoded, label_encoder

def entrainer_modele(X, y_encoded):
    """
    Entraîne un modèle XGBoost.
    :param X: Features.
    :param y_encoded: Labels encodés.
    :return: Modèle entraîné.
    """
    # Afficher les classes uniques dans y_encoded
    unique_classes = np.unique(y_encoded)
    print(f"Classes uniques dans y_encoded : {unique_classes}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    model = XGBClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Évaluation du modèle
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Précision du modèle : {accuracy * 100:.1f}%")
    
    return model

def afficher_graphique_precision(precisions: List[float], labels: List[str]):
    """
    Affiche un graphique en courbes de la précision du modèle.
    :param precisions: Liste des précisions du modèle.
    :param labels: Liste des labels pour l'axe des x.
    """
    plt.plot(labels, precisions, marker='o', color='red')
    plt.xlabel('Paramètres')
    plt.ylabel('Précision (%)')
    plt.title('Précision du modèle en fonction des paramètres')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Afficher ou sauvegarder le graphique
    try:
        plt.show()  # Afficher le graphique
    except Exception as e:
        print(f"Erreur lors de l'affichage du graphique : {e}")
        plt.savefig('graphique_precision.png')  # Sauvegarder le graphique dans un fichier
        print("Le graphique a été sauvegardé dans 'graphique_precision.png'.")

def preparer_donnees_tranche_1_5(courses):
    """
    Prépare les données pour prédire les numéros dans la tranche 1-5.
    :param courses: Liste des courses.
    :return: X (features), y_encoded (labels encodés), label_encoders (pour inverser la transformation).
    """
    data = []

    for course in courses:
        # Extraire les fonctionnalités
        discipline = course.get('type_course', 'Inconnu')  # Utiliser 'type_course' au lieu de 'discipline'
        distance = course.get('distance', 'Inconnu')
        lieu = course.get('lieu', 'Inconnu')

        # Extraire les numéros de la synthèse
        synthese = course.get('synthese', '')
        synthese_list = [x.strip() for x in synthese.split('-') if x.strip()]
        numeros = [int(x.replace('e', '')) for x in synthese_list if x.replace('e', '').isdigit()]

        # Identifier les numéros dans la tranche 1-5
        numeros_tranche_1_5 = [num for num in numeros if 1 <= num <= 5]

        # Ajouter chaque numéro de la tranche 1-5 comme une ligne dans le DataFrame
        for num in numeros_tranche_1_5:
            data.append({
                'discipline': discipline,  # Utiliser 'discipline' comme nom de colonne
                'distance': distance,
                'lieu': lieu,
                'numero': num
            })

    # Convertir en DataFrame
    df = pd.DataFrame(data)

    # Encodage des variables catégorielles
    label_encoders = {}
    for col in ['discipline', 'distance', 'lieu']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le  # Sauvegarder les encodeurs pour plus tard

    # Séparer les fonctionnalités (X) et la cible (y)
    X = df[['discipline', 'distance', 'lieu']]
    y = df['numero']

    # Encoder la cible (numéros)
    label_encoder_numero = LabelEncoder()
    y_encoded = label_encoder_numero.fit_transform(y)

    return X, y_encoded, label_encoders, label_encoder_numero

def entrainer_modele_tranche_1_5(db: Database):
    # Récupérer toutes les courses
    courses = db.get_courses()

    # Préparer les données
    X, y_encoded, label_encoders, label_encoder_numero = preparer_donnees_tranche_1_5(courses)

    # Entraîner le modèle
    model = entrainer_modele(X, y_encoded)

    # Retourner le modèle et les encodeurs pour les utiliser plus tard
    return model, label_encoders, label_encoder_numero

def predire_tranche_1_5(model, label_encoders, label_encoder_numero, nouvelle_course, top_n=3):
    """
    Prédit les numéros dans la tranche 1-5 pour une nouvelle course.
    :param model: Modèle entraîné.
    :param label_encoders: Dictionnaire des encodeurs pour les fonctionnalités.
    :param label_encoder_numero: Encodeur pour les numéros.
    :param nouvelle_course: Dictionnaire contenant les informations de la nouvelle course.
    :param top_n: Nombre de numéros à prédire.
    :return: Numéros prédits dans la tranche 1-5 avec leurs probabilités.
    """
    # Encoder les valeurs de la nouvelle course
    nouvelle_course_encoded = {
        'discipline': label_encoders['discipline'].transform([nouvelle_course['discipline']])[0],
        'distance': label_encoders['distance'].transform([nouvelle_course['distance']])[0],
        'lieu': label_encoders['lieu'].transform([nouvelle_course['lieu']])[0]
    }

    # Convertir en DataFrame
    nouvelle_course_df = pd.DataFrame([nouvelle_course_encoded])

    # Faire la prédiction des probabilités
    probabilites = model.predict_proba(nouvelle_course_df)[0]

    # Obtenir les indices des top_n numéros les plus probables
    top_indices = probabilites.argsort()[-top_n:][::-1]

    # Décoder les numéros prédits et leurs probabilités
    numeros_predits = label_encoder_numero.inverse_transform(top_indices)
    probabilites_predits = probabilites[top_indices]

    return list(zip(numeros_predits, probabilites_predits))

def entrainer_modele_compare(X, y_encoded):
    """
    Entraîne et compare plusieurs modèles de machine learning.
    :param X: Features.
    :param y_encoded: Labels encodés.
    :return: Meilleur modèle entraîné.
    """
    models = {
        'XGBoost': XGBClassifier(n_estimators=100, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    best_model = None
    best_score = 0
    
    for name, model in models.items():
        scores = cross_val_score(model, X, y_encoded, cv=5, scoring='accuracy')
        mean_score = scores.mean()
        print(f"{name} : Précision moyenne = {mean_score * 100:.1f}%")
        
        if mean_score > best_score:
            best_score = mean_score
            best_model = model
    
    best_model.fit(X, y_encoded)
    return best_model