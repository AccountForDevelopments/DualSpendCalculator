import re

from django import forms
from django.contrib.auth.models import User

from .models import MonthlyBudget


class MonthlyBudgetCreateForm(forms.ModelForm):
    """月次予算作成フォーム"""
    
    class Meta:
        model = MonthlyBudget
        fields = ["year_month"]
        widgets = {
            "year_month": forms.TextInput(attrs={
                "type": "month",
                "class": "form-input",
                "placeholder": "YYYY-MM",
            }),
        }

    def clean_year_month(self):
        year_month = self.cleaned_data.get("year_month")
        
        # YYYY-MM形式のバリデーション
        if not re.match(r"^\d{4}-\d{2}$", year_month):
            raise forms.ValidationError("YYYY-MM形式で入力してください")
        
        # 重複チェック
        if MonthlyBudget.objects.filter(year_month=year_month).exists():
            raise forms.ValidationError("その月は既に存在します")
        
        return year_month

    def clean(self):
        cleaned_data = super().clean()
        user_count = (
            User.objects.filter(is_active=True)
            .exclude(is_superuser=True)
            .count()
        )
        if user_count < 2:
            raise forms.ValidationError(
                "ユーザーが2名以上必要です。管理画面でユーザーを作成してください。"
            )
        return cleaned_data


class IncomeForm(forms.ModelForm):
    """収入入力フォーム"""
    
    class Meta:
        model = MonthlyBudget
        fields = ["income_a", "income_b"]
        widgets = {
            "income_a": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "例: 300000",
                "min": "0",
            }),
            "income_b": forms.NumberInput(attrs={
                "class": "form-input",
                "placeholder": "例: 200000",
                "min": "0",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        income_a = cleaned_data.get("income_a")
        income_b = cleaned_data.get("income_b")
        
        # 両方入力されていて両方0の場合はエラー
        if income_a is not None and income_b is not None:
            if income_a == 0 and income_b == 0:
                raise forms.ValidationError("収入を入力してください（両方0は設定できません）")
        
        return cleaned_data

