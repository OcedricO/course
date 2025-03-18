# test_file_parser
import unittest
import sys
import os

# Ajouter le chemin du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from file_parser.file_parser import parse_file  # Import correct

class TestFileParser(unittest.TestCase):
    def test_parse_file_valid(self):
        # Test avec un fichier valide
        file_path = "18-01-25.txt"
        result = parse_file(file_path)
        self.assertIsNotNone(result)
        self.assertEqual(result['lieu'], "Vincennes")
        self.assertEqual(result['type'], "Attelé")
        self.assertEqual(result['distance'], "2700m")
        self.assertEqual(result['arrivee'], "3 - 8 - 12 - 4 - 9")
        self.assertEqual(result['synthese'], "1e - 3e - 2e - 4e - 11e")

    def test_parse_file_invalid(self):
        # Test avec un fichier invalide (données manquantes)
        file_path = "invalid_file.txt"
        result = parse_file(file_path)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()