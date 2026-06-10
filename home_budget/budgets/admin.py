from django.contrib import admin

from .models import MonthlyBudget


@admin.register(MonthlyBudget)
class MonthlyBudgetAdmin(admin.ModelAdmin):
    list_display = ["year_month", "user_a", "user_b", "income_a", "income_b", "created_at"]
    list_filter = ["year_month"]
    search_fields = ["year_month"]
    ordering = ["-year_month"]

