# scripts/import_sqlite.py

import os
import sys
import django
import sqlite3
from pathlib import Path

# --------------------------------------------------
# AJOUT DU ROOT DU PROJET AU PYTHONPATH (IMPORTANT)
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# --------------------------------------------------
# CONFIG DJANGO
# --------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# --------------------------------------------------
# IMPORT DES MODÈLES
# --------------------------------------------------
from machines.models import Vrac  # adapte si besoin

# --------------------------------------------------
# CONNEXION SQLITE
# --------------------------------------------------
sqlite_db_path = BASE_DIR / "db.sqlite3"

conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, nom, description FROM machines_vrac")
rows = cursor.fetchall()

for row in rows:
    Vrac.objects.update_or_create(
        id=row[0],
        defaults={
            "nom": row[1],
            "description": row[2],
        }
    )

conn.close()

print("✅ Import SQLite → PostgreSQL terminé avec succès")