from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required

from machines.models import (
    ReglageEKO, Godet, Bec, Centreur, Bute, Pince, PinceF
)


# ============================================================
# Helpers
# ============================================================

def to_float(v):
    """Convertit une saisie en float ou None (vide -> None, virgule -> point)."""
    v = (v or "").strip()
    if v == "":
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def handle_fk_select(request, obj, *, field, model, new_field):
    """
    Gère un champ FK alimenté par :
    - <select name="field"> avec value = id ou "_new" ou ""
    - <input name="new_field"> pour créer un nouvel objet (model(valeur=...))

    Exemples:
      handle_fk_select(request, reglage, field="godet", model=Godet, new_field="godet_new_value")
      handle_fk_select(request, reglage, field="butee_vis", model=Bute, new_field="butee_vis_new_value")
      handle_fk_select(request, reglage, field="pince_vis", model=Pince, new_field="pince_vis_new_value")
      handle_fk_select(request, reglage, field="tube_bec_1", model=Bec, new_field="tube_bec_1_new_value")
      handle_fk_select(request, reglage, field="centerur_2", model=Centreur, new_field="centerur_2_new_value")
    """
    choice = request.POST.get(field)
    new_val = request.POST.get(new_field)

    if choice == "_new" and new_val:
        inst, _ = model.objects.get_or_create(valeur=new_val.strip())
        setattr(obj, field, inst)
        return

    if choice:
        # IMPORTANT : on assigne l'ID dans *_id pour éviter "must be an instance"
        setattr(obj, f"{field}_id", int(choice))
    else:
        setattr(obj, field, None)


def build_pompes(reglage: ReglageEKO):
    # Attention : dans ton modèle actuel, centerur_4 est un CharField (pas FK). [1](https://bricotechnique-my.sharepoint.com/personal/tristanhudreaux_bricotechnique_onmicrosoft_com/Documents/Fichiers%20Microsoft%20Copilot%20Chat/models.py)
    # On le met tel quel dans la structure. Si tu le passes en FK, ce code fonctionne aussi.
    return [
        {"num": 1, "pompe": reglage.pompe_1, "valeur": reglage.valeur_1, "bec": reglage.tube_bec_1, "centerur": reglage.centerur_1, "motorise": reglage.motorise_1},
        {"num": 2, "pompe": reglage.pompe_2, "valeur": reglage.valeur_2, "bec": reglage.tube_bec_2, "centerur": reglage.centerur_2, "motorise": reglage.motorise_2},
        {"num": 3, "pompe": reglage.pompe_3, "valeur": reglage.valeur_3, "bec": reglage.tube_bec_3, "centerur": reglage.centerur_3, "motorise": reglage.motorise_3},
        {"num": 4, "pompe": reglage.pompe_4, "valeur": reglage.valeur_4, "bec": reglage.tube_bec_4, "centerur": reglage.centerur_4, "motorise": None},
    ]


# ============================================================
# Delete
# ============================================================

@login_required
@permission_required("machines.delete_reglageeko", raise_exception=True)
def delete_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    if request.method == "POST":
        reglage.delete()
        return redirect("recherche_reglages")

    return render(request, "machines/delete_confirm.html", {"reglage": reglage})


# ============================================================
# Create
# ============================================================

@login_required
@permission_required("machines.add_reglageeko", raise_exception=True)
def create_reglage(request):
    # numeros_lot n'est pas blank dans ton modèle, on met une chaîne vide.
    reglage = ReglageEKO.objects.create(
        ref="NOUVEAU",
        numeros_of=None,
        numeros_lot="",
        nom_produit="",
    )
    return redirect("edit_reglage", reglage_id=reglage.id)


# ============================================================
# Search
# ============================================================

@login_required
def recherche_reglages(request):
    reglages = ReglageEKO.objects.all().order_by("-date_reglage")

    ref = request.GET.get("ref")
    nom = request.GET.get("nom")
    lot = request.GET.get("lot")
    of_ = request.GET.get("of")
    volume = request.GET.get("volume")

    if ref:
        reglages = reglages.filter(ref__icontains=ref)
    if nom:
        reglages = reglages.filter(nom_produit__icontains=nom)
    if lot:
        reglages = reglages.filter(numeros_lot__icontains=lot)
    if of_:
        reglages = reglages.filter(numeros_of__icontains=of_)
    if volume:
        reglages = reglages.filter(volume=volume)

    return render(request, "machines/recherche_reglages.html", {"reglages": reglages})


# ============================================================
# Detail (view mode)
# ============================================================

@login_required
def detail_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    return render(request, "machines/reglage_gabarit.html", {
        "reglage": reglage,
        "mode": "view",
        "pompes": build_pompes(reglage),

        # listes utiles même en view (si ton template les référence)
        "ofs": ReglageEKO.objects.exclude(id=reglage.id).order_by("numeros_of"),
        "godets": Godet.objects.all().order_by("valeur"),
        "becs": Bec.objects.all().order_by("valeur"),
        "centreurs": Centreur.objects.all().order_by("valeur"),
        "butes": Bute.objects.all().order_by("valeur"),
        "pinces": Pince.objects.all().order_by("valeur"),
        "pincesf": PinceF.objects.all().order_by("valeur"),
    })


# ============================================================
# Edit (edit mode)
# ============================================================

@login_required
@permission_required("machines.change_reglageeko", raise_exception=True)
def edit_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    ofs = ReglageEKO.objects.exclude(id=reglage.id).order_by("numeros_of")
    godets = Godet.objects.all().order_by("valeur")
    becs = Bec.objects.all().order_by("valeur")
    centreurs = Centreur.objects.all().order_by("valeur")
    butes = Bute.objects.all().order_by("valeur")
    pinces = Pince.objects.all().order_by("valeur")
    pincesf = PinceF.objects.all().order_by("valeur")

    if request.method == "POST":
        # -------------------------
        # Champs simples (texte / date)
        # -------------------------
        reglage.ref = request.POST.get("ref", "")
        reglage.nom_produit = request.POST.get("nom_produit", "")
        reglage.numeros_lot = request.POST.get("numeros_lot", "")
        reglage.regleur = request.POST.get("regleur", "")
        reglage.observation = request.POST.get("observation", "")
        reglage.date_reglage = request.POST.get("date_reglage") or None

        # -------------------------
        # Champs float (vide -> None)
        # -------------------------
        float_fields = [
            "volume", "volume_demarrage",
            "h_machine", "h_compo_1", "h_marteau", "h_compo_2",
            "couple_vis", "h_pince_ext", "h_pince_int",
            "cadence", "h_finale",
            "hauteur_rail",
            # pompes valeurs
            "valeur_1", "valeur_2", "valeur_3", "valeur_4",
        ]
        for f in float_fields:
            if hasattr(reglage, f):
                setattr(reglage, f, to_float(request.POST.get(f)))

        # -------------------------
        # Champs texte divers
        # -------------------------
        text_fields = [
            "moussant", "ref_flacon", "programme", "filtre",
            "type_bec", "ctrl_jus_h", "ctrl_jus_prof", "ctrl_ultra",
            "presence_marteau", "embout",
            "presence_visseuse", "visseuse",
            "type_pince_ext", "type_pince_int",
            "convoyeur", "cames_bec_on", "cames_bec_off",
            "presence_cueilleur", "cueilleur", "cueilleur_1", "cueilleur_2", "cueilleur_3",
            "etiquette", "consigne_etiquette", "etiqueteuse",
            "vrac", "vrac_type", "vrac_pompe", "vrac_etuve", "vrac_temperature",
            "vrac_rincage_eko", "vrac_circuit_ferme_microbio",
            "vrac_commentaire", "vrac_labo_validation", "vrac_microbio_validation",
        ]
        for f in text_fields:
            if hasattr(reglage, f):
                setattr(reglage, f, request.POST.get(f, ""))

        # -------------------------
        # FK self : OF précédent / lavage
        # -------------------------
        of_precedent_id = request.POST.get("of_precedent")
        reglage.of_precedent_id = int(of_precedent_id) if of_precedent_id else None

        of_lavage_id = request.POST.get("of_lavage")
        reglage.of_lavage_id = int(of_lavage_id) if of_lavage_id else None

        # -------------------------
        # FK "choix + nouveau" (factorisé)
        # -------------------------
        handle_fk_select(request, reglage, field="godet", model=Godet, new_field="godet_new_value")
        handle_fk_select(request, reglage, field="butee_vis", model=Bute, new_field="butee_vis_new_value")
        handle_fk_select(request, reglage, field="pince_vis", model=Pince, new_field="pince_vis_new_value")
        handle_fk_select(request, reglage, field="pince_f", model=PinceF, new_field="pince_f_new_value")

        # -------------------------
        # Pompes 1..4 : pompe / FK bec / FK centreur (factorisé)
        # -------------------------
        for i in range(1, 5):
            if hasattr(reglage, f"pompe_{i}"):
                setattr(reglage, f"pompe_{i}", request.POST.get(f"pompe_{i}") or None)

            # Bec FK + _new
            if hasattr(reglage, f"tube_bec_{i}"):
                handle_fk_select(
                    request, reglage,
                    field=f"tube_bec_{i}",
                    model=Bec,
                    new_field=f"tube_bec_{i}_new_value"
                )

          
            if hasattr(reglage, f"centerur_{i}_id") or (i <= 3 and hasattr(reglage, f"centerur_{i}")):
                # centerur_1/2/3 sont FK
                if i <= 3:
                    handle_fk_select(
                        request, reglage,
                        field=f"centerur_{i}",
                        model=Centreur,
                        new_field=f"centerur_{i}_new_value"
                    )
                else:
                    # centerur_4 est texte -> on enregistre la valeur texte
                    setattr(reglage, "centerur_4", request.POST.get("centerur_4_new_value") or request.POST.get("centerur_4") or None)

        reglage.save()
        return redirect("detail_reglage", reglage_id=reglage.id)

    # GET
    return render(request, "machines/reglage_gabarit.html", {
        "reglage": reglage,
        "mode": "edit",
        "pompes": build_pompes(reglage),
        "ofs": ofs,
        "godets": godets,
        "becs": becs,
        "centreurs": centreurs,
        "butes": butes,
        "pinces": pinces,
        "pincesf": pincesf,
    })


# ============================================================
# API autocomplete OF
# ============================================================

@login_required
def api_of_list(request):
    term = request.GET.get("term", "").upper()
    qs = ReglageEKO.objects.filter(numeros_of__icontains=term).order_by("numeros_of")
    data = [{"id": r.id, "of": r.numeros_of, "nom": r.nom_produit} for r in qs[:20]]
    return JsonResponse(data, safe=False)