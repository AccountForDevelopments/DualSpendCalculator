from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View

from .forms import IncomeForm, MonthlyBudgetCreateForm
from .models import MonthlyBudget
from .presenters import (
    build_income_ratio_context,
    build_month_detail_section_context,
    build_month_list_rows,
)
from .services import AgreementRequestValidator, SettlementCalculator


class MonthListView(LoginRequiredMixin, ListView):
    """月次一覧画面"""
    model = MonthlyBudget
    template_name = "budgets/month_list.html"
    context_object_name = "months"
    ordering = ["-year_month"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["month_rows"] = build_month_list_rows(context["months"])
        return context


class MonthCreateView(LoginRequiredMixin, CreateView):
    """月次作成画面"""
    model = MonthlyBudget
    form_class = MonthlyBudgetCreateForm
    template_name = "budgets/month_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = User.objects.filter(is_active=True).exclude(is_superuser=True)
        context["users"] = users
        context["can_create_month"] = users.count() >= 2
        return context

    def form_valid(self, form):
        users = User.objects.filter(is_active=True).exclude(is_superuser=True).order_by("id")[:2]
        form.instance.user_a = users[0]
        form.instance.user_b = users[1]
        messages.success(self.request, f"{form.instance.year_month} を作成しました")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("budgets:month_detail", kwargs={"pk": self.object.pk})


class MonthDetailView(LoginRequiredMixin, DetailView):
    """月次詳細画面（収入・CSV取り込み・明細一覧を同一画面で表示）。"""
    model = MonthlyBudget
    template_name = "budgets/month_detail.html"
    context_object_name = "month"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.object
        context["income_form"] = IncomeForm(instance=month)
        context.update(build_income_ratio_context(month))
        context.update(build_month_detail_section_context(month, self.request.GET))
        return context


class IncomeUpdateView(LoginRequiredMixin, View):
    """収入更新ビュー"""

    def post(self, request, pk):
        month = get_object_or_404(MonthlyBudget, pk=pk)
        form = IncomeForm(request.POST, instance=month)
        
        if form.is_valid():
            form.save()
            messages.success(request, "収入を保存しました")
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                if field != "__all__":
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        
        return redirect("budgets:month_detail", pk=pk)


class DashboardView(LoginRequiredMixin, TemplateView):
    """ダッシュボード画面
    
    精算サマリを表示するメイン画面。
    settlements アプリから budgets アプリに統合。
    """
    template_name = "budgets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # すべての月次データを取得（ドロップダウン用）
        all_months = MonthlyBudget.objects.all()
        context["all_months"] = all_months
        
        # 選択された月を取得（GETパラメータまたは最新月）
        selected_month_pk = self.request.GET.get("month")
        if selected_month_pk:
            try:
                selected_month = MonthlyBudget.objects.get(pk=selected_month_pk)
            except MonthlyBudget.DoesNotExist:
                selected_month = all_months.first()
        else:
            selected_month = all_months.first()
        
        context["selected_month"] = selected_month
        
        # 精算計算
        if selected_month:
            calculator = SettlementCalculator(selected_month)
            context["settlement"] = calculator.calculate()
        else:
            context["settlement"] = None
        
        return context


class AgreementDownloadView(LoginRequiredMixin, View):
    """家事按分同意書PDFダウンロードビュー"""
    
    def post(self, request):
        """POSTリクエストでPDFを生成・ダウンロード"""
        transaction_ids = request.POST.getlist("transaction_ids")
        monthly_budget_id = request.POST.get("monthly_budget_id")

        validation = AgreementRequestValidator().validate(
            transaction_ids, monthly_budget_id
        )
        if not validation.ok:
            messages.error(request, validation.message)
            if validation.redirect_pk is not None:
                return redirect(
                    validation.redirect_url_name, pk=validation.redirect_pk
                )
            return redirect(validation.redirect_url_name)

        monthly_budget = validation.monthly_budget
        transaction_ids_int = validation.transaction_ids

        from .services import AgreementCalculator, generate_agreement_pdf

        try:
            calculator = AgreementCalculator(monthly_budget)
            agreement_result = calculator.calculate(transaction_ids_int)
            pdf_bytes = generate_agreement_pdf(agreement_result)
        except Exception as e:
            messages.error(request, f"PDF生成中にエラーが発生しました: {str(e)}")
            return redirect("budgets:month_detail", pk=monthly_budget.pk)
        
        # PDFレスポンスを返却（RFC 5987 でファイル名をエンコード）
        filename = f"家事按分同意書_{agreement_result.year_month}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename*=utf-8''{quote(filename)}"
        return response

