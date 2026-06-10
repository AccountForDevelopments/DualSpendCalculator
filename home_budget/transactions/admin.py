from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["date", "description", "amount", "is_living_cost", "payer", "category", "monthly_budget"]
    list_filter = ["is_living_cost", "category", "payer", "monthly_budget"]
    search_fields = ["description", "memo"]
    ordering = ["-date", "-id"]
    date_hierarchy = "date"

