import csv
from datetime import datetime
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from machines.models import ReglageEKO, Godet, Bec, Centreur


# =========================
# Utils
# =========================
def clean(v):
    if v is None:
        return ""
    return str(v).strip()


def to_float(v):
    v = clean(v)
    if v == "" or v.lower() in ("nc", "n/c"):
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def to_date(v):
    v = clean(v)
    if not v:
        return None
    for fmt in ("%Y/%m/%d", "%y/%m/%d"):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    return None


def parse_bool(v):
    v = clean(v).lower()
    if v in ("true", "vrai", "oui", "1", "on", "checked"):
        return True
    if v in ("false", "faux", "non", "0"):
        return False
    # par défaut -> False (comme tu voulais)
    return False


def get_godet(v):
    v = clean(v)
    if not v:
        return None
    obj, _ = Godet.objects.get_or_create(valeur=v)
    return obj


def get_bec(v):
    v = clean(v)
    if not v:
        return None
    obj, _ = Bec.objects.get_or_create(valeur=v)
    return obj


def get_centreur(v):
    v = clean(v)
    if not v:
        return None
    obj, _ = Centreur.objects.get_or_create(valeur=v)
    return obj


def suffix(idx: int) -> str:
    """
    idx=0 -> ''
    idx=1 -> 'A'
    idx=2 -> 'B'
    ...
    """
    if idx <= 0:
        return ""
    return chr(ord("A") + idx - 1)


# =========================
# Command
# =========================
class Command(BaseCommand):
    help = "Import CSV complet (Godet/Bec/Centreur) + OF uniques A/B/C + OF vides = NULL + liens OF"

    def add_arguments(self, parser):
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Vide ReglageEKO/Godet/Bec/Centreur avant import (recommandé)",
        )

    def handle(self, *args, **options):
        path = "data/Fiche_de_reglage_PKB.csv"
        self.stdout.write(f"📄 Import depuis : {path}")

        if options["purge"]:
            self.stdout.write("🧹 Purge des tables (ReglageEKO, Godet, Bec, Centreur)…")
            ReglageEKO.objects.all().delete()
            Godet.objects.all().delete()
            Bec.objects.all().delete()
            Centreur.objects.all().delete()
        else:
            self.stdout.write("ℹ️ Astuce : relance avec --purge si tu veux éviter les conflits d'unicité.")

        # Compteur pour suffixes A/B/C sur numerosOf (seulement si numerosOf existe)
        seen_of = defaultdict(int)
        empty_of = 0

        # 2e passe pour résoudre OF précédent / lavage
        pending_links = []   # (reglage_id, of_prec_raw, of_lav_raw)
        first_by_raw_of = {} # raw_of -> 1er ReglageEKO créé (sans suffixe)

        created = 0

        with transaction.atomic():
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f, delimiter=",", quotechar='"')

                # Décommente si besoin pour debug
                # self.stdout.write(f"FIELDNAMES: {reader.fieldnames}")

                for row in reader:
                    # -------------------------
                    # OF : colonne = numerosOf
                    # -------------------------
                    raw_of = clean(row.get("numerosOf"))

                    if raw_of:
                        seen_of[raw_of] += 1
                        idx = seen_of[raw_of] - 1
                        unique_of = raw_of + suffix(idx)
                    else:
                        # ✅ OF vide => NULL (on n'ignore plus la ligne)
                        empty_of += 1
                        unique_of = None

                    # -------------------------
                    # Création du réglage
                    # -------------------------
                    reglage = ReglageEKO()

                    # Identité / entête
                    reglage.numeros_of = unique_of
                    reglage.ref = clean(row.get("Titre"))
                    reglage.nom_produit = clean(row.get("Nom"))
                    reglage.numeros_lot = clean(row.get("numerosLot"))
                    reglage.regleur = clean(row.get("Régleur"))
                    reglage.observation = clean(row.get("Observation"))

                    # Date / volumes
                    reglage.date_reglage = to_date(row.get("Date"))
                    reglage.volume = to_float(row.get("Volume"))
                    reglage.volume_demarrage = to_float(row.get("Volume démarrage"))

                    # Remplissage
                    reglage.moussant = clean(row.get("Moussant"))
                    reglage.ref_flacon = clean(row.get("Ref flacon"))
                    reglage.programme = clean(row.get("Programme"))
                    reglage.godet = get_godet(row.get("Godet"))
                    reglage.filtre = parse_bool(row.get("Filtre"))

                    # Pompes
                    reglage.pompe_1 = clean(row.get("Pompe 1"))
                    reglage.pompe_2 = clean(row.get("Pompe 2"))
                    reglage.pompe_3 = clean(row.get("Pompe 3"))
                    reglage.pompe_4 = clean(row.get("Pompe 4"))

                    reglage.valeur_1 = to_float(row.get("valeur 1"))
                    reglage.valeur_2 = to_float(row.get("valeur 2"))
                    reglage.valeur_3 = to_float(row.get("valeur 3"))
                    reglage.valeur_4 = to_float(row.get("valeur 4"))

                    # ✅ Becs (FK)
                    reglage.tube_bec_1 = get_bec(row.get("tube bec 1"))
                    reglage.tube_bec_2 = get_bec(row.get("tube bec 2"))
                    reglage.tube_bec_3 = get_bec(row.get("tube bec 3"))
                    reglage.tube_bec_4 = get_bec(row.get("tube bec 4"))

                    # ✅ Centreurs (FK) — colonne CSV = "Centreur 1..4"
                    reglage.centerur_1 = get_centreur(row.get("Centreur 1"))
                    reglage.centerur_2 = get_centreur(row.get("Centreur 2"))
                    reglage.centerur_3 = get_centreur(row.get("Centreur 3"))
                    reglage.centerur_4 = get_centreur(row.get("Centreur 4"))

                    # Motorisés (attention : 1 majuscule, 2/3 parfois minuscules)
                    reglage.motorise_1 = parse_bool(row.get("Motorisé 1"))
                    reglage.motorise_2 = parse_bool(row.get("motorisé 2"))
                    reglage.motorise_3 = parse_bool(row.get("motorisé 3"))
                    # pas de motorise_4

                    # Type de bec (si tu veux le garder comme texte)
                    reglage.type_bec = clean(row.get("Type de bec"))
                    reglage.h_machine = to_float(row.get("H machine"))

                    # Stocker les liens OF pour 2e passe
                    of_prec_raw = clean(row.get("Of precedent"))
                    of_lav_raw = clean(row.get("Of Lavage"))
                    pending_links.append((reglage.id, raw_of, of_prec_raw, of_lav_raw))  # raw_of utile

                    reglage.save()
                    created += 1

                    # mémoriser le premier enregistrement pour ce raw_of (sans suffixe)
                    if raw_of and raw_of not in first_by_raw_of:
                        first_by_raw_of[raw_of] = reglage

            # -------------------------
            # 2e passe : résoudre OF precedent/lavage
            # -------------------------
            for reg_id, raw_of, of_prec_raw, of_lav_raw in pending_links:
                r = ReglageEKO.objects.filter(id=reg_id).first()
                if not r:
                    continue

                if of_prec_raw:
                    # d'abord match exact, sinon "premier de la série"
                    target = (
                        ReglageEKO.objects.filter(numeros_of=of_prec_raw).first()
                        or first_by_raw_of.get(of_prec_raw)
                    )
                    r.of_precedent = target

                if of_lav_raw:
                    target = (
                        ReglageEKO.objects.filter(numeros_of=of_lav_raw).first()
                        or first_by_raw_of.get(of_lav_raw)
                    )
                    r.of_lavage = target

                r.save(update_fields=["of_precedent", "of_lavage"])

        self.stdout.write(self.style.SUCCESS(
            f"✅ Import terminé : {created} lignes créées | OF vides importés (NULL) : {empty_of}"
        ))