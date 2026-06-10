# DualSpendCalculator

## プロジェクト概要

**DualSpendCalculator** は、同棲カップルの共同生活費を **収入比で按分**し、月次の **立替精算額** を算出する Django Web アプリです。

### 解決する課題

- クレジットカード明細 CSV を取り込み、生活費対象の明細を整理する
- 2 人の月収から負担割合を自動計算する
- 「誰がいくら立て替えたか」と「本来負担すべき額」の差分から精算額を出す
- 選択した明細について、収入比に基づく **家事按分同意書 PDF** を生成する

### ドメインモデル

- `MonthlyBudget`（月次予算）: 対象月 `year_month`、ユーザー A/B、各月収
- `Transaction`（取引明細）: 日付・摘要・金額・生活費フラグ・支払者・カテゴリ


## コアロジック

収入比で生活費の**負担額**を出し、**立替過不足**を精算する。

1. `ratio` = 各月収 / 合計収入（小数第 4 位）
2. `share` = 生活費合計 × `ratio`（円・四捨五入）
3. `settlement` = `paid_a` − `share_a`（正→B→A、負→A→B、0→不要）

**例**（収入 30万:20万、生活費 3万円、A 立替 1.3万円）→ A は 1.8万円負担 → **A が B に 5,000 円**

収入未入力・合計 0 は割合なし。支払者未設定は警告。金額は `Decimal` / `ROUND_HALF_UP`。

| 順 | ファイル | 役割 |
|----|----------|------|
| 1 | `budgets/domain/ratios.py` | 割合・負担額 |
| 2 | `budgets/services/settlement.py` | 合計・立替・精算 |
| 3 | `tests/budgets/test_domain_ratios.py`, `test_settlement.py` | 検証 |

同意書 PDF・CSV 取込は同じ按分ロジック / パース＋重複排除（`agreement.py`, `csv_import/`）。

## アーキテクチャ

`View` → `Service` → `domain/ratios.py`（計算） / ORM（明細集計）。CSV のみ Protocol → Adapter。

- 計算は ORM 非依存
- 精算と同意書で按分関数を共有
- CSV はポート/アダプター分離

## ディレクトリ構成

`dualspendcalculator/` は Django アプリ本体です。機能ごとにフォルダが分かれています。

| フォルダ | 役割（一言） |
|----------|-------------|
| `config/` | 設定・URL の入口（どの URL がどの画面につながるか） |
| `common/` | 全アプリ共通の小さな道具（環境変数の読み取り、文字コード判定など） |
| `budgets/` | **月と収入の管理・精算計算・同意書 PDF**（このアプリの中心） |
| `transactions/` | **カード明細の表示・編集・一括操作**（生活費フラグ・支払者の付け替え） |
| `csv_import/` | **クレジットカードデータ(CSV)の取込**（読み取り → 重複チェック → DB 保存） |
| `static/` | 全画面共通の CSS とログイン画面などのベーステンプレート |

### `budgets/` の中身

| フォルダ / ファイル | 役割 |
|--------------------|------|
| `domain/` | 収入比・負担額の計算だけを書いた場所（DB に触れない純粋なロジック） |
| `services/` | 精算・同意書 PDF など「やりたいこと」を実現する処理 |
| `presenters/` | 画面に渡す数字・文言の組み立て |
| `models.py` | 月次予算（`MonthlyBudget`）の定義 |
| `views.py` / `forms.py` | 画面の表示・入力受付 |
| `templates/` | ダッシュボード・月一覧・月詳細・同意書の HTML |
| `static/budgets/js/` | 月詳細画面の Ajax 一括操作 |

### `transactions/` の中身

| フォルダ / ファイル | 役割 |
|--------------------|------|
| `models.py` | 取引明細（`Transaction`）の定義 |
| `services/` | 明細の一括更新（生活費から外す・支払者を設定する） |
| `presenters/` | 明細一覧ブロックの表示データ組み立て |
| `templates/` | 明細編集画面・一覧の部分テンプレート |

### `csv_import/` の中身

| フォルダ / ファイル | 役割 |
|--------------------|------|
| `services/` | CSV の1行ずつの読み取りと取込処理 |
| `ports.py` / `adapters.py` | 取込処理と DB のつなぎ方を分離（テストしやすくするため） |
| `presenters/` | アップロード欄の表示データ組み立て |
| `views.py` / `forms.py` | CSV アップロード画面 |

**読む順の目安**: `budgets/domain/` → `budgets/services/` → `transactions/models.py` → `csv_import/services/`

## 技術スタック

| 層 | 技術 |
|----|------|
| 言語 / FW | Python 3.11, Django 5.x |
| DB | PostgreSQL 16 |
| PDF | WeasyPrint |
| テスト | pytest, pytest-django |
| インフラ | Docker Compose |
| フロント | Django テンプレート + 素の JavaScript（Ajax 一括操作） |

金額計算は `Decimal` を使用し、`float` は使いません。

## テストの読み方

```bash
# Docker 内で全テスト実行
docker compose exec web pytest

# ドメインロジックのみ（計算の精査に最適）
docker compose exec web pytest tests/budgets/test_domain_ratios.py tests/budgets/test_settlement.py -v

# CSV パーサのみ
docker compose exec web pytest tests/csv_import/ -v
```

### テスト構成

| ディレクトリ | 検証対象 |
|-------------|----------|
| `tests/budgets/` | 精算・按分・Presenter・View |
| `tests/transactions/` | 一括操作・明細表示 |
| `tests/csv_import/` | エポス CSV パーサ |
| `tests/common/` | 環境変数ユーティリティ |

### テスト設計の特徴

- `conftest.py` で `user_a` / `user_b` / `monthly_budget` / `transaction` フィクスチャを共通化
- 計算ロジックは Arrange-Act-Assert 形式で、docstring にテスト ID（T-xxx）を記載
- 金額計算は `Decimal` を使用（`float` 不使用）

## ローカル起動

リポジトリルートで実行します。Docker と Compose v2 が必要です。

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

ブラウザで `http://localhost:8000/` を開き、ログイン画面が表示されれば起動完了です。
