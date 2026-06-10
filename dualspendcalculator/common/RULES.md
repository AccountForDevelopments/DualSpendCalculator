# common/ 配置ルール

このドキュメントは `common/` アプリに何を配置して良いか、何を配置してはいけないかを定義する。

---

## 📁 ディレクトリ構造

```
common/
├── text/           # テキスト処理（純粋関数）
│   ├── encoding.py # 文字コード判定
│   └── parsing.py  # 日付・金額パース
├── env.py          # 環境変数文字列の解釈（純粋関数）
└── RULES.md        # このファイル
```

---

## ✅ 入れて良いもの

| 種類 | 配置先 | 例 |
|------|--------|-----|
| 純粋関数（副作用なし） | `text/` | `parse_date()`, `detect_encoding()` |
| 環境変数の解釈 | `env.py` | `env_bool()`, `env_str()` |
| 型定義、Protocol | 新規 `types/` | 将来追加可能 |
| バリデーター | 新規 `validators/` | 将来追加可能 |

---

## ❌ 入れてはいけないもの

| 種類 | 理由 | 配置先 |
|------|------|--------|
| ビジネスロジック | ドメイン固有 | 各アプリの `services/` |
| モデル定義 | ドメイン固有 | 各アプリの `models.py` |
| 特定アプリ専用コード | 再利用されない | そのアプリ内 |
| 設定値そのもの | 設定層に属する | `config/settings.py` |
| ビューミックスイン | Django 依存・各ビューで明示がよい | 各アプリの `views.py` 等 |
| 外部API呼び出し | 変更頻度が高い | 専用アプリ（例: 決済連携アプリ） |
| テンプレート | プレゼンテーション層 | `templates/` |

---

## 🔍 判断フローチャート

```
このコードを common/ に入れるべき？

1. 「2つ以上のアプリで使う？」
   └── No → そのアプリに配置
   └── Yes → 次へ

2. 「ビジネスルールを含む？」
   └── Yes → ドメインアプリの services/ に配置
   └── No → 次へ

3. 「外部サービスに依存する？」
   └── Yes → 専用アプリに配置（csv_import など）
   └── No → 次へ

4. 「Django に依存する？」
   └── Yes → common には入れない（各アプリの views 等）
   └── No → common/text/ または env.py 等に配置
```

---

## 📝 新しいサブモジュールを追加する場合

1. 責務が明確であること
2. 既存のサブモジュールと重複しないこと
3. このファイル（RULES.md）を更新すること

### 追加候補の例

| モジュール | 用途 |
|-----------|------|
| `validators/` | 共通バリデーター |
| `types/` | 型定義、Protocol、データクラス |
| `formatters/` | 出力フォーマット |

---

## 🚫 アンチパターン

### ❌ utils.py に何でも入れる

```python
# BAD: 責務が不明確
# common/utils.py に500行のコードがある
```

### ❌ 巨大なミックスイン

```python
# BAD: 責務が多すぎる
class GodMixin(LoginRequiredMixin, PermissionMixin, MessageMixin, ...):
    pass
```

### ❌ ビジネスロジックを common に入れる

```python
# BAD: これは budgets アプリに属すべき
def calculate_settlement(month):
    ...
```

---

**最終更新**: 2026-06-04
