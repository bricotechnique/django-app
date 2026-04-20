import csv
from django.core.management.base import BaseCommand
from machines.models import Vrac, ReglageEKO

def clean(v):
    return "" if v is None else str(v).strip()

def parse_boolish(v):
    s = clean(v).lower()
    return s in ("true", "vrai", "oui", "1", "on", "checked", "x")

class Command(BaseCommand):
    help = "Import CSV VRAC dans la table Vrac (et optionnellement lie ReglageEKO)"

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, default="data/Listing_vrac.csv", help="Chemin du CSV VRAC")
        parser.add_argument("--link", action="store_true", help="Lie aussi ReglageEKO.vrac_ref si champ existant")
        parser.add_argument("--purge", action="store_true", help="Vide la table Vrac avant import")

    def handle(self, *args, **options):
        path = options["path"]

        if options["purge"]:
            self.stdout.write("🧹 Purge table Vrac...")
            Vrac.objects.all().delete()

        self.stdout.write(f"📄 Import VRAC depuis : {path}")

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=",", quotechar='"')

            self.stdout.write(f"✅ Colonnes détectées: {reader.fieldnames}")

            created = 0
            updated = 0

            for row in reader:
                # ⚠️ ADAPTER ICI la colonne clé (ref VRAC)
                
                            # clé VRAC
                ref = clean(row.get("code"))
                if not ref:
                    continue

                defaults = {
                    "Nom_vrac": clean(row.get("Nom vrac")),
                    "vrac_type": clean(row.get("type vrac")),
                    "pompe": clean(row.get("Pompe")),
                    "etuve": clean(row.get("Etuve")),
                    "temperature": clean(row.get("T°C ambiante")),
                    "circuit_ferme_microbio": "True" if parse_boolish(row.get("Circuit Fermé Microbio")) else "False",
                    "commentaire": clean(row.get("Commentaire")),
                    "labo_validation": clean(row.get("Labo validation")),
                    "microbio_validation": clean(row.get("Microbio validation")),
                    "marque": clean(row.get("marque")),
                }


                obj, was_created = Vrac.objects.update_or_create(
                    ref=ref,
                    defaults=defaults
                )

                if was_created:
                    created += 1
                else:
                    updated += 1

                # Optionnel: lier les réglages au VRAC
                if options["link"]:
                    # Ici on suppose que ReglageEKO.vrac contient la ref VRAC.
                    # Si tu as vrac_ref FK dans ReglageEKO, on peut lier :
                    ReglageEKO.objects.filter(vrac=ref).update(vrac_ref=obj)

        self.stdout.write(self.style.SUCCESS(f"✅ Import terminé. Créés={created}, mis à jour={updated}"))