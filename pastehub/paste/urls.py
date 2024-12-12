from django.urls import path

from paste import views

app_name = "paste"

urlpatterns = [
    path("protected/", views.create_protected, name="create_protected"),
    path(
        "protected/<str:short_link>/",
        views.detail_protected,
        name="detail_protected",
    ),
    path(
        "protected/<str:short_link>/delete/",
        views.delete_protected,
        name="delete_protected",
    ),
    path("", views.create, name="create"),
    path("<str:short_link>/", views.detail, name="detail"),
    path(
        "<str:short_link>/<int:version>/", views.detail, name="version-detail",
    ),
    path("<str:short_link>/delete/", views.delete, name="delete"),
    path("<str:short_link>/edit/", views.edit, name="edit"),
]
