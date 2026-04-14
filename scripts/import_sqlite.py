# scripts/import_sqlite.py

import os
import sys
import django
import sqlite3
from pathlib import Path

# ==================================================
# CONFIG DJANGO
# ==================================================
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# ==================================================
# IMPORT MODELE
# ==================================================
from machines.models import Vrac

# ==================================================
# CONNEXION SQLITE
# ==================================================
sqlite_path = BASE_DIR / "db.sqlite3"
conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM machines_vrac")
columns = [col[0] for col in cursor.description]

rows = cursor.fetchall()

for row in rows:
    data = dict(zip(columns, row))

    # ✅ Mapping propre (sans id dans defaults)
    pk = data.pop("id")

    Vrac.objects.update_or_create(
        id=pk,
        defaults=data
    )

conn.close()

print("✅ Import SQLite → PostgreSQL terminé avec succès")