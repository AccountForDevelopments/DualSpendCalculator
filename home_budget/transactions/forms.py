from django import forms
from django.contrib.auth.models import User

from .models import Transaction


class TransactionFilterForm(forms.Form):
    """明細フィルタフォーム"""
    
    LIVING_COST_CHOICES = [
        ("", "すべて"),
        ("true", "生活費対象のみ"),
        ("false", "生活費対象外のみ"),
    ]
    
    PAYER_CHOICES = [
        ("", "すべて"),
        ("unset", "未設定"),
    ]
    
    CATEGORY_CHOICES = [
        ("", "すべて"),
    ] + list(Transaction.CATEGORY_CHOICES)
    
    is_living_cost = forms.ChoiceField(
        choices=LIVING_COST_CHOICES,
        required=False,
        label="生活費対象",
        widget=forms.Select(attrs={"class": "form-input form-input--sm"}),
    )
    
    payer = forms.ChoiceField(
        choices=PAYER_CHOICES,
        required=False,
        label="支払者",
        widget=forms.Select(attrs={"class": "form-input form-input--sm"}),
    )
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        label="カテゴリ",
        widget=forms.Select(attrs={"class": "form-input form-input--sm"}),
    )
    
    amount_min = forms.IntegerField(
        required=False,
        label="金額（最小）",
        widget=forms.NumberInput(attrs={
            "class": "form-input form-input--sm",
            "placeholder": "最小金額",
            "min": "0",
        }),
    )
    
    amount_max = forms.IntegerField(
        required=False,
        label="金額（最大）",
        widget=forms.NumberInput(attrs={
            "class": "form-input form-input--sm",
            "placeholder": "最大金額",
            "min": "0",
        }),
    )
    
    def __init__(self, *args, monthly_budget=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 支払者の選択肢を動的に設定
        if monthly_budget:
            payer_choices = [
                ("", "すべて"),
                ("unset", "未設定"),
                (str(monthly_budget.user_a.id), monthly_budget.user_a.username),
                (str(monthly_budget.user_b.id), monthly_budget.user_b.username),
            ]
            self.fields["payer"].choices = payer_choices


class TransactionEditForm(forms.ModelForm):
    """明細編集フォーム"""
    
    class Meta:
        model = Transaction
        fields = ["is_living_cost", "payer", "category", "memo"]
        widgets = {
            "is_living_cost": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "payer": forms.Select(attrs={"class": "form-input"}),
            "category": forms.Select(attrs={"class": "form-input"}),
            "memo": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 3,
                "placeholder": "メモを入力...",
            }),
        }
    
    def __init__(self, *args, monthly_budget=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 支払者の選択肢をMonthlyBudgetのuser_a/user_bに制限
        if monthly_budget:
            self.fields["payer"].queryset = User.objects.filter(
                id__in=[monthly_budget.user_a.id, monthly_budget.user_b.id]
            )
        elif self.instance and self.instance.pk:
            mb = self.instance.monthly_budget
            self.fields["payer"].queryset = User.objects.filter(
                id__in=[mb.user_a.id, mb.user_b.id]
            )

