# HomeBudgetApp

このリポジトリは、家計簿アプリケーションのソースコードを管理しています。アプリ本体は **PMF（Product-Market Fit）達成後版**として、実際に使用する本番環境と再利用可能なアーキテクチャを目指しています。

## 📁 ディレクトリ構成

```
HomeBudgetApp/
├── home_budget/          # Django プロジェクト（PMF達成後版アーキテクチャ）
│   ├── common/           # 共通基盤
│   ├── budgets/          # 予算・精算
│   ├── transactions/     # 取引明細
│   └── csv_import/       # CSVインポート
├── compose.yaml
├── Dockerfile
├── requirements.txt
├── libs/                 # 共通ライブラリ（予定）
└── docs/                 # ドキュメント（予定）
```

## 📁 アーキテクチャ

**4アプリ構造**:

| アプリ | 責務 | 依存関係 |
|--------|------|---------|
| `common` | 共通ユーティリティ（text, env） | なし（最も安定） |
| `budgets` | 月次予算管理 + 精算ダッシュボード | common |
| `transactions` | 取引明細管理 | common, budgets |
| `csv_import` | CSVインポート機能 | common, transactions |

**設計判断**:
- `common`: 共通コードを格納（安定依存の原則）
- `accounts`: 削除 → 認証URLを `config/urls.py` に統合
- `settlements`: 削除 → `budgets` アプリに統合

## 🏗️ 適用した設計原則

| 原則 | 適用内容 |
|------|---------|
| **DIP（依存性逆転）** | Protocol で抽象を定義、アダプターで実装 |
| **SDP（安定依存）** | common が最も安定、他が依存 |
| **CCP（共通閉鎖）** | 同じ理由で変更されるコードを同じアプリに |
| **ポートとアダプター** | 外部連携を差し替え可能に |

## 📂 ディレクトリ構造（home_budget）

```
home_budget/
├── common/                 # 共通ユーティリティ
│   ├── text/               # テキスト処理
│   │   ├── encoding.py     # 文字コード判定
│   │   └── parsing.py      # 日付・金額パース
│   └── env.py              # 環境変数の解釈
│
├── budgets/                # 月次予算
│   ├── services/           # ビジネスロジック
│   ├── static/budgets/     # 画面専用 JS など
│   └── templates/budgets/  # アプリ固有テンプレート
│
├── transactions/           # 取引明細
│   └── templates/transactions/
│
├── csv_import/             # CSVインポート
│   ├── ports.py            # Protocol 定義
│   ├── adapters.py         # Django ORM 実装
│   └── services/           # 取込サービス・パーサ・結果 DTO
│
├── static/                 # 共通静的ファイル（CSS など）
└── templates/              # 共通テンプレート（base.html など）
```

### テンプレート・静的ファイルの配置

| 種別 | 置き場 | 例 |
|------|--------|-----|
| 共通テンプレート | `home_budget/templates/` | `base.html`, `registration/login.html` |
| アプリ固有テンプレート | `<app>/templates/<app>/` | `budgets/templates/budgets/month_detail.html` |
| 共通静的ファイル | `home_budget/static/` | `css/style.css` |
| 画面専用 JS | その画面を持つアプリの `<app>/static/<app>/` | `budgets/static/budgets/js/month_detail.js` |

## 🚀 起動方法

Docker と環境ファイルはリポジトリ直下にあります。手順はリポジトリのルート（`HomeBudgetApp/`）をカレントにして実行します。

### 1. 環境ファイルを作成（初回のみ）

```bash
cp env.example env
```

### 2. コンテナを起動

```bash
docker compose up --build -d
```

### 3. 初期化（初回のみ）

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

> **📌 補足**: マイグレーションとユーザー作成は**初回のみ**必要です。  
> データは Docker ボリュームに永続化されるため、2回目以降の起動では不要です。

### 4. 動作確認

ブラウザで `http://localhost:8000/` にアクセスしてください（ホスト側ポートを変えた場合はその番号に読み替えてください）。ログイン画面が表示されれば起動成功です。

### ポート 8000 が既に使われている場合

`Bind for 0.0.0.0:8000 failed: port is already allocated` は、**別のコンテナやプロセスがすでにホストの 8000 番を掴んでいる**ときに出ます。リネーム前のスタック（例: `homebudget_pmf_web`）が残っているケースが多いです。

1. `docker ps` で `0.0.0.0:8000->8000/tcp` のコンテナを確認し、`docker stop <コンテナ名>` で止めるか、旧プロジェクトのディレクトリで `docker compose down` を実行する。
2. 止められない・両方動かしたい場合は、ホスト側だけ別ポートを指定して起動する。

```bash
HOST_WEB_PORT=8001 docker compose up --build -d
```

このときブラウザでは `http://localhost:8001/` を開きます。`compose.yaml` の `${HOST_WEB_PORT:-8000}` は、シェルの環境変数または同じディレクトリの `.env`（Compose が読むファイル）から解決されます。

## 🔍 確認コマンド

```bash
# コンテナの状態確認
docker compose ps

# ログ確認
docker compose logs web --tail 50

# コンテナ停止（データは保持）
docker compose down

# コンテナ停止 + ボリューム削除（データも削除）
docker compose down -v
```

## テストの実行方法

テストは **`home_budget/`** をカレントにして実行します（仮想環境はリポジトリ直下の `.venv` を想定）。

### 1. 仮想環境の準備（初回のみ）

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. テストの実行

```bash
cd home_budget
../.venv/bin/python -m pytest -v
```

- 上記コマンドで **`test/` 配下の全テスト**（精算・同意書・conftest 確認を含む）が実行される（`pytest.ini` の `testpaths = test`）
- マーカー付きテストのみ: `../.venv/bin/python -m pytest -m slow -v`
- 仮想環境を有効化してから実行する場合:
  ```bash
  source .venv/bin/activate && cd home_budget && pytest -v
  ```

**DB を使うテスト**（`@pytest.mark.django_db` 付き）を実行する場合は、先にリポジトリ直下で `docker compose up -d` により DB を起動するか、`DATABASE_URL` をローカル用に設定してください。

## デプロイ・運用の予定

現在は localhost + Docker で開発しています。開発が一区切りしたら、Tailscale によるプライベートネットワークへ切り替え、スマホ等からも安全にアクセスできるようにする予定です。詳細は [docs/whole_flow/2026-03-14_deployment_plan.md](docs/whole_flow/2026-03-14_deployment_plan.md) を参照してください。

## 📝 特徴

- **再利用可能**: csv_import は別プロジェクトで再利用可能
- **テスト容易**: アダプターをモックに差し替え可能
- **明確な責務分離**: 各アプリの責務が明確

## 🔌 再利用方法

別プロジェクトで csv_import を使う場合：

```python
# my_project/adapters.py
from csv_import.ports import TransactionRepository

class MyRepository:
    def exists_by_hash(self, h): ...
    def create(self, data, h): ...
    def generate_hash(self, d, desc, amt): ...

# 使用
from csv_import.services import CSVImportService
repository = MyRepository()
service = CSVImportService(repository)
```
