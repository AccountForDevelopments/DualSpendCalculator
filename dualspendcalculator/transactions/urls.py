from django.urls import path

from . import views

app_name = "transactions"

urlpatterns = [
    path("<int:pk>/transactions/", views.TransactionListView.as_view(), name="transaction_list"),
    path("<int:pk>/transactions/<int:transaction_pk>/edit/", views.TransactionEditView.as_view(), name="transaction_edit"),
    path("<int:pk>/transactions/bulk/", views.BulkActionView.as_view(), name="bulk_action"),
]

