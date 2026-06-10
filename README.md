# DualSpendCalculator

家計簿アプリケーションのソースコードを管理するリポジトリです。
この README は、**Docker のみ**でローカル環境を起動し、ブラウザでログイン画面を確認できるところまでを再現する手順書です。

## 前提条件

| 項目 | 要件 |
|------|------|
| Docker | Docker Desktop、または Docker Engine + Compose v2 |
| Compose コマンド | `docker compose`（`docker-compose` ではない） |
| 空きポート | デフォルト `8000`（`.env` で変更可能） |
| OS | macOS / Linux / Windows（WSL2 推奨） |

セットアップ前に、次のコマンドが通ることを確認してください。

```bash
docker --version
docker compose version
```

## クイックスタート（初回セットアップ）

以下のコマンドは、すべて**リポジトリルート**（`DualSpendCalculator/`）で実行します。

### 1. リポジトリを取得

```bash
git clone <repository-url>
cd DualSpendCalculator
```

### 2. 環境変数ファイルを作成

```bash
cp .env.example .env
```

`.env` は git 管理外です。秘密情報やポート番号の変更は `.env` に記述します。

`.env` は次の 2 用途で使われます。

- Docker Compose の変数置換（`${HOST_WEB_PORT}` など）
- `web` コンテナへの環境変数注入（`env_file`）

### 3. コンテナをビルド・起動

```bash
docker compose up --build -d
```

**成功の目安**: `docker compose ps` で `web` と `db` の STATUS が `Up` になる。

```bash
docker compose ps
```

想定されるコンテナ名:

| サービス | コンテナ名 |
|----------|-----------|
| Django（web） | `dualspendcalculator_web` |
| PostgreSQL（db） | `dualspendcalculator_db` |

### 4. DB マイグレーション（初回のみ）

```bash
docker compose exec web python manage.py migrate
```

**成功の目安**: `Applying ... OK` が表示される。

### 5. 管理者ユーザーを作成（初回のみ）

```bash
docker compose exec web python manage.py createsuperuser
```

対話形式でユーザー名・メールアドレス・パスワードを入力します。

### 6. 動作確認

ブラウザで次の URL を開きます。

```
http://localhost:8000/
```

**成功の目安**: ログイン画面が表示される。

## 2 回目以降の起動

```bash
docker compose up -d
```

マイグレーションと管理者ユーザー作成は不要です。PostgreSQL のデータは Docker ボリューム `dualspendcalculator_postgres_data` に永続化されます。

## 環境変数リファレンス

`.env.example` をコピーした `.env` で設定します。

| 変数名 | デフォルト | 用途 |
|--------|-----------|------|
| `HOST_WEB_PORT` | `8000` | ホスト側の公開ポート |
| `DJANGO_SECRET_KEY` | `django-insecure-change-me` | Django 秘密鍵（本番では必ず変更） |
| `DJANGO_DEBUG` | `1` | デバッグモード（`1` = 有効） |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | 許可ホスト（カンマ区切り） |
| `POSTGRES_DB` | `dualspendcalculator` | DB 名（`db` コンテナの初期化に使用） |
| `POSTGRES_USER` | `dualspendcalculator` | DB ユーザー |
| `POSTGRES_PASSWORD` | `dualspendcalculator` | DB パスワード |
| `DATABASE_URL` | `postgresql://dualspendcalculator:dualspendcalculator@db:5432/dualspendcalculator` | `web` コンテナの DB 接続先 |

`DATABASE_URL` のホスト名は `db`（Compose のサービス名）です。`localhost` ではありません。

## よく使うコマンド

リポジトリルートで実行します。

```bash
# コンテナの状態確認
docker compose ps

# web コンテナのログ確認（直近 50 行）
docker compose logs web --tail 50

# db コンテナのログ確認（直近 50 行）
docker compose logs db --tail 50

# コンテナ停止（データは保持）
docker compose down

# コンテナ停止 + ボリューム削除（DB データも削除）
docker compose down -v
```

`docker compose down -v` は DB データを完全に消去します。初回セットアップからやり直す場合にのみ使用してください。

## トラブルシューティング

### ポート 8000 が既に使われている

`Bind for 0.0.0.0:8000 failed: port is already allocated` は、別のコンテナやプロセスがホストの 8000 番ポートを使用しているときに発生します。

**対処 1**: 競合しているコンテナを停止する。

```bash
docker ps
docker stop <コンテナ名>
```

**対処 2**: ホスト側ポートを変更して起動する。

`.env` を編集:

```
HOST_WEB_PORT=8001
```

または、一時的に環境変数を指定:

```bash
HOST_WEB_PORT=8001 docker compose up --build -d
```

この場合、ブラウザでは `http://localhost:8001/` を開きます。

### コンテナが起動しない

```bash
docker compose logs web
docker compose logs db
```

`.env` がリポジトリルートに存在するか確認してください（`cp .env.example .env`）。

### DB 接続エラー

1. `docker compose ps` で `db` が `Up` であることを確認する。
2. `.env` の `DATABASE_URL` と `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` が整合していることを確認する。

### ログイン画面は出るが操作でエラーになる

マイグレーション未実行の可能性があります。

```bash
docker compose exec web python manage.py migrate
```

### 管理者ユーザーでログインできない

`createsuperuser` が未実行、または別ユーザーで作成した可能性があります。

```bash
docker compose exec web python manage.py createsuperuser
```
