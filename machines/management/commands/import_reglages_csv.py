import csv
from datetime import datetime
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from machines.models import (
    ReglageEKO,
    Godet, Bec, Centreur,
    Bute, Pince, PinceF, Vrac,
)



# =========================
# Helpers
# =========================


def clean(v):
    return "" if v is None else str(v).strip()




def is_trueish(v):
    s = clean(v).lower()
    return s in ("true", "vrai", "oui", "1", "on", "checked", "x")

def is_meaningful_text(v):
    """
    True si la cellule contient un "texte utile" (nom/type) => on considère présence.
    False si vide ou valeurs 'vides' typiques.
    """
    s = clean(v).lower()
    return s not in ("", "nc", "n/c", "0", "non", "false", "faux", "-", "_")




def pick(row, *keys):
    """Retourne row[k] pour le premier k existant (utile pour accents/casse)."""
    for k in keys:
        if k in row:
            return row.get(k)
    return None

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
    return v in ("true", "vrai", "oui", "1", "on", "checked")

def get_fk(model, v):
    """Crée/réutilise un objet de table de choix basé sur model(valeur=...)."""
    v = clean(v)
    if not v:
        return None
    obj, _ = model.objects.get_or_create(valeur=v)
    return obj

def suffix(idx: int) -> str:
    """0 -> '', 1 -> 'A', 2 -> 'B', ..."""
    if idx <= 0:
        return ""
    return chr(ord("A") + idx - 1)


class Command(BaseCommand):
    help = "Import CSV complet (sections gabarit + champs choix FK)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--purge",
            action="store_true",
            help="Vide ReglageEKO + tables choix avant import (recommandé si tu réimportes souvent).",
        )
        parser.add_argument(
            "--path",
            type=str,
            default="data/Fiche_de_reglage_PKB.csv",
            help="Chemin du CSV.",
        )

    def handle(self, *args, **options):
        path = options["path"]
        self.stdout.write(f"📄 Import depuis : {path}")
        seen_numeros = defaultdict(int)

        if options["purge"]:
            self.stdout.write("🧹 Purge (ReglageEKO, Godet, Bec, Centreur, Bute, Pince, PinceF)…")
            ReglageEKO.objects.all().delete()
            Godet.objects.all().delete()
            Bec.objects.all().delete()
            Centreur.objects.all().delete()
            Bute.objects.all().delete()
            Pince.objects.all().delete()
            PinceF.objects.all().delete()

        seen_of = defaultdict(int)
        first_by_raw_of = {}
        pending_links = []  # (reglage_id, of_prec_raw, of_lav_raw)
        created = 0
        empty_of = 0

        with transaction.atomic():
            with open(path, newline="", encoding="utf-8-sig") as f:
                # CSV séparé par virgules (vu via FIELDNAMES)
                reader = csv.DictReader(f, delimiter=",", quotechar='"')

                for row in reader:
                    # -------------------------
                    # OF (numerosOf) -> suffixes A/B/C... si doublons
                    # -------------------------
                    raw_of = clean(row.get("numerosOf"))
                    if raw_of:
                        seen_of[raw_of] += 1
                        idx = seen_of[raw_of] - 1
                        unique_of = raw_of + suffix(idx)
                    else:
                        # OF vide -> NULL (tu l'as demandé)
                        empty_of += 1
                        unique_of = None

                    reglage = ReglageEKO()
                    reglage.numeros_of = unique_of

                    # -------------------------
                    # Infos principales
                    # -------------------------
                    reglage.ref = clean(row.get("Titre"))
                    reglage.nom_produit = clean(row.get("Nom"))
                    reglage.numeros_lot = clean(row.get("numerosLot"))
                    reglage.date_reglage = to_date(row.get("Date"))
                    reglage.regleur = clean(pick(row, "Régleur", "Regleur"))
                    reglage.observation = clean(row.get("Observation"))

                    # -------------------------
                    # Remplissage
                    # -------------------------
                    reglage.moussant = clean(row.get("Moussant"))
                    reglage.ref_flacon = clean(row.get("Ref flacon"))
                    reglage.programme = clean(row.get("Programme"))

                    # Godet (FK choix)
                    reglage.godet = get_fk(Godet, row.get("Godet"))

                    # Volume(s)
                    reglage.volume = to_float(row.get("Volume"))
                    reglage.volume_demarrage = to_float(row.get("Volume démarrage"))

                    # Filtre (dans ton modèle c'est CharField actuellement) [1](https://bricotechnique-my.sharepoint.com/personal/tristanhudreaux_bricotechnique_onmicrosoft_com/Documents/Fichiers%20Microsoft%20Copilot%20Chat/models.py)
                    reglage.filtre = clean(row.get("Filtre"))

                    # -------------------------
                    # Pompes 1..4 (choix + valeurs)
                    # -------------------------
                    reglage.pompe_1 = clean(row.get("Pompe 1")) or None
                    reglage.pompe_2 = clean(row.get("Pompe 2")) or None
                    reglage.pompe_3 = clean(row.get("Pompe 3")) or None
                    reglage.pompe_4 = clean(row.get("Pompe 4")) or None

                    reglage.valeur_1 = to_float(row.get("valeur 1"))
                    reglage.valeur_2 = to_float(row.get("valeur 2"))
                    reglage.valeur_3 = to_float(row.get("valeur 3"))
                    reglage.valeur_4 = to_float(row.get("valeur 4"))

                    # Bute bec (texte)
                    reglage.bute_bec_1 = clean(row.get("Bute bec 1")) or None
                    reglage.bute_bec_2 = clean(row.get("bute bec 2")) or None
                    reglage.bute_bec_3 = clean(row.get("bute bec 3")) or None
                    reglage.bute_bec_4 = clean(row.get("bute bec 4")) or None

                    # Tube bec (FK choix Bec)
                    reglage.tube_bec_1 = get_fk(Bec, row.get("tube bec 1"))
                    reglage.tube_bec_2 = get_fk(Bec, row.get("tube bec 2"))
                    reglage.tube_bec_3 = get_fk(Bec, row.get("tube bec 3"))
                    reglage.tube_bec_4 = get_fk(Bec, row.get("tube bec 4"))

                    # Centreur (FK choix) 
                    reglage.centerur_1 = get_fk(Centreur, row.get("Centreur 1"))
                    reglage.centerur_2 = get_fk(Centreur, row.get("Centreur 2"))
                    reglage.centerur_3 = get_fk(Centreur, row.get("Centreur 3"))
                    reglage.centerur_4 = get_fk(Centreur, row.get("Centreur 4"))

                    # Motorisés (dans ton modèle c'est CharField) [1](https://bricotechnique-my.sharepoint.com/personal/tristanhudreaux_bricotechnique_onmicrosoft_com/Documents/Fichiers%20Microsoft%20Copilot%20Chat/models.py)
                    reglage.motorise_1 = clean(row.get("Motorisé 1"))
                    reglage.motorise_2 = clean(row.get("motorisé 2"))
                    reglage.motorise_3 = clean(row.get("motorisé 3"))

                    # -------------------------
                    # Hauteurs / capteurs / postes
                    # -------------------------
                    reglage.type_bec = clean(row.get("Type de bec"))
                    reglage.h_machine = to_float(row.get("H machine"))
                    reglage.ctrl_jus_h = clean(row.get("ctrl jus H"))
                    reglage.ctrl_jus_prof = clean(row.get("ctrl jus prof"))
                    reglage.ctrl_ultra = clean(row.get("ctrl ultra"))

                    reglage.h_compo_1 = to_float(row.get("H compo 1"))
                    reglage.presence_marteau = clean(row.get("Prés_Marteau"))
                    reglage.h_marteau = to_float(row.get("H marteau"))
                    reglage.embout = clean(row.get("Embout"))
                    reglage.h_compo_2 = to_float(row.get("H compo 2"))

                    # Poste 2 / visseuse / pinces
                    reglage.presence_visseuse = clean(row.get("Prés_Visseuse"))
                    reglage.couple_vis = to_float(row.get("couple vis"))

                    # Butée vis : tu veux en FK choix (Option 1) → on crée/réutilise Bute(valeur=...) [1](https://bricotechnique-my.sharepoint.com/personal/tristanhudreaux_bricotechnique_onmicrosoft_com/Documents/Fichiers%20Microsoft%20Copilot%20Chat/models.py)
                    # Ton CSV a une colonne "buté vis"
                    reglage.butee_vis = get_fk(Bute, row.get("buté vis"))

                    # Pince vis : CSV contient "pince vis" → FK Pince [1](https://bricotechnique-my.sharepoint.com/personal/tristanhudreaux_bricotechnique_onmicrosoft_com/Documents/Fichiers%20Microsoft%20Copilot%20Chat/models.py)
                    reglage.pince_vis = get_fk(Pince, row.get("pince vis"))

                    # Pince flacon : pas toujours présent dans ton CSV -> on tente plusieurs noms
                    reglage.pince_f = get_fk(PinceF, row.get("Type pince ext"))
                    reglage.h_pince_ext = to_float(row.get("H pince ext"))
                    reglage.h_pince_int = to_float(row.get("H pince int"))
                

                    reglage.cadence = to_float(row.get("cadence"))
                    reglage.visseuse = clean(row.get("visseuse"))
                    reglage.h_finale = to_float(row.get("H finale"))
                    reglage.convoyeur = clean(row.get("convoyeur"))
                    reglage.cames_bec_on = clean(row.get("cames bec on"))
                    reglage.cames_bec_off = clean(row.get("cames bec off"))

                    # -------------------------
                    # Cueilleur
                    # -------------------------
                    
                    presence_val = row.get("presence_Ceuilleur")  # nom exact de ta colonne CSV
                    cueilleur_val = row.get("Cueilleur")          # peut être bool OU texte

                    cueilleur_bool = (
                        is_trueish(presence_val)
                        or is_trueish(cueilleur_val)
                        or is_meaningful_text(cueilleur_val)
                    )

                    # Comme ton champ est un CharField => on stocke une string
                    reglage.cueilleur = "True" if cueilleur_bool else "False"

                    reglage.cueilleur_1 = clean(pick(row, "Cueilleur 1", "Cueilleur 1 "))
                    reglage.cueilleur_2 = clean(row.get("Cueilleur 2"))
                    reglage.cueilleur_3 = clean(row.get("Cueilleur 3"))
                    reglage.hauteur_rail = to_float(row.get("Hauteur rail"))

                    # -------------------------
                    # Etiquetage
                    # -------------------------
                    reglage.etiquette = clean(row.get("Etiquette"))
                    reglage.consigne_etiquette = clean(row.get("Consigne Etiquette"))
                    reglage.etiqueteuse = clean(row.get("Etiqueteuse"))

                    
                   # =========================
                    # VRAC : on n'importe que la référence + lien FK si la fiche existe
                    # =========================
                    ref_vrac = clean(row.get("vrac"))  # colonne clé dans ton CSV

                    # 1) garder la référence dans ReglageEKO.vrac (champ texte existant)
                    reglage.vrac = ref_vrac

                    # 2) lier à la table Vrac si le champ FK existe dans ton modèle
                    if hasattr(reglage, "vrac_ref_id"):
                        reglage.vrac_ref = Vrac.objects.filter(ref=ref_vrac).first() if ref_vrac else None

                    # 3) optionnel : vider les champs VRAC "legacy" du réglage pour ne pas stocker de doublons
                    # (utile si tu ne veux plus du tout ces colonnes dans ReglageEKO)
                    for f in (
                        "vrac_type", "vrac_pompe", "vrac_etuve", "vrac_temperature",
                        "vrac_rincage_eko", "vrac_circuit_ferme_microbio", "vrac_commentaire",
                        "vrac_labo_validation", "vrac_microbio_validation",
                    ):
                        if hasattr(reglage, f):
                            setattr(reglage, f, "")
                    # -------------------------
                    # Liens OF précédent / lavage (2e passe)
                    # -------------------------
                    of_prec_raw = clean(pick(row, "Of precedent", "OF precedent", "OF Precedent"))
                    of_lav_raw = clean(pick(row, "Of Lavage", "OF lavage", "OF Lavage"))
                    base_num = clean(numeros_of)
                    idx = seen_numeros[base_num]

                    num_final = f"{base_num}{suffix(idx)}"

                    while ReglageEKO.objects.filter(numeros_of=num_final).exists():
                        idx += 1
                        num_final = f"{base_num}{suffix(idx)}"

                    seen_numeros[base_num] = idx + 1
                    reglage.numeros_of = num_final

                    reglage.save()
                    created += 1

                    pending_links.append((reglage.id, of_prec_raw, of_lav_raw))

                    # mémorise le 1er record d'une série (utile si l'OF référence une version sans suffixe)
                    if raw_of and raw_of not in first_by_raw_of:
                        first_by_raw_of[raw_of] = reglage

            # 2e passe : résoudre of_precedent / of_lavage
            for reg_id, of_prec_raw, of_lav_raw in pending_links:
                r = ReglageEKO.objects.filter(id=reg_id).first()
                if not r:
                    continue

                if of_prec_raw:
                    target = (ReglageEKO.objects.filter(numeros_of=of_prec_raw).first()
                              or first_by_raw_of.get(of_prec_raw))
                    r.of_precedent = target

                if of_lav_raw:
                    target = (ReglageEKO.objects.filter(numeros_of=of_lav_raw).first()
                              or first_by_raw_of.get(of_lav_raw))
                    r.of_lavage = target

                r.save(update_fields=["of_precedent", "of_lavage"])

        self.stdout.write(self.style.SUCCESS(
            f"✅ Import terminé : {created} lignes créées | OF vides importés (NULL) : {empty_of}"
        ))
