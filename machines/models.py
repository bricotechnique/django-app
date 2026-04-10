from django.db import models


class ReglageEKO(models.Model):
    # =====================================================
    # IDENTIFICATION / TRACABILITÉ
    # =====================================================
    ref = models.CharField(max_length=200)
    nom_produit = models.CharField(max_length=200, blank=True)

    numeros_of = models.CharField(max_length=100, db_index=True)
    numeros_lot = models.CharField(max_length=100, db_index=True)

    of_precedent = models.ForeignKey(
    "self",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="precedents"
    )

    of_lavage = models.ForeignKey(
    "self",
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="lavages"
    )
    
    date_reglage = models.DateTimeField(null=True, blank=True)

    regleur = models.CharField(max_length=50, blank=True)
    observation = models.TextField(blank=True)

    # =====================================================
    # PRODUIT / REMPLISSAGE
    # =====================================================
    moussant = models.CharField(max_length=10, blank=True)
    ref_flacon = models.CharField(max_length=100, blank=True)
    programme = models.CharField(max_length=50, blank=True)
    godet = models.CharField(max_length=50, blank=True)

    volume = models.FloatField(null=True, blank=True)
    volume_demarrage = models.FloatField(null=True, blank=True)

    filtre = models.CharField(max_length=10, blank=True)

    # =====================================================
    # POMPE 1
    # =====================================================
    pompe_1 = models.CharField(max_length=10, blank=True)
    motorise_1 = models.CharField(max_length=10, blank=True)
    valeur_1 = models.FloatField(null=True, blank=True)
    bute_bec_1 = models.CharField(max_length=50, blank=True)
    tube_bec_1 = models.CharField(max_length=50, blank=True)
    centerur_1 = models.CharField(max_length=50, blank=True)

    # =====================================================
    # POMPE 2
    # =====================================================
    pompe_2 = models.CharField(max_length=10, blank=True)
    motorise_2 = models.CharField(max_length=10, blank=True)
    valeur_2 = models.FloatField(null=True, blank=True)
    bute_bec_2 = models.CharField(max_length=50, blank=True)
    tube_bec_2 = models.CharField(max_length=50, blank=True)
    centerur_2 = models.CharField(max_length=50, blank=True)

    # =====================================================
    # POMPE 3
    # =====================================================
    pompe_3 = models.CharField(max_length=10, blank=True)
    motorise_3 = models.CharField(max_length=10, blank=True)
    valeur_3 = models.FloatField(null=True, blank=True)
    bute_bec_3 = models.CharField(max_length=50, blank=True)
    tube_bec_3 = models.CharField(max_length=50, blank=True)
    centerur_3 = models.CharField(max_length=50, blank=True)

    # =====================================================
    # POMPE 4
    # =====================================================
    pompe_4 = models.CharField(max_length=10, blank=True)
    valeur_4 = models.FloatField(null=True, blank=True)
    bute_bec_4 = models.CharField(max_length=50, blank=True)
    tube_bec_4 = models.CharField(max_length=50, blank=True)
    centerur_4 = models.CharField(max_length=50, blank=True)

    # =====================================================
    # BEC / HAUTEURS / CONTROLES
    # =====================================================
    type_bec = models.CharField(max_length=50, blank=True)

    h_machine = models.FloatField(null=True, blank=True)
    ctrl_jus_h = models.CharField(max_length=10, blank=True)
    ctrl_jus_prof = models.CharField(max_length=10, blank=True)
    ctrl_ultra = models.CharField(max_length=10, blank=True)

    h_compo_1 = models.FloatField(null=True, blank=True)
    presence_marteau = models.CharField(max_length=10, blank=True)
    h_marteau = models.FloatField(null=True, blank=True)

    embout = models.CharField(max_length=50, blank=True)
    h_compo_2 = models.FloatField(null=True, blank=True)

    presence_visseuse = models.CharField(max_length=10, blank=True)
    couple_vis = models.FloatField(null=True, blank=True)
    butee_vis = models.FloatField(null=True, blank=True)

    pince_vis = models.CharField(max_length=50, blank=True)
    h_pince_ext = models.FloatField(null=True, blank=True)
    type_pince_ext = models.CharField(max_length=50, blank=True)

    h_pince_int = models.FloatField(null=True, blank=True)
    type_pince_int = models.CharField(max_length=50, blank=True)

    cadence = models.FloatField(null=True, blank=True)
    visseuse = models.CharField(max_length=50, blank=True)

    h_finale = models.FloatField(null=True, blank=True)
    convoyeur = models.CharField(max_length=50, blank=True)

    cames_bec_on = models.CharField(max_length=50, blank=True)
    cames_bec_off = models.CharField(max_length=50, blank=True)

    # =====================================================
    # CUEILLEUR
    # =====================================================
    presence_cueilleur = models.CharField(max_length=10, blank=True)
    cueilleur = models.CharField(max_length=50, blank=True)
    cueilleur_1 = models.CharField(max_length=50, blank=True)
    cueilleur_2 = models.CharField(max_length=50, blank=True)
    cueilleur_3 = models.CharField(max_length=50, blank=True)

    hauteur_rail = models.FloatField(null=True, blank=True)

    # =====================================================
    # ETIQUETAGE
    # =====================================================
    etiquette = models.CharField(max_length=50, blank=True)
    consigne_etiquette = models.TextField(blank=True)
    etiqueteuse = models.CharField(max_length=50, blank=True)

    # =====================================================
    # VRAC (REFERENCE – LIAISON FUTURE)
    # =====================================================
    vrac = models.CharField(max_length=10, blank=True)
    vrac_type = models.CharField(max_length=50, blank=True)
    vrac_pompe = models.CharField(max_length=50, blank=True)
    vrac_etuve = models.CharField(max_length=50, blank=True)
    vrac_temperature = models.CharField(max_length=50, blank=True)
    vrac_rincage_eko = models.CharField(max_length=10, blank=True)
    vrac_circuit_ferme_microbio = models.CharField(max_length=10, blank=True)
    vrac_commentaire = models.TextField(blank=True)

    vrac_labo_validation = models.CharField(max_length=10, blank=True)
    vrac_microbio_validation = models.CharField(max_length=10, blank=True)

    # =====================================================
    # META
    # =====================================================
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_reglage"]

    def __str__(self):
        return f"{self.ref} | OF {self.numeros_of} | Lot {self.numeros_lot}"