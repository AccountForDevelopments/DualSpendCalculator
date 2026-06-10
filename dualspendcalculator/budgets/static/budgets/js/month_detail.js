/**
 * 月次詳細画面用JavaScript
 *
 * 機能:
 * - 一括選択（全選択/個別選択）
 * - 支払者の一括設定（Ajax）
 * - 同意書ダウンロード
 */

document.addEventListener('DOMContentLoaded', function() {
    initSelectAll();
    initBulkPayerActions();
    initAgreementButton();
});

const EMPTY_SELECTION_TITLE = '1件以上選択してください';

/**
 * 選択件数表示と一括操作ボタンの有効/無効を同期する
 */
function updateSelectedCount() {
    const count = document.querySelectorAll('.select-row:checked').length;
    const isEmpty = count === 0;
    const selectedCount = document.querySelector('.selected-count');
    const bulkActions = document.querySelector('.bulk-actions');

    if (selectedCount) {
        selectedCount.textContent = count + '件選択中';
    }

    document.querySelectorAll('.bulk-action-btn').forEach(btn => {
        btn.disabled = isEmpty;
        btn.title = isEmpty ? EMPTY_SELECTION_TITLE : '';
    });

    if (bulkActions) {
        bulkActions.classList.toggle('bulk-actions--inactive', isEmpty);
    }
}

/**
 * すべての行チェックと全選択チェックを外す
 */
function clearSelectedRows() {
    document.querySelectorAll('.select-row:checked').forEach(cb => {
        cb.checked = false;
    });
    const selectAll = document.getElementById('select-all');
    if (selectAll) {
        selectAll.checked = false;
    }
    updateSelectedCount();
}

/**
 * 一括選択機能を初期化する
 */
function initSelectAll() {
    const selectAll = document.getElementById('select-all');
    const selectRows = document.querySelectorAll('.select-row');

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
 * 支払者一括設定を Ajax で実行する
 */
function initBulkPayerActions() {
    const form = document.getElementById('bulk-form');
    if (!form) return;

    const payerButtons = document.querySelectorAll('.bulk-payer-btn');
    if (payerButtons.length === 0) return;

    payerButtons.forEach(btn => {
        btn.addEventListener('click', async function() {
            if (btn.disabled) return;

            const action = btn.dataset.action;
            const selectedIds = getSelectedTransactionIds();
            if (selectedIds.length === 0) return;

            await submitPayerAction(form, action, selectedIds);
        });
    });
}

/**
 * 選択中の Transaction ID を取得する
 */
function getSelectedTransactionIds() {
    return [...document.querySelectorAll('.select-row:checked')].map(cb => cb.value);
}

/**
 * 支払者一括設定を POST し、該当行のバッジを更新する
 */
async function submitPayerAction(form, action, selectedIds) {
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    const bulkButtons = document.querySelectorAll('.bulk-action-btn');
    const formData = new FormData();
    formData.append('action', action);
    selectedIds.forEach(id => formData.append('selected', id));
    const filterParams = form.querySelector('[name=filter_params]');
    if (filterParams) {
        formData.append('filter_params', filterParams.value);
    }

    bulkButtons.forEach(btn => { btn.disabled = true; });

    const bulkActionUrl = form.getAttribute('action');

    try {
        const response = await fetch(bulkActionUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData,
        });

        const data = await response.json();
        showBulkToast(data.level, data.message);

        if (data.level === 'success' && data.updated) {
            data.updated.forEach(item => {
                updatePayerCell(item.id, item.payer_username);
            });
            clearSelectedRows();
        }
    } catch {
        showBulkToast('error', '通信エラーが発生しました。再度お試しください。');
    } finally {
        updateSelectedCount();
    }
}

/**
 * 支払者セルのバッジを更新する
 */
function updatePayerCell(txId, payerUsername) {
    const row = document.querySelector(`tr[data-tx-id="${txId}"]`);
    if (!row) return;

    const cell = row.querySelector('.cell-payer');
    if (!cell) return;

    if (payerUsername) {
        cell.innerHTML = `<span class="badge badge-payer">${escapeHtml(payerUsername)}</span>`;
    } else {
        cell.innerHTML = '<span class="badge badge-warning">未設定</span>';
    }
}

/**
 * 一括操作バーにフィードバックメッセージを表示する
 */
function showBulkToast(level, message) {
    const bulkActions = document.querySelector('.bulk-actions');
    if (!bulkActions) return;

    const existing = bulkActions.querySelector('.bulk-toast');
    if (existing) existing.remove();

    const toastLevel = level === 'error' ? 'error' : level;
    const toast = document.createElement('div');
    toast.className = `bulk-toast bulk-toast--${toastLevel}`;
    toast.textContent = message;
    toast.setAttribute('role', 'status');
    bulkActions.insertBefore(toast, bulkActions.firstChild);

    setTimeout(() => toast.remove(), 4000);
}

/**
 * HTML エスケープ（バッジ表示用）
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 同意書ダウンロードボタンを初期化する
 * 選択されたTransaction IDと monthly_budget_id を動的フォームでPOST送信する
 */
function initAgreementButton() {
    const btn = document.getElementById('btn-agreement');
    if (!btn) return;

    btn.addEventListener('click', function() {
        const selectedIds = getSelectedTransactionIds();
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
