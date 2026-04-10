from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import ReglageEKO
from django.contrib.auth.decorators import login_required
from machines.models import ReglageEKO, Godet

from django.contrib.auth.decorators import permission_required

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



@login_required
@permission_required("machines.add_reglageeko", raise_exception=True)
def create_reglage(request):
    reglage = ReglageEKO.objects.create(
        ref="NOUVEAU",
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
    return render(request, "machines/detail_reglage.html", {"reglage": reglage})


# ============================================================
# 3 — PAGE ÉDITION + DUPLICATION
# ============================================================
login_required


@permission_required("machines.change_reglageeko", raise_exception=True)

def edit_reglage(request, reglage_id):
    reglage = get_object_or_404(ReglageEKO, id=reglage_id)
    ofs = ReglageEKO.objects.all().order_by("numeros_of")
    godets = Godet.objects.all().order_by("valeur")

    if request.method == "POST":
        mode = request.POST.get("mode")



        godet_value = request.POST.get("godet")

        if godet_value:
            godet_obj, _ = Godet.objects.get_or_create(valeur=godet_value.strip())
            reglage.godet = godet_obj
        else:
            reglage.godet = None

        # Champs simples
        reglage.ref = request.POST.get("ref")
        reglage.nom_produit = request.POST.get("nom_produit")
        reglage.numeros_of = request.POST.get("numeros_of")
        reglage.numeros_lot = request.POST.get("numeros_lot")
        reglage.volume = request.POST.get("volume")
        reglage.observation = request.POST.get("observation")

        
        of_precedent_id = request.POST.get("of_precedent")
        of_lavage_id = request.POST.get("of_lavage")

        reglage.of_precedent = (
            ReglageEKO.objects.filter(id=of_precedent_id).first()
            if of_precedent_id else None
        )

        reglage.of_lavage = (
            ReglageEKO.objects.filter(id=of_lavage_id).first()
            if of_lavage_id else None
        )


        # DUPLICATION
        if mode == "duplicate":
            reglage.pk = None
            reglage.save()
            return redirect("detail_reglage", reglage_id=reglage.id)

        # ENREGISTRER
        reglage.save()
        return redirect("detail_reglage", reglage_id=reglage_id)

    
    return render(request, "machines/edit_reglage.html", {
            "reglage": reglage,
            "godets": godets,  
            "ofs": ofs,
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

