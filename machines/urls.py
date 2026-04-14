from django.urls import path
from . import views
from .views import (
    recherche_reglages,
    detail_reglage,
    edit_reglage,
    delete_reglage,
    create_reglage,
    api_of_list,
)
from django.contrib import admin
from django.views.generic import RedirectView



    
urlpatterns = [
    path("", RedirectView.as_view(url="/login/", permanent=False)),
    path("recherche/", views.recherche_reglages, name="recherche_reglages"),
    path("reglage/new/", views.create_reglage, name="create_reglage"),
    path("reglage/<int:reglage_id>/", views.detail_reglage, name="detail_reglage"),
    path("reglage/<int:reglage_id>/edit/", views.edit_reglage, name="edit_reglage"),
    path("reglage/<int:reglage_id>/delete/", views.delete_reglage, name="delete_reglage"),
    path("reglage/<int:reglage_id>/cancel/", views.cancel_new_reglage, name="cancel_new_reglage"),
    path("api/of/", views.api_of_list, name="api_of_list"),
    path("api/vrac/<int:vrac_id>/", views.api_vrac_detail, name="api_vrac_detail"),
    path("api/reglage/history/<str:ref>/", views.api_history_by_ref, name="api_history_by_ref"),
    path("api/vrac/usage/<int:vrac_id>/", views.api_vrac_usage, name="api_vrac_usage"),
]