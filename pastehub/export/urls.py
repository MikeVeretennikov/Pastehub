from django.urls import path

from export.views import export_docx, export_json, export_source


app_name = "export"

urlpatterns = [
    path(
        "<str:short_link>/<int:version>/source", export_source, name="source",
    ),
    path("<str:short_link>/<int:version>/json", export_json, name="json"),
    path("<str:short_link>/<int:version>/docx", export_docx, name="docx"),
]
