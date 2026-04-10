import csv
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from machines.models import ReglageEKO


# -------------------------------------------------
#  Nettoyage de base
# -------------------------------------------------
def clean(v):
    if v is None:
        return ""
    return str(v).strip()


# -------------------------------------------------
#  Normalisation des OF (OBLIGATOIRE)
# -------------------------------------------------
def normalize_of(v):
    v = clean(v)
    if not v:
        return ""
    return v.upper().replace(" ", "").replace("\u00A0", "").strip()


# -------------------------------------------------
#  Conversion des dates du CSV (AA/MM/JJ)
# -------------------------------------------------
def to_date(value):
    value = clean(value)
    if not value:
        return None

    try:
        # Format AA/MM/JJ
        a, m, j = value.split("/")
        year = 2000 + int(a)
        month = int(m)
        day = int(j)
        return timezone.make_aware(datetime(year, month, day))
    except:
        return None


# -------------------------------------------------
#  Conversion des nombres (ex: "12,5")
# -------------------------------------------------
def to_float(v):
    v = clean(v)
    if v == "" or v.lower() in ["nc", "n/c"]:
        return None
    try:
        return float(v.replace(",", "."))
    except:
        return None


# -------------------------------------------------
#  Commande Django
# -------------------------------------------------
class Command(BaseCommand):
    help = "Import EKO en 2 passes (création puis liaisons OF)"

    def handle(self, *args, **options):

        project_root = Path(__file__).resolve().parents[3]
        csv_path = project_root / "data" / "Fiche_de_reglage_PKB.csv"

        self.stdout.write(f"📄 Lecture du fichier : {csv_path}")

        # -------------------------------------------------
        # PASSE 1 : création des réglages (sans FK)
        # -------------------------------------------------
        reader = csv.DictReader(open(csv_path, encoding="utf-8-sig"))
        count = 0

        for row in reader:

            current_of = normalize_of(row["numerosOf"])

            ReglageEKO.objects.create(
                ref=clean(row["Titre"]),
                nom_produit=clean(row["Nom"]),
                numeros_lot=clean(row["numerosLot"]),
                numeros_of=current_of,

                # ✅ PAS DE FK ICI !
                # ✅ On importe seulement les champs simples

                of_precedent=None,
                of_lavage=None,

                # ==== Exemple de quelques champs ====
                date_reglage=to_date(row["Date"]),
                regleur=clean(row["Régleur"]),
                moussant=clean(row["Moussant"]),
                ref_flacon=clean(row["Ref flacon"]),
                observation=clean(row["Observation"]),
                programme=clean(row["Programme"]),
                godet=clean(row["Godet"]),
                volume=to_float(row["Volume"]),
                volume_demarrage=to_float(row["Volume démarrage"]),
                filtre=clean(row["Filtre"]),

                pompe_1=clean(row["Pompe 1"]),
                motorise_1=clean(row["Motorisé 1"]),
                valeur_1=to_float(row["valeur 1"]),
                bute_bec_1=clean(row["Bute bec 1"]),
                tube_bec_1=clean(row["tube bec 1"]),
                centerur_1=clean(row["Centreur 1"]),

                pompe_2=clean(row["Pompe 2"]),
                motorise_2=clean(row["motorisé 2"]),
                valeur_2=to_float(row["valeur 2"]),
                bute_bec_2=clean(row["bute bec 2"]),
                tube_bec_2=clean(row["tube bec 2"]),
                centerur_2=clean(row["Centreur 2"]),

                pompe_3=clean(row["Pompe 3"]),
                motorise_3=clean(row["motorisé 3"]),
                valeur_3=to_float(row["valeur 3"]),
                bute_bec_3=clean(row["bute bec 3"]),
                tube_bec_3=clean(row["tube bec 3"]),
                centerur_3=clean(row["Centreur 3"]),

                pompe_4=clean(row["Pompe 4"]),
                valeur_4=to_float(row["valeur 4"]),
                bute_bec_4=clean(row["bute bec 4"]),
                tube_bec_4=clean(row["tube bec 4"]),
                centerur_4=clean(row["Centreur 4"]),

                type_bec=clean(row["Type de bec"]),
                h_machine=to_float(row["H machine"]),
                ctrl_jus_h=clean(row["ctrl jus H"]),
                ctrl_jus_prof=clean(row["ctrl jus prof"]),
                ctrl_ultra=clean(row["ctrl ultra"]),

                h_compo_1=to_float(row["H compo 1"]),
                presence_marteau=clean(row["Prés_Marteau"]),
                h_marteau=to_float(row["H marteau"]),

                embout=clean(row["Embout"]),
                h_compo_2=to_float(row["H compo 2"]),

                presence_visseuse=clean(row["Prés_Visseuse"]),
                couple_vis=to_float(row["couple vis"]),
                butee_vis=to_float(row["buté vis"]),

                pince_vis=clean(row["pince vis"]),
                h_pince_ext=to_float(row["H pince ext"]),
                type_pince_ext=clean(row["Type pince ext"]),
                h_pince_int=to_float(row["H pince int"]),
                type_pince_int=clean(row["Type pince int"]),

                cadence=to_float(row["cadence"]),
                visseuse=clean(row["visseuse"]),
                h_finale=to_float(row["H finale"]),
                convoyeur=clean(row["convoyeur"]),

                cames_bec_on=clean(row["cames bec on"]),
                cames_bec_off=clean(row["cames bec off"]),

                presence_cueilleur=clean(row["presence_Ceuilleur"]),
                cueilleur=clean(row["Cueilleur"]),
                cueilleur_1=clean(row["Cueilleur 1 "]),
                cueilleur_2=clean(row["Cueilleur 2"]),
                cueilleur_3=clean(row["Cueilleur 3"]),

                hauteur_rail=to_float(row["Hauteur rail"]),

                etiquette=clean(row["Etiquette"]),
                consigne_etiquette=clean(row["Consigne Etiquette"]),
                etiqueteuse=clean(row["Etiqueteuse"]),

                vrac=clean(row["vrac"]),
                vrac_type=clean(row["vrac: type vrac"]),
                vrac_pompe=clean(row["vrac: Pompe"]),
                vrac_etuve=clean(row["vrac: Etuve"]),
                vrac_temperature=clean(row["vrac: T°C ambiante"]),
                vrac_rincage_eko=clean(row["vrac: Rincage Eko"]),
                vrac_circuit_ferme_microbio=clean(row["vrac: Circuit Fermé Microbio"]),
                vrac_commentaire=clean(row["vrac: Commentaire"]),
                vrac_labo_validation=clean(row["vrac: Labo validation"]),
                vrac_microbio_validation=clean(row["vrac: Microbio validation"]),
            )

            count += 1


        # -------------------------------------------------
        # PASSE 2 : création des liens OF (FK)
        # -------------------------------------------------
        reader = csv.DictReader(open(csv_path, encoding="utf-8-sig"))

        for row in reader:

            current_of = normalize_of(row["numerosOf"])
            reg = ReglageEKreg = ReglageEKO.objects.filter(numeros_of=current_of).first()
            if not reg:
             continue  # sécurité si jamais une ligne n’existe pas

            # OF précédent
            prec_of = normalize_of(row["Of precedent"])
            if prec_of:
                reg.of_precedent = ReglageEKO.objects.filter(numeros_of=prec_of).first()

            # OF lavage
            lav_of = normalize_of(row["Of Lavage"])
            if lav_of:
                reg.of_lavage = ReglageEKO.objects.filter(numeros_of=lav_of).first()

            reg.save()


        # -------------------------------------------------
        # FIN
        # -------------------------------------------------
        self.stdout.write(self.style.SUCCESS(
            f"✅ Import terminé ! {count} lignes créées + liens OF résolus"
        ))
