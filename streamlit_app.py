import streamlit as st
import pandas as pd
import sqlite3
from database import Database
from statistiques import AnalyseStatistiqueAvancee

# Configuration de la page
st.set_page_config(page_title="Analyse Courses Hippiques", layout="wide")

# Connexion à la base de données
@st.cache_resource
def init_db():
    return Database('courses.db')

db = init_db()

# Titre de l'application
st.title("Analyse des Courses Hippiques")

# Menu latéral
st.sidebar.header("Menu")
menu_option = st.sidebar.selectbox(
    "Choisissez une option",
    ["Accueil", "Analyser un numéro", "Statistiques", "À propos"]
)

if menu_option == "Accueil":
    st.header("Bienvenue sur l'analyse des courses hippiques")
    st.write("Utilisez le menu de gauche pour naviguer entre les différentes sections.")
    
    # Afficher les dernières courses
    st.subheader("Dernières courses enregistrées")
    try:
        courses = db.get_courses(limit=5)
        if courses:
            st.dataframe(pd.DataFrame(courses))
        else:
            st.warning("Aucune course trouvée dans la base de données.")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")

elif menu_option == "Analyser un numéro":
    st.header("Analyse d'un numéro")
    
    # Sélection du numéro
    numero = st.number_input("Entrez le numéro à analyser", min_value=1, step=1)
    
    if st.button("Analyser"):
        with st.spinner("Analyse en cours..."):
            try:
                # Initialisation de l'analyseur
                analyseur = AnalyseStatistiqueAvancee(db)
                
                # Récupération des données
                resultats = analyseur.analyser_joueur(numero)
                
                if "erreur" in resultats:
                    st.error(resultats["erreur"])
                else:
                    # Affichage des résultats
                    st.subheader(f"Analyse du numéro {numero}")
                    
                    # Statistiques générales
                    st.metric("Participations", resultats["participations"]["participations"])
                    st.metric("Taux d'abandon", f"{resultats['participations']['taux_abandon']}%")
                    
                    # Détails des courses terminées
                    st.subheader("Performances sur courses terminées")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Courses terminées", resultats["courses_terminees"]["nombre"])
                    with col2:
                        st.metric("Position moyenne", f"{resultats['courses_terminees']['moyenne_position']:.1f}")
                    with col3:
                        st.metric("Régularité top 3", f"{resultats['courses_terminees']['regularite_top3']}%")
                    
                    # Probabilités par position
                    st.subheader("Probabilités par position")
                    probas = pd.DataFrame(
                        resultats["probabilites"].items(),
                        columns=["Position", "Probabilité"]
                    )
                    st.bar_chart(probas.set_index("Position") * 100)
                    
            except Exception as e:
                st.error(f"Une erreur est survenue : {str(e)}")

elif menu_option == "Statistiques":
    st.header("Statistiques globales")
    
    try:
        # Récupération des statistiques globales
        stats = db.obtenir_statistiques_globales()
        
        if stats:
            st.subheader("Résumé des courses")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total des courses", stats.get("total_courses", 0))
            with col2:
                st.metric("Moyenne de partants/course", f"{stats.get('moyenne_partants', 0):.1f}")
            with col3:
                st.metric("Taux d'abandon moyen", f"{stats.get('taux_abandon', 0):.1f}%")
            
            # Graphique des disciplines
            st.subheader("Répartition par discipline")
            if "repartition_disciplines" in stats:
                df_disciplines = pd.DataFrame(
                    stats["repartition_disciplines"].items(),
                    columns=["Discipline", "Nombre de courses"]
                )
                st.bar_chart(df_disciplines.set_index("Discipline"))
        else:
            st.warning("Aucune statistique disponible.")
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des statistiques : {e}")

else:  # À propos
    st.header("À propos")
    st.write("""
    ## Application d'analyse des courses hippiques
    
    Cette application permet d'analyser les performances des chevaux
    et de générer des statistiques avancées sur les courses.
    
    **Fonctionnalités :**
    - Analyse détaillée par numéro
    - Statistiques globales
    - Visualisation des données
    
    *Développé avec Python et Streamlit*
    """)
