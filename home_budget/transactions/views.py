from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import RedirectView, UpdateView, View

from .forms import TransactionEditForm
from .models import Transaction
from .services import BulkTransactionActionService
from budgets.models import MonthlyBudget


class TransactionListView(LoginRequiredMixin, RedirectView):
    """旧・明細一覧 URL。月次詳細（明細セクション）へクエリを引き継いでリダイレクトする。"""

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        pk = self.kwargs["pk"]
        get_object_or_404(MonthlyBudget, pk=pk)
        return reverse("budgets:month_detail", kwargs={"pk": pk})


class TransactionEditView(LoginRequiredMixin, UpdateView):
    """明細編集画面"""
    model = Transaction
    form_class = TransactionEditForm
    template_name = "transactions/transaction_edit.html"
    context_object_name = "transaction"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Transaction,
            pk=self.kwargs["transaction_pk"],
            monthly_budget_id=self.kwargs["pk"]
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["monthly_budget"] = self.object.monthly_budget
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["month"] = self.object.monthly_budget
        return context

    def form_valid(self, form):
        messages.success(self.request, "明細を更新しました")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("budgets:month_detail", kwargs={"pk": self.kwargs["pk"]})


class BulkActionView(LoginRequiredMixin, View):
    """一括操作ビュー"""

    def post(self, request, pk):
        month = get_object_or_404(MonthlyBudget, pk=pk)
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected")

        result = BulkTransactionActionService().apply(month, action, selected_ids)
        getattr(messages, result.level)(request, result.message)
        return self._redirect_with_filters(request, pk)

    def _redirect_with_filters(self, request, pk):
        """フィルタパラメータを保持してリダイレクト"""
        base_url = reverse("budgets:month_detail", kwargs={"pk": pk})
        # フィルタパラメータを取得
        filter_params = request.POST.get("filter_params", "")
        if filter_params:
            return redirect(f"{base_url}?{filter_params}")
        return redirect(base_url)

