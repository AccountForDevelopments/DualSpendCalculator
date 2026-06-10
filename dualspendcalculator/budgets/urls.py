from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path("", views.MonthListView.as_view(), name="month_list"),
    path("create/", views.MonthCreateView.as_view(), name="month_create"),
    path("<int:pk>/", views.MonthDetailView.as_view(), name="month_detail"),
    path("<int:pk>/income/", views.IncomeUpdateView.as_view(), name="income_update"),
    path("agreement/download/", views.AgreementDownloadView.as_view(), name="agreement_download"),
]

