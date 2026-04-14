import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from django.views.decorators.http import require_GET
from django.utils.html import escape
from django.db.models import F




from machines.models import (
    ReglageEKO, Godet, Bec, Centreur, Bute, Pince, PinceF, Vrac
)



# ============================================================
# Helpers
# ============================================================

def clean(v):
    return "" if v is None else str(v).strip()

def to_float(v):
    v = clean(v)
    if v == "" or v.lower() in ("nc", "n/c"):
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None

def handle_fk_select(request, obj, *, field, model, new_field):
    """
    Gère un champ FK alimenté par :
    - <select name="field"> value = id / "_new" / ""
    - <input  name="new_field"> valeur à créer (model(valeur=...))

    Assigne via field_id pour éviter : "must be a <Model> instance".
    """
    choice = request.POST.get(field)
    new_val = request.POST.get(new_field)

    if choice == "_new" and new_val:
        inst, _ = model.objects.get_or_create(valeur=new_val.strip())
        setattr(obj, field, inst)
        return

    if choice:
        setattr(obj, f"{field}_id", int(choice))
    else:
        setattr(obj, field, None)

def build_pompes(reglage: ReglageEKO):
    # P4 n'a pas motorise_4
    return [
        {"num": 1, "pompe": reglage.pompe_1, "valeur": reglage.valeur_1, "bec": reglage.tube_bec_1, "centerur": reglage.centerur_1, "motorise": reglage.motorise_1},
        {"num": 2, "pompe": reglage.pompe_2, "valeur": reglage.valeur_2, "bec": reglage.tube_bec_2, "centerur": reglage.centerur_2, "motorise": reglage.motorise_2},
        {"num": 3, "pompe": reglage.pompe_3, "valeur": reglage.valeur_3, "bec": reglage.tube_bec_3, "centerur": reglage.centerur_3, "motorise": reglage.motorise_3},
        {"num": 4, "pompe": reglage.pompe_4, "valeur": reglage.valeur_4, "bec": reglage.tube_bec_4, "centerur": getattr(reglage, "centerur_4", None), "motorise": None},
    ]

def is_blank_reglage(obj: ReglageEKO) -> bool:
    """
    Détecte un brouillon 'vide'. Ajuste si besoin.
    """
    def empty(s): return (s or "").strip() == ""
    return (
        (obj.ref or "").strip() in ("", "NOUVEAU")
        and empty(obj.nom_produit)
        and empty(obj.numeros_lot)
        and empty(obj.regleur)
        and empty(obj.observation)
        and obj.date_reglage is None
        and obj.volume is None
        and obj.volume_demarrage is None
        and empty(getattr(obj, "pompe_1", None))
        and empty(getattr(obj, "pompe_2", None))
        and empty(getattr(obj, "pompe_3", None))
        and empty(getattr(obj, "pompe_4", None))
        and getattr(obj, "valeur_1", None) is None
        and getattr(obj, "valeur_2", None) is None
        and getattr(obj, "valeur_3", None) is None
        and getattr(obj, "valeur_4", None) is None
    )

def make_unique_of(of_value: str) -> str:
    """
    Si l'OF existe déjà, suffixe -COPY1, -COPY2, ...
    """
    base = of_value.strip()
    if base == "":
        return ""
    if not ReglageEKO.objects.filter(numeros_of=base).exists():
        return base
    n = 1
    while True:
        cand = f"{base}-COPY{n}"
        if not ReglageEKO.objects.filter(numeros_of=cand).exists():
            return cand
        n += 1

def apply_post_to_reglage(request, obj: ReglageEKO):
    """
    Applique le formulaire sur obj (sauf numeros_of géré séparément).
    """
    # Champs simples
    obj.ref = request.POST.get("ref", "")
    obj.nom_produit = request.POST.get("nom_produit", "")
    obj.numeros_lot = request.POST.get("numeros_lot", "")
    obj.regleur = request.POST.get("regleur", "")
    obj.observation = request.POST.get("observation", "")
    obj.date_reglage = request.POST.get("date_reglage") or None

    # Floats principaux
    obj.volume = to_float(request.POST.get("volume"))
    obj.volume_demarrage = to_float(request.POST.get("volume_demarrage"))

    # Texte (si champ existe)
    for f in [
        "moussant", "ref_flacon", "programme", "filtre", "type_bec",
        "ctrl_jus_h", "ctrl_jus_prof", "ctrl_ultra",
        "presence_marteau", "embout",
        "presence_visseuse", "visseuse",
        "type_pince_ext", "type_pince_int",
        "convoyeur", "cames_bec_on", "cames_bec_off",
        "presence_cueilleur", "cueilleur", "cueilleur_1", "cueilleur_2", "cueilleur_3",
        "etiquette", "consigne_etiquette", "etiqueteuse",
    ]:
        if hasattr(obj, f):
            setattr(obj, f, request.POST.get(f, ""))

    # Floats divers
    for f in [
        "h_machine", "h_compo_1", "h_marteau", "h_compo_2",
        "couple_vis", "h_pince_ext", "h_pince_int",
        "cadence", "h_finale", "hauteur_rail",
    ]:
        if hasattr(obj, f):
            setattr(obj, f, to_float(request.POST.get(f)))

    # FK self: OF précédent / lavage
    of_precedent_id = request.POST.get("of_precedent")
    obj.of_precedent_id = int(of_precedent_id) if of_precedent_id else None

    of_lavage_id = request.POST.get("of_lavage")
    obj.of_lavage_id = int(of_lavage_id) if of_lavage_id else None

    # FK choix + nouveau
    if hasattr(obj, "godet"):
        handle_fk_select(request, obj, field="godet", model=Godet, new_field="godet_new_value")
    if hasattr(obj, "butee_vis"):
        handle_fk_select(request, obj, field="butee_vis", model=Bute, new_field="butee_vis_new_value")
    if hasattr(obj, "pince_vis"):
        handle_fk_select(request, obj, field="pince_vis", model=Pince, new_field="pince_vis_new_value")
    if hasattr(obj, "pince_f"):
        handle_fk_select(request, obj, field="pince_f", model=PinceF, new_field="pince_f_new_value")

    # VRAC FK : on stocke uniquement le lien
    if hasattr(obj, "vrac_ref_id"):
        vrac_choice = request.POST.get("vrac_ref")
        obj.vrac_ref_id = int(vrac_choice) if vrac_choice else None
        if hasattr(obj, "vrac"):
            obj.vrac = obj.vrac_ref.ref if obj.vrac_ref else ""

    # Pompes 1..4
    for i in range(1, 5):
        if hasattr(obj, f"pompe_{i}"):
            setattr(obj, f"pompe_{i}", request.POST.get(f"pompe_{i}") or None)
        if hasattr(obj, f"valeur_{i}"):
            setattr(obj, f"valeur_{i}", to_float(request.POST.get(f"valeur_{i}")))

        # Becs
        if hasattr(obj, f"tube_bec_{i}"):
            handle_fk_select(request, obj, field=f"tube_bec_{i}", model=Bec, new_field=f"tube_bec_{i}_new_value")

        # Centreurs (si centerur_4 est FK, ça marche aussi)
        if hasattr(obj, f"centerur_{i}"):
            handle_fk_select(request, obj, field=f"centerur_{i}", model=Centreur, new_field=f"centerur_{i}_new_value")

        # motorise_1..3 = texte chez toi (si champ existe)
        if i <= 3 and hasattr(obj, f"motorise_{i}"):
            setattr(obj, f"motorise_{i}", request.POST.get(f"motorise_{i}", ""))

 #Historique

@require_GET
@login_required
def api_history_by_ref(request, ref):
    ref = ref.strip()
    if not ref:
        return JsonResponse({"ref": "", "items": []})

    qs = (
        ReglageEKO.objects
        .filter(ref=ref)
        .order_by(F("date_reglage").desc(nulls_last=True), F("id").desc())
        .values(
            "id", "numeros_of", "numeros_lot", "nom_produit", "date_reglage",
            "regleur", "volume_demarrage", "cadence", "observation"
        )
    )

    # JSON serialisable: date -> str
    items = []
    for r in qs:
        items.append({
            "id": r["id"],
            "numeros_of": r["numeros_of"] or "",
            "numeros_lot": r["numeros_lot"] or "",
            "nom_produit": r["nom_produit"] or "",
            "date_reglage": r["date_reglage"].isoformat() if r["date_reglage"] else "",
            "regleur": r["regleur"] or "",
            "volume_demarrage": r["volume_demarrage"],
            "cadence": r["cadence"],
            "observation": r["observation"]
        })

    return JsonResponse({"ref": ref, "items": items})

#historique vrac

@require_GET
@login_required
def api_vrac_usage(request, vrac_id):
    qs = (
        ReglageEKO.objects
        .filter(vrac_ref_id=vrac_id)
        .order_by(F("date_reglage").desc(nulls_last=True), F("id").desc())
        .values(
            "id",
            "ref",
            "numeros_of",
            "numeros_lot",
            "nom_produit",
            "date_reglage",
            "regleur",
            "volume",
        )
    )

    items = []
    for r in qs:
        items.append({
            "id": r["id"],
            "ref": r["ref"] or "",
            "numeros_of": r["numeros_of"] or "",
            "numeros_lot": r["numeros_lot"] or "",
            "nom_produit": r["nom_produit"] or "",
            "date_reglage": r["date_reglage"].isoformat() if r["date_reglage"] else "",
            "regleur": r["regleur"] or "",
            "volume": r["volume"],
        })

    return JsonResponse({
        "vrac_id": vrac_id,
        "count": len(items),
        "items": items,
    })

# ============================================================
# Create / Cancel / Delete
# ============================================================

@login_required
@permission_required("machines.add_reglageeko", raise_exception=True)
def create_reglage(request):
    """
    Nouveau brouillon : OF NULL seulement si fiche vide.
    ⚠️ Si ta DB force '' au lieu de NULL, on fallback sur DRAFT-...
    """
    try:
        reglage = ReglageEKO.objects.create(
            ref="NOUVEAU",
            numeros_of=None,     # OF NULL
            numeros_lot="",
            nom_produit="",
            date_reglage=timezone.localdate(),
        )
    except IntegrityError:
        # Fallback si ta DB transforme None en '' (unique)
        draft = f"DRAFT-{timezone.now():%Y%m%d%H%M%S}-{uuid.uuid4().hex[:6]}"
        reglage = ReglageEKO.objects.create(
            ref="NOUVEAU",
            numeros_of=draft,
            numeros_lot="",
            nom_produit="",
            date_reglage=timezone.localdate(),
        )

    url = reverse("edit_reglage", kwargs={"reglage_id": reglage.id})
    return HttpResponseRedirect(f"{url}?new=1")

@login_required
@permission_required("machines.change_reglageeko", raise_exception=True)
def cancel_new_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    # supprime seulement si c'est un brouillon vide
    is_draft = (
        reglage.ref == "NOUVEAU"
        and (reglage.numeros_of is None or str(reglage.numeros_of).startswith("DRAFT-"))
        and is_blank_reglage(reglage)
    )
    if is_draft:
        reglage.delete()

    return redirect("recherche_reglages")

@login_required
@permission_required("machines.delete_reglageeko", raise_exception=True)
def delete_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)
    if request.method == "POST":
        reglage.delete()
        return redirect("recherche_reglages")
    return render(request, "machines/delete_confirm.html", {"reglage": reglage})

# ============================================================
# Recherche / Détail / Edit + Dupliquer
# ============================================================

@login_required
def recherche_reglages(request):
    reglages = ReglageEKO.objects.all().order_by("-date_reglage", "-id")

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

@login_required
def detail_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    context = {
        "reglage": reglage,
        "mode": "view",
        "pompes": build_pompes(reglage),

        "ofs": ReglageEKO.objects.exclude(id=reglage.id).order_by("-date_reglage", "-id"),
        "godets": Godet.objects.all().order_by("valeur"),
        "becs": Bec.objects.all().order_by("valeur"),
        "centreurs": Centreur.objects.all().order_by("valeur"),
        "butes": Bute.objects.all().order_by("valeur"),
        "pinces": Pince.objects.all().order_by("valeur"),
        "pincesf": PinceF.objects.all().order_by("valeur"),
        "vracs": Vrac.objects.all().order_by("ref"),
    }
    return render(request, "machines/reglage_gabarit.html", context)

@login_required
@permission_required("machines.change_reglageeko", raise_exception=True)
def edit_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    ofs = ReglageEKO.objects.exclude(id=reglage.id).order_by("-date_reglage", "-id")
    godets = Godet.objects.all().order_by("valeur")
    becs = Bec.objects.all().order_by("valeur")
    centreurs = Centreur.objects.all().order_by("valeur")
    butes = Bute.objects.all().order_by("valeur")
    pinces = Pince.objects.all().order_by("valeur")
    pincesf = PinceF.objects.all().order_by("valeur")
    vracs = Vrac.objects.all().order_by("ref")

    if request.method == "POST":
        # ✅ action existe toujours en POST
        action = request.POST.get("action", "save")

        # ✅ target existe toujours (évite UnboundLocalError)
        target = reglage
        source_of = reglage.numeros_of  # OF original (utile en duplication)

        if action == "duplicate":
            target = ReglageEKO()
            # champs minimum non blank
            target.ref = request.POST.get("ref", "COPIE")
            target.numeros_lot = request.POST.get("numeros_lot", "")
            target.nom_produit = request.POST.get("nom_produit", "")
            # OF géré plus bas selon règles (souvent NULL)

        # Applique le formulaire au bon objet
        apply_post_to_reglage(request, target)

        # ==================================================
        # RÈGLE OF :
        # - NULL si fiche vide
        # - en duplication : NULL si OF vide OU identique à l'original
        # - sinon : si OF saisi, le garder (unique si conflit)
        # - sinon : en save, ne pas écraser l’OF existant
        # ==================================================
        posted_of = clean(request.POST.get("numeros_of"))  # nécessite un input dans le template

        if is_blank_reglage(target):
            target.numeros_of = None

        elif action == "duplicate" and (posted_of == "" or (source_of and posted_of == source_of)):
            target.numeros_of = None

        elif posted_of != "" and action == "duplicate":
            target.numeros_of = make_unique_of(posted_of)

        elif posted_of != "" and action == "save":
            # ✅ édition normale : on garde exactement l’OF saisi
            target.numeros_of = posted_of
        else:
            # Save normal : ne pas écraser l’OF existant si champ laissé vide
            if action == "duplicate":
                target.numeros_of = None
            # action == save -> on conserve celui existant
            # (rien à faire)

        target.save()

        # OPTION 2 : duplication -> détail de la copie
        if action == "duplicate":
            return redirect("detail_reglage", reglage_id=target.id)

        return redirect("detail_reglage", reglage_id=reglage.id)

    # GET
    context = {
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
        "vracs": vracs,
    }
    return render(request, "machines/reglage_gabarit.html", context)

# ============================================================
# API
# ============================================================

@login_required
def api_of_list(request):
    term = request.GET.get("term", "").upper()
    qs = ReglageEKO.objects.filter(numeros_of__icontains=term).order_by("numeros_of")
    data = [{"id": r.id, "of": r.numeros_of, "nom": r.nom_produit} for r in qs[:20]]
    return JsonResponse(data, safe=False)

@login_required
def api_vrac_detail(request, vrac_id):
    v = get_object_or_404(Vrac, id=vrac_id)
    return JsonResponse({
        "id": v.id,
        "ref": v.ref,
        "Nom_vrac": v.Nom_vrac,
        "vrac_type": v.vrac_type,
        "pompe": v.pompe,
        "etuve": v.etuve,
        "temperature": v.temperature,
        "circuit_ferme_microbio": v.circuit_ferme_microbio,
        "commentaire": v.commentaire,
        "labo_validation": v.labo_validation,
        "microbio_validation": v.microbio_validation,
    })