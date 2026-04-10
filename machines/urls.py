from django.urls import path
from .views import (
    recherche_reglages,
    detail_reglage,
    edit_reglage,
    delete_reglage,
    api_of_list,
)

urlpatterns = [
    path("", recherche_reglages, name="home"),
    path("recherche/", recherche_reglages, name="recherche_reglages"),

    path("reglage/<int:reglage_id>/", detail_reglage, name="detail_reglage"),
    path("reglage/<int:reglage_id>/edit/", edit_reglage, name="edit_reglage"),
    path("reglage/<int:reglage_id>/delete/", delete_reglage, name="delete_reglage"),

    path("api/of/", api_of_list, name="api_of_list"),
]