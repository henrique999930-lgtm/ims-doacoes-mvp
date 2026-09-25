from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("familias/nova/", views.family_create, name="family_create"),
    path("estoque/", views.stock, name="stock"),
    path("entregas/nova/<int:family_id>/", views.delivery_create, name="delivery_create"),
    path("entregas/<int:delivery_id>/sucesso/", views.delivery_success, name="delivery_success"),
]
