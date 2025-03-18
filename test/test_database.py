import unittest
import sqlite3
from database import Database

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Créer une base de données temporaire pour les tests
        self.db_path = ":memory:"
        self.db = Database(self.db_path)

    def test_save_course(self):
        # Test de sauvegarde d'une course
        donnees = {
            'date': '2025-01-18',
            'lieu': 'Vincennes',
            'type': 'Attelé',
            'distance': '2700m',
            'arrivee': '3 - 8 - 12 - 4 - 9',
            'synthese': '1e - 3e - 2e - 4e - 11e'
        }
        result = self.db.save_course("18-01-25.txt", donnees)
        self.assertTrue(result)

        # Vérifier que la course a bien été insérée
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM courses WHERE nom_fichier = ?', ("18-01-25.txt",))
            course = cur.fetchone()
            self.assertIsNotNone(course)

    def test_save_course_duplicate(self):
        # Test de sauvegarde d'une course déjà existante
        donnees = {
            'date': '2025-01-18',
            'lieu': 'Vincennes',
            'type': 'Attelé',
            'distance': '2700m',
            'arrivee': '3 - 8 - 12 - 4 - 9',
            'synthese': '1e - 3e - 2e - 4e - 11e'
        }
        self.db.save_course("18-01-25.txt", donnees)
        result = self.db.save_course("18-01-25.txt", donnees)  # Tentative de doublon
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()