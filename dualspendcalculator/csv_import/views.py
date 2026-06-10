"""
CSVインポートビュー

アダプターを注入してサービスを使用する。
依存性逆転の原則（DIP）により、ビューはサービスの抽象に依存する。
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from .forms import CSVUploadForm
from .services import CSVImportService
from .adapters import DjangoTransactionRepository
from budgets.models import MonthlyBudget


class CSVUploadView(LoginRequiredMixin, View):
    """CSVアップロードビュー
    
    アダプター（DjangoTransactionRepository）を注入して、
    CSVImportService を使用する。
    
    設計原則:
    - DIP: ビューはサービスとリポジトリの抽象に依存
    - ポートとアダプター: Django固有の実装はアダプターに閉じ込め
    """

    def post(self, request, pk):
        month = get_object_or_404(MonthlyBudget, pk=pk)
        form = CSVUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            
            # アダプターを注入してサービスを使用
            repository = DjangoTransactionRepository(month)
            service = CSVImportService(repository)
            result = service.import_csv(csv_file)
            
            if result.success_count > 0:
                messages.success(request, f"{result.success_count}件の明細を取り込みました")
            
            if result.duplicate_count > 0:
                messages.info(request, f"重複スキップ: {result.duplicate_count}件")
            
            if result.skip_count > 0:
                messages.info(request, f"除外行スキップ: {result.skip_count}件")
            
            if result.error_count > 0:
                messages.warning(request, f"エラー: {result.error_count}件")
            
            for error in result.errors[:5]:  # 最初の5件のみ表示
                messages.error(request, error)
            
            if result.success_count == 0 and result.error_count == 0 and result.duplicate_count == 0:
                messages.warning(request, "取り込み対象のデータがありませんでした")
        else:
            for error in form.errors.get("csv_file", []):
                messages.error(request, error)
        
        return redirect("budgets:month_detail", pk=pk)
