from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import ReglageEKO
from django.contrib.auth.decorators import login_required, permission_required
from machines.models import ReglageEKO, Godet, Bec, Centreur


@login_required

@permission_required("machines.delete_reglageeko", raise_exception=True)

def delete_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    if request.method == "POST":
        reglage.delete()
        return redirect("home")   # Retour à la recherche

    return render(request, "machines/delete_confirm.html", {"reglage": reglage})
# ============================================================
# 1 — PAGE RECHERCHE
# ============================================================

def parse_bool(v):
    if not v:
        return False
    return v.strip().lower() in ("true", "vrai", "oui", "1", "on", "checked")



@login_required
@permission_required("machines.add_reglageeko", raise_exception=True)
def create_reglage(request):
    reglage = ReglageEKO.objects.create(
        ref="",
        numeros_of=""
    )
    return redirect("edit_reglage", reglage_id=reglage.id)


@login_required
def recherche_reglages(request):
    reglages = ReglageEKO.objects.all().order_by("-date_reglage")

    ref = request.GET.get("ref")
    nom = request.GET.get("nom")
    lot = request.GET.get("lot")
    of = request.GET.get("of")
    volume = request.GET.get("volume")

    if ref:
        reglages = reglages.filter(ref__icontains=ref)
    if nom:
        reglages = reglages.filter(nom_produit__icontains=nom)
    if lot:
        reglages = reglages.filter(numeros_lot__icontains=lot)
    if of:
        reglages = reglages.filter(numeros_of__icontains=of)
    if volume:
        reglages = reglages.filter(volume=volume)


    return render(request, "machines/recherche_reglages.html", {"reglages": reglages})


# ============================================================
# 2 — PAGE DÉTAIL
# ============================================================

@login_required

def detail_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    pompes = [
    {
        "num": 1,
        "pompe": reglage.pompe_1,
        "valeur": reglage.valeur_1,
        "bec": reglage.tube_bec_1,
        "centerur": reglage.centerur_1,
        "motorise": reglage.motorise_1,
    },
    {
        "num": 2,
        "pompe": reglage.pompe_2,
        "valeur": reglage.valeur_2,
        "bec": reglage.tube_bec_2,
        "centerur": reglage.centerur_2,
        "motorise": reglage.motorise_2,
    },
    {
        "num": 3,
        "pompe": reglage.pompe_3,
        "valeur": reglage.valeur_3,
        "bec": reglage.tube_bec_3,
        "centerur": reglage.centerur_3,
        "motorise": reglage.motorise_3,
    },
    {
        "num": 4,
        "pompe": reglage.pompe_4,
        "valeur": reglage.valeur_4,
        "bec": reglage.tube_bec_4,
        "centerur": reglage.centerur_4,
        "motorise": None,  # ✅ IMPORTANT
    },
]



    return render(request, "machines/reglage_gabarit.html", {
    "reglage": reglage,
    "mode": "view",
    "pompes": pompes,
    })


# ============================================================
# 3 — PAGE ÉDITION + DUPLICATION
# ============================================================




@login_required
@permission_required("machines.change_reglageeko", raise_exception=True)
def edit_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)

    ofs = ReglageEKO.objects.exclude(id=reglage.id).order_by("numeros_of")
    godets = Godet.objects.all().order_by("valeur")
    pompes = [
        {
            "num": 1,
            "pompe": reglage.pompe_1,
            "valeur": reglage.valeur_1,
            "bec": reglage.tube_bec_1,
            "centerur": reglage.centerur_1,
            "motorise": reglage.motorise_1,
        },
        {
            "num": 2,
            "pompe": reglage.pompe_2,
            "valeur": reglage.valeur_2,
            "bec": reglage.tube_bec_2,
            "centerur": reglage.centerur_2,
            "motorise": reglage.motorise_2,
        },
        {
            "num": 3,
            "pompe": reglage.pompe_3,
            "valeur": reglage.valeur_3,
            "bec": reglage.tube_bec_3,
            "centerur": reglage.centerur_3,
            "motorise": reglage.motorise_3,
        },
        {
            "num": 4,
            "pompe": reglage.pompe_4,
            "valeur": reglage.valeur_4,
            "bec": reglage.tube_bec_4,
            "centerur": reglage.centerur_4,
            "motorise": None,  # ✅ IMPORTANT
        },
    ]


    # ==========================
    # POST = sauvegarde
    # ==========================
    if request.method == "POST":

        # Champs simples
        reglage.ref = request.POST.get("ref", "")
        reglage.nom_produit = request.POST.get("nom_produit", "")
        reglage.numeros_lot = request.POST.get("numeros_lot", "")
        reglage.regleur = request.POST.get("regleur", "")
        reglage.volume = request.POST.get("volume") or None
        reglage.observation = request.POST.get("observation", "")


        

        date_str = request.POST.get("date_reglage")

        if date_str:
            reglage.date_reglage = date_str   # Django convertit automatiquement YYYY-MM-DD
        else:
            reglage.date_reglage = None

    
        bec_choice_1 = request.POST.get("tube_bec_1")
        bec_new_1 = request.POST.get("tube_bec_1_new_value")

        if bec_choice_1 == "_new" and bec_new_1:
            bec_obj_1, _ = Bec.objects.get_or_create(valeur=bec_new_1.strip())
            reglage.tube_bec_1 = bec_obj_1
        elif bec_choice_1:
            reglage.tube_bec_1 = Bec.objects.filter(id=bec_choice_1).first()
        else:
            reglage.tube_bec_1 = None

      
        



        # OF précédent / lavage
        of_precedent_id = request.POST.get("of_precedent")
        reglage.of_precedent = (
            ReglageEKO.objects.filter(id=of_precedent_id).first()
            if of_precedent_id else None
        )

        of_lavage_id = request.POST.get("of_lavage")
        reglage.of_lavage = (
            ReglageEKO.objects.filter(id=of_lavage_id).first()
            if of_lavage_id else None
        )
        
        godet_choice = request.POST.get("godet")
        godet_new = request.POST.get("godet_new_value")

        if godet_choice == "_new" and godet_new:
            reglage.godet, _ = Godet.objects.get_or_create(valeur=godet_new.strip())
        elif godet_choice:
            reglage.godet = Godet.objects.filter(id=godet_choice).first()
        else:
            reglage.godet = None

        for i in range(1, 5):
            # Pompe (valeur select)
            reglage.__setattr__(f"pompe_{i}", request.POST.get(f"pompe_{i}") or None)

            # Valeur numérique
            reglage.__setattr__(f"valeur_{i}", request.POST.get(f"valeur_{i}") or None)

            cent_choice = request.POST.get(f"centerur_{i}")
            cent_new = request.POST.get(f"centerur_{i}_new_value")

            if cent_choice == "_new" and cent_new:
                cent_obj, _ = Centreur.objects.get_or_create(valeur=cent_new.strip())
                setattr(reglage, f"centerur_{i}", cent_obj)
            elif cent_choice:
                setattr(reglage, f"centerur_{i}_id", int(cent_choice))
            else:
                setattr(reglage, f"centerur_{i}", None)
            # Motorisé (seulement 1,2,3)
            if i <= 3:
                reglage.__setattr__(f"motorise_{i}", parse_bool(request.POST.get(f"motorise_{i}")))

            # BEC (table)
            bec_choice = request.POST.get(f"tube_bec_{i}")
            bec_new = request.POST.get(f"tube_bec_{i}_new_value")

            if bec_choice == "_new" and bec_new:
                bec_obj, _ = Bec.objects.get_or_create(valeur=bec_new.strip())
                reglage.__setattr__(f"tube_bec_{i}", bec_obj)

            elif bec_choice:
                reglage.__setattr__(f"tube_bec_{i}", Bec.objects.filter(id=bec_choice).first())

            else:
                reglage.__setattr__(f"tube_bec_{i}", None)



        reglage.save()
        return redirect("detail_reglage", reglage_id=reglage.id)

    # ==========================
    # GET = affichage du formulaire
    # ==========================
    return render(request, "machines/reglage_gabarit.html", {
        "reglage": reglage,
        "mode": "edit",
        "godets": godets,
        "ofs": ofs,
        "becs": Bec.objects.all().order_by("valeur"),
        "pompes": pompes,
        "centreurs": Centreur.objects.all().order_by("valeur"),
        
    })






# ============================================================
# 4 — API AUTOCOMPLETE OF
# ============================================================
login_required
def api_of_list(request):
    term = request.GET.get("term", "").upper()

    qs = ReglageEKO.objects.filter(numeros_of__icontains=term).order_by("numeros_of")

    data = [
        {"id": r.id, "of": r.numeros_of, "nom": r.nom_produit}
        for r in qs[:20]
    ]

    return JsonResponse(data, safe=False)

