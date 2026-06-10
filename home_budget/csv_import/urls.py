from django.urls import path

from . import views

app_name = "csv_import"

urlpatterns = [
    path("<int:pk>/upload/", views.CSVUploadView.as_view(), name="csv_upload"),
]

