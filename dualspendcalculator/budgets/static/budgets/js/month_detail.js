/**
 * 月次詳細画面用JavaScript
 *
 * 機能:
 * - 一括選択（全選択/個別選択）
 * - 同意書ダウンロード
 */

document.addEventListener('DOMContentLoaded', function() {
    initSelectAll();
    initAgreementButton();
});

/**
 * 一括選択機能を初期化する
 */
function initSelectAll() {
    const selectAll = document.getElementById('select-all');
    const selectRows = document.querySelectorAll('.select-row');
    const selectedCount = document.querySelector('.selected-count');
    const bulkActions = document.querySelector('.bulk-actions');
    const emptyTitle = '1件以上選択してください';

    function updateSelectedCount() {
        const count = document.querySelectorAll('.select-row:checked').length;
        const isEmpty = count === 0;

        if (selectedCount) {
            selectedCount.textContent = count + '件選択中';
        }

        document.querySelectorAll('.bulk-action-btn').forEach(btn => {
            btn.disabled = isEmpty;
            btn.title = isEmpty ? emptyTitle : '';
        });

        if (bulkActions) {
            bulkActions.classList.toggle('bulk-actions--inactive', isEmpty);
        }
    }

    if (selectAll) {
        selectAll.addEventListener('change', function() {
            selectRows.forEach(cb => cb.checked = selectAll.checked);
            updateSelectedCount();
        });
    }

    selectRows.forEach(cb => {
        cb.addEventListener('change', function() {
            const allChecked = document.querySelectorAll('.select-row:checked').length === selectRows.length;
            if (selectAll) selectAll.checked = allChecked;
            updateSelectedCount();
        });
    });

    updateSelectedCount();
}

/**
 * 同意書ダウンロードボタンを初期化する
 * 選択されたTransaction IDと monthly_budget_id を動的フォームでPOST送信する
 */
function initAgreementButton() {
    const btn = document.getElementById('btn-agreement');
    if (!btn) return;

    btn.addEventListener('click', function() {
        const selectedIds = [...document.querySelectorAll('.select-row:checked')]
            .map(cb => cb.value);
        if (selectedIds.length === 0) return;

        const agreementUrl = btn.dataset.agreementUrl;
        const monthId = btn.dataset.monthId;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = agreementUrl;

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);

        const monthInput = document.createElement('input');
        monthInput.type = 'hidden';
        monthInput.name = 'monthly_budget_id';
        monthInput.value = monthId;
        form.appendChild(monthInput);

        selectedIds.forEach(id => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'transaction_ids';
            input.value = id;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    });
}
