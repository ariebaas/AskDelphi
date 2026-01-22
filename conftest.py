"""Pytest configuration file voor path setup.

Dit bestand zorgt ervoor dat de src directory correct in de Python path
wordt opgenomen, zodat imports werken ongeacht waar pytest wordt uitgevoerd.
"""

import sys
from pathlib import Path

# Voeg project root toe aan Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
