#utils.py
from datetime import datetime
from typing import Optional

def valider_date(date_str: str) -> Optional[datetime]:
    """Valide une date au format YYYY-MM-DD ou YYYY."""
    try:
        if len(date_str) == 4:  # Année seulement
            return datetime.strptime(date_str, '%Y')
        else:
            return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None