from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.urls import include, path

from budgets.views import DashboardView


def healthcheck(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck),
    # 認証（accounts アプリを削除し、Django 組み込みビューを直接使用）
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    # ダッシュボード（settlements アプリを削除し、budgets アプリに統合）
    path("", DashboardView.as_view(), name="dashboard"),
    # App URLs
    path("months/", include("budgets.urls")),
    path("months/", include("transactions.urls")),
    path("months/", include("csv_import.urls")),
]
