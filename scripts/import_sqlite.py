# scripts/import_sqlite.py

import os
import django
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from machines.models import Vrac  # adapte aux modèles voulus

conn = sqlite3.connect("db.sqlite3")
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

print("✅ Import terminé")

conn.close()