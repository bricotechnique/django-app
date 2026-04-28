from django.db import models

from django.conf import settings
from django.db import models
from django.conf import settings





class ReglageEKOHistory(models.Model):
    reglage = models.ForeignKey(
        "ReglageEKO",
        related_name="history",
        on_delete=models.CASCADE
    )

    version = models.PositiveIntegerField()

    snapshot = models.JSONField()

    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version"]

    def __str__(self):
        return f"{self.reglage.ref} v{self.version}"




class Vrac(models.Model):
    ref = models.CharField(max_length=50, unique=True, db_index=True)  # identifiant VRAC (clé)
    vrac_type = models.CharField(max_length=50, blank=True)
    pompe = models.CharField(max_length=50, blank=True)
    etuve = models.CharField(max_length=50, blank=True)
    temperature = models.CharField(max_length=50, blank=True)
    Nom_vrac = models.CharField(max_length=50, blank=True)
    circuit_ferme_microbio = models.CharField(max_length=10, blank=True)  # ou BooleanField si tu veux plus tard
    commentaire = models.TextField(blank=True)
    labo_validation = models.CharField(max_length=50, blank=True)
    microbio_validation = models.CharField(max_length=50, blank=True)
    marque = models.CharField(max_length=50, blank=True)


    def __str__(self):
        return self.ref


class Bec(models.Model):
    valeur = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.valeur

class Bute(models.Model):
    valeur = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.valeur

class Pince(models.Model):
    valeur = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.valeur
    

class PinceF(models.Model):
    valeur = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.valeur
    

class Centreur(models.Model):
    valeur = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.valeur

class Godet(models.Model):
    valeur = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.valeur
    


 
   

class ReglageEKO(models.Model):
    # =====================================================
    # IDENTIFICATION / TRACABILITÉ
    # =====================================================

    version = models.PositiveIntegerField(default=1)
    ref = models.CharField(max_length=200)
    nom_produit = models.CharField(max_length=200, blank=True)
    machine_choices = [("EKO", "EKO"),("G1", "G1"),("K", "K"),("N", "N"),("A", "A"),("Dumek", "Dumek"),]

    machine = models.CharField(
        max_length=10,
        choices=machine_choices,
        default="EKO"
    )

    
    numeros_of = models.CharField(
        max_length=100,
        null=True,       # ✅ OBLIGATOIRE
        blank=True,      # ✅ OBLIGATOIRE
        unique=False,
        db_index=True,
    )
    numeros_lot = models.CharField(max_length=100, db_index=True)


    of_precedent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reglages_suivants",
    )

    of_lavage = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reglages_lavage_suivants",
    )
    date_reglage = models.DateField(null=True, blank=True)

    regleur = models.CharField(max_length=50, blank=True)
    observation = models.CharField(max_length=1000, null=True, blank=True)
    # =====================================================
    # PRODUIT / REMPLISSAGE
    # =====================================================
    moussant = models.CharField(max_length=10, blank=True)
    ref_flacon = models.CharField(max_length=100, blank=True)
    programme = models.CharField(max_length=50, blank=True)

    godet = models.ForeignKey(Godet, null=True, blank=True, on_delete=models.SET_NULL)

    butee_vis = models.ForeignKey(Bute, null=True, blank=True, on_delete=models.SET_NULL)

    
    pince_vis = models.ForeignKey(Pince, null=True, blank=True, on_delete=models.SET_NULL)

    pince_f = models.ForeignKey(PinceF, null=True, blank=True, on_delete=models.SET_NULL)


    volume = models.FloatField(null=True, blank=True)
    volume_demarrage = models.FloatField(null=True, blank=True)

    filtre = models.CharField(max_length=10, blank=True)

    # =====================================================
    # POMPE 1
    # =====================================================
    pompe_1 = models.CharField(max_length=10, null=True, blank=True)
    motorise_1 = models.CharField(max_length=10, blank=True)
    valeur_1 = models.FloatField(null=True, blank=True)
    bute_bec_1 = models.CharField(max_length=50, null=True, blank=True)
    tube_bec_1 = models.ForeignKey(Bec, null=True, blank=True, on_delete=models.SET_NULL, related_name="tubes_bec_p1")
    centerur_1 = models.ForeignKey(Centreur, null=True, blank=True, on_delete=models.SET_NULL, related_name="p1")

    # =====================================================
    # POMPE 2
    # =====================================================
    pompe_2 = models.CharField(max_length=10, null=True, blank=True)
    motorise_2 = models.CharField(max_length=10, blank=True)
    valeur_2 = models.FloatField(null=True, blank=True)
    bute_bec_2 = models.CharField(max_length=50, null=True, blank=True)
    tube_bec_2 = models.ForeignKey(Bec, null=True, blank=True, on_delete=models.SET_NULL, related_name="tubes_bec_p2")
    centerur_2 = models.ForeignKey(Centreur, null=True, blank=True, on_delete=models.SET_NULL, related_name="p2")

    # =====================================================
    # POMPE 3
    # =====================================================
    pompe_3 = models.CharField(max_length=50, null=True, blank=True)
    motorise_3 = models.CharField(max_length=10, blank=True)
    valeur_3 = models.FloatField(null=True, blank=True)
    bute_bec_3 = models.CharField(max_length=50, null=True, blank=True)
    tube_bec_3 = models.ForeignKey(Bec, null=True, blank=True, on_delete=models.SET_NULL, related_name="tubes_bec_p3")
    centerur_3 = models.ForeignKey(Centreur, null=True, blank=True, on_delete=models.SET_NULL, related_name="p3")

    # =====================================================
    # POMPE 4
    # =====================================================
    pompe_4 = models.CharField(max_length=10, null=True, blank=True)
    valeur_4 = models.FloatField(null=True, blank=True)
    bute_bec_4 = models.CharField(max_length=50, null=True, blank=True)
    tube_bec_4 = models.ForeignKey(Bec, null=True, blank=True, on_delete=models.SET_NULL, related_name="tubes_bec_p4")
    centerur_4 = models.ForeignKey(Centreur, null=True, blank=True, on_delete=models.SET_NULL, related_name="p4")

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

    h_pince_ext = models.FloatField(null=True, blank=True)
    h_pince_int = models.FloatField(null=True, blank=True)

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
    vrac_ref = models.ForeignKey("Vrac", null=True, blank=True, on_delete=models.SET_NULL, related_name="reglages")

    
    # META
    # =====================================================
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)



    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ref} v{self.version}"

    class Meta:
        ordering = ["-date_reglage"]

    def __str__(self):
        return f"{self.ref} | OF {self.numeros_of} | Lot {self.numeros_lot}"
    

class ReglageEKOChange(models.Model):
    reglage = models.ForeignKey(
        ReglageEKO,
        on_delete=models.CASCADE,
        related_name="changes"
    )

    version_from = models.PositiveIntegerField()
    version_to = models.PositiveIntegerField()

    field = models.CharField(max_length=100)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["version_to", "changed_at"]

    def __str__(self):
        return f"{self.field} v{self.version_from}→v{self.version_to}"