import unittest
from analyse import analyse_frequence_synthese

class TestAnalyse(unittest.TestCase):
    def test_analyse_frequence_synthese(self):
        # Test avec des données de synthèse
        courses = [
            {'synthese': '1e - 2e - 3e - 4e - 5e'},
            {'synthese': '2e - 3e - 4e - 5e - 6e'},
            {'synthese': '1e - 3e - 5e - 7e - 9e'}
        ]
        result = analyse_frequence_synthese(courses)
        self.assertEqual(result[1], 66.67)  # Le numéro 1 apparaît dans 2/3 courses
        self.assertEqual(result[2], 33.33)  # Le numéro 2 apparaît dans 1/3 courses

    def test_analyse_frequence_synthese_empty(self):
        # Test avec une liste de courses vide
        courses = []
        result = analyse_frequence_synthese(courses)
        self.assertEqual(result, {})

if __name__ == "__main__":
    unittest.main()