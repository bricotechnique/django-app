import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.utils import timezone

from machines.models import ReglageEKO, Godet



# ==========================================================
# UTILS
# ==========================================================
def clean(v):
    if v is None:
        return ""
    return str(v).strip()


def normalize_of(v):
    v = clean(v)
    if not v:
        return None
    return (
        v.upper()
        .replace(" ", "")
        .replace("\u00A0", "")
        .strip()
    )



def to_date(value):
    value = str(value).strip() if value else ""

    if not value:
        return None

    for fmt in ("%Y/%m/%d", "%y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass

    return None



def to_float(v):
    v = clean(v)
    if v == "" or v.lower() in ["nc", "n/c"]:
        return None
    try:
        return float(v.replace(",", "."))
    except Exception:
        return None


def suffix(n):
    """0 -> '', 1 -> A, 2 -> B, 3 -> C ..."""
    if n == 0:
        return ""
    return chr(ord("A") + n - 1)


def get_godet(v):
    v = clean(v)
    if not v:
        return None
    godet, _ = Godet.objects.get_or_create(valeur=v)
    return godet


# ==========================================================
# COMMAND
# ==========================================================
class Command(BaseCommand):
    help = "Import CSV COMPLET avec OF uniques (A,B,C) et Godet FK"

    def handle(self, *args, **options):

        project_root = Path(__file__).resolve().parents[3]
        csv_path = project_root / "data" / "Fiche_de_reglage_PKB.csv"

        self.stdout.write(f"📄 Import depuis : {csv_path}")

        reader = csv.DictReader(
            open(csv_path, encoding="utf-8-sig"),
            delimiter=","
        )

        of_counter = defaultdict(int)
        created = 0

        for row in reader:

            # ==================================================
            # OF UNIQUE
            # ==================================================
            raw_of = normalize_of(row.get("numerosOf"))

            if raw_of is None:
                numeros_of = None
            else:
                idx = of_counter[raw_of]
                numeros_of = f"{raw_of}{suffix(idx)}"
                of_counter[raw_of] += 1

            # ==================================================
            # CREATION DU REGLAGE
            # ==================================================
            ReglageEKO.objects.create(

                # --- IDENTIFICATION ---
                ref=clean(row.get("Titre")),
                nom_produit=clean(row.get("Nom")),
                numeros_of=numeros_of,
                numeros_lot=clean(row.get("numerosLot")),

                of_precedent=None,
                of_lavage=None,

                date_reglage=to_date(row.get("Date")),
                regleur=clean(row.get("Régleur")),
                observation=clean(row.get("Observation")),

                # --- REMPLISSAGE ---
                moussant=clean(row.get("Moussant")),
                ref_flacon=clean(row.get("Ref flacon")),
                programme=clean(row.get("Programme")),
                godet=get_godet(row.get("Godet")),
                volume=to_float(row.get("Volume")),
                volume_demarrage=to_float(row.get("Volume démarrage")),
                filtre=clean(row.get("Filtre")),

                # --- POMPE 1 ---
                pompe_1=clean(row.get("Pompe 1")),
                motorise_1=clean(row.get("Motorisé 1")),
                valeur_1=to_float(row.get("valeur 1")),
                bute_bec_1=clean(row.get("Bute bec 1")),
                tube_bec_1=clean(row.get("tube bec 1")),
                centerur_1=clean(row.get("Centreur 1")),

                # --- POMPE 2 ---
                pompe_2=clean(row.get("Pompe 2")),
                motorise_2=clean(row.get("motorisé 2")),
                valeur_2=to_float(row.get("valeur 2")),
                bute_bec_2=clean(row.get("bute bec 2")),
                tube_bec_2=clean(row.get("tube bec 2")),
                centerur_2=clean(row.get("Centreur 2")),

                # --- POMPE 3 ---
                pompe_3=clean(row.get("Pompe 3")),
                motorise_3=clean(row.get("motorisé 3")),
                valeur_3=to_float(row.get("valeur 3")),
                bute_bec_3=clean(row.get("bute bec 3")),
                tube_bec_3=clean(row.get("tube bec 3")),
                centerur_3=clean(row.get("Centreur 3")),

                # --- POMPE 4 ---
                pompe_4=clean(row.get("Pompe 4")),
                valeur_4=to_float(row.get("valeur 4")),
                bute_bec_4=clean(row.get("bute bec 4")),
                tube_bec_4=clean(row.get("tube bec 4")),
                centerur_4=clean(row.get("Centreur 4")),

                # --- BEC / CONTROLES ---
                type_bec=clean(row.get("Type de bec")),
                h_machine=to_float(row.get("H machine")),
                ctrl_jus_h=clean(row.get("ctrl jus H")),
                ctrl_jus_prof=clean(row.get("ctrl jus prof")),
                ctrl_ultra=clean(row.get("ctrl ultra")),

                # --- MARTEAU / VISSEUSE ---
                h_compo_1=to_float(row.get("H compo 1")),
                presence_marteau=clean(row.get("Prés_Marteau")),
                h_marteau=to_float(row.get("H marteau")),

                embout=clean(row.get("Embout")),
                h_compo_2=to_float(row.get("H compo 2")),
                presence_visseuse=clean(row.get("Prés_Visseuse")),
                couple_vis=to_float(row.get("couple vis")),
                butee_vis=to_float(row.get("buté vis")),
                pince_vis=clean(row.get("pince vis")),

                h_pince_ext=to_float(row.get("H pince ext")),
                type_pince_ext=clean(row.get("Type pince ext")),
                h_pince_int=to_float(row.get("H pince int")),
                type_pince_int=clean(row.get("Type pince int")),

                # --- DIVERS ---
                cadence=to_float(row.get("cadence")),
                visseuse=clean(row.get("visseuse")),
                h_finale=to_float(row.get("H finale")),
                convoyeur=clean(row.get("convoyeur")),
                cames_bec_on=clean(row.get("cames bec on")),
                cames_bec_off=clean(row.get("cames bec off")),

                # --- CUEILLEUR ---
                presence_cueilleur=clean(row.get("presence_Ceuilleur")),
                cueilleur=clean(row.get("Cueilleur")),
                cueilleur_1=clean(row.get("Cueilleur 1 ")),
                cueilleur_2=clean(row.get("Cueilleur 2")),
                cueilleur_3=clean(row.get("Cueilleur 3")),
                hauteur_rail=to_float(row.get("Hauteur rail")),

                # --- ETIQUETAGE ---
                etiquette=clean(row.get("Etiquette")),
                consigne_etiquette=clean(row.get("Consigne Etiquette")),
                etiqueteuse=clean(row.get("Etiqueteuse")),

                # --- VRAC ---
                vrac=clean(row.get("vrac")),
                vrac_type=clean(row.get("vrac: type vrac")),
                vrac_pompe=clean(row.get("vrac: Pompe")),
                vrac_etuve=clean(row.get("vrac: Etuve")),
                vrac_temperature=clean(row.get("vrac: T°C ambiante")),
                vrac_rincage_eko=clean(row.get("vrac: Rincage Eko")),
                vrac_circuit_ferme_microbio=clean(row.get("vrac: Circuit Fermé Microbio")),
                vrac_commentaire=clean(row.get("vrac: Commentaire")),
                vrac_labo_validation=clean(row.get("vrac: Labo validation")),
                vrac_microbio_validation=clean(row.get("vrac: Microbio validation")),
            )

            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Import terminé — {created} réglages créés, OF uniques garantis"
        ))