# database.py
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

query = "SELECT *, date_course as date FROM courses"

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        print(f"Chemin de la base de données : {self.db_path}")
        self.init_db()  # Appeler init_db() pour créer la base de données si elle n'existe pas

    def init_db(self) -> None:
        """Initialise la base de données."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS fichiers_traites (
                    nom_fichier TEXT PRIMARY KEY,
                    date_traitement TIMESTAMP,
                    statut_traitement TEXT,
                    erreur TEXT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY,
                    date_course DATE,
                    lieu TEXT,
                    type_course TEXT,
                    distance TEXT,
                    arrivee TEXT,
                    synthese TEXT,
                    partants TEXT,
                    nom_fichier TEXT,
                    FOREIGN KEY (nom_fichier) REFERENCES fichiers_traites(nom_fichier)
                )
            ''')
            conn.commit()
            print("Base de données initialisée avec succès.")
    
    def save_course(self, nom_fichier: str, donnees: Dict[str, Any]) -> bool:
        """
        Sauvegarde les données d'une course dans la base.
        :param nom_fichier: Nom du fichier traité.
        :param donnees: Dictionnaire contenant les données de la course.
        :return: True si la sauvegarde a réussi, False sinon.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            try:
                cur.execute('SELECT nom_fichier FROM fichiers_traites WHERE nom_fichier = ?', (nom_fichier,))
                if cur.fetchone():
                    print(f"Le fichier {nom_fichier} a déjà été traité.")
                    return False
                
                cur.execute('''
                    INSERT INTO fichiers_traites (nom_fichier, date_traitement, statut_traitement, erreur)
                    VALUES (?, ?, ?, ?)
                ''', (nom_fichier, datetime.now(), 'success', None))
                
                cur.execute('''
                    INSERT INTO courses (date_course, lieu, type_course, distance, arrivee, synthese, partants, nom_fichier)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    donnees['date'],
                    donnees['lieu'],
                    donnees['type'],
                    donnees['distance'],
                    donnees['arrivée'],
                    donnees['synthese'],
                    ','.join(map(str, donnees['partants'])),  # Convertir la liste en chaîne
                    nom_fichier
                ))
                
                conn.commit()
                print(f"Course sauvegardée : {donnees}")
                return True
            except sqlite3.Error as e:
                print(f"Erreur lors de la sauvegarde : {e}")
                conn.rollback()
                return False
    
    def get_processed_files(self) -> List[str]:
        """Récupère la liste des fichiers déjà traités."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT nom_fichier FROM fichiers_traites')
            return [row[0] for row in cur.fetchall()]
        
    def get_courses(
    self,
    type_course: Optional[str] = None,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    distance: Optional[str] = None
) -> List[Dict[str, Any]]:
        """
        Récupère les courses depuis la base de données avec des filtres optionnels.
        Garantit la présence des colonnes critiques.
        """
        try:
            # Liste des colonnes essentielles à récupérer
            columns = [
                "date_course",
                "type_course",
                "distance",
                "lieu",
                "partants",
                "arrivee",
                "synthese"
            ]

            query = f"SELECT {', '.join(columns)} FROM courses"
            conditions = []
            params = []

            # Construction dynamique des filtres
            if type_course:
                conditions.append("type_course = ?")
                params.append(type_course)
            
            if date_debut:
                conditions.append("date(date_course) >= date(?)")
                params.append(date_debut)
            
            if date_fin:
                conditions.append("date(date_course) <= date(?)")
                params.append(date_fin)
            
            if distance:
                conditions.append("distance = ?")
                params.append(distance)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY date(date_course) ASC"

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                
                cur.execute(query, params)
                rows = cur.fetchall()
                
                # Conversion en dictionnaires avec validation
                courses = []
                required_keys = {'date_course', 'partants', 'arrivee'}
                
                for row in rows:
                    course = dict(row)
                    missing = required_keys - course.keys()
                    if missing:
                        raise KeyError(f"Colonnes manquantes : {missing}")
                    courses.append(course)

                return courses

        except sqlite3.Error as e:
            print(f"Erreur SQLite : {str(e)}")
            return []
        except KeyError as ke:
            print(f"Problème d'intégrité des données : {str(ke)}")
            return []
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM courses')
            total_courses = cur.fetchone()[0]
            cur.execute('SELECT COUNT(DISTINCT type_course) FROM courses')
            nb_types = cur.fetchone()[0]
            cur.execute('SELECT MIN(date_course), MAX(date_course) FROM courses')
            premiere_course, derniere_course = cur.fetchone()
            return {
                'total_courses': total_courses,
                'nb_types': nb_types,
                'premiere_course': premiere_course,
                'derniere_course': derniere_course
            }

    def combinaison_existe(self, discipline: str, distance: str, lieu: str) -> bool:
        """
        Vérifie si une combinaison discipline-distance-lieu existe dans la base de données.
        :param discipline: La discipline de la course.
        :param distance: La distance de la course.
        :param lieu: Le lieu de la course.
        :return: True si la combinaison existe, False sinon.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT COUNT(*) FROM courses
                WHERE type_course = ? AND distance = ? AND lieu = ?
            ''', (discipline, distance, lieu))
            count = cur.fetchone()[0]
            return count > 0

    def obtenir_lieux_disponibles_par_discipline_et_distance(self, discipline: str, distance: str) -> List[str]:
        """
        Retourne la liste des lieux disponibles pour une discipline et une distance données.
        :param discipline: La discipline de la course.
        :param distance: La distance de la course.
        :return: Liste des lieux disponibles.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT DISTINCT lieu FROM courses
                WHERE type_course = ? AND distance = ?
            ''', (discipline, distance))
            return [row[0] for row in cur.fetchall()]

    def verifier_structure_table(self):
        """Affiche la structure de la table 'courses'."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(courses)")
            columns = cur.fetchall()
            print("Structure de la table 'courses':")
            for column in columns:
                print(column)
    
    def afficher_courses_avec_partants(self):
        """Affiche les courses avec leur nombre de partants."""
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT date_course, partants FROM courses')
            for row in cur.fetchall():
                print(f"Course du {row[0]} : {row[1]} partants")

    def recuperer_courses(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les courses depuis la base de données.
        
        Returns:
            List[Dict]: Liste des courses, chaque course étant un dictionnaire.
        """
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM courses")
            colonnes = [description[0] for description in cur.description]
            print(f"Colonnes disponibles dans la table 'courses': {colonnes}")  # Afficher les colonnes
            courses = []
            for row in cur.fetchall():
                course = dict(zip(colonnes, row))
                print(f"Course récupérée : {course}")  # Afficher chaque course
                courses.append(course)
            return courses

    def calculer_ecarts_numeros_arrivee_avec_participation(self, courses: List[Dict[str, Any]]) -> Dict[int, Dict[str, int]]:
        """
        Calcule les écarts en utilisant la fonction d'analyse existante.
        """
        from analyse import calculer_ecarts_numeros_arrivee_avec_participation
        return calculer_ecarts_numeros_arrivee_avec_participation(courses)
    
# Point d'entrée pour tester database.py de manière isolée
#if __name__ == "__main__":
#    db = Database('courses.db')
#    db.verifier_structure_table()
