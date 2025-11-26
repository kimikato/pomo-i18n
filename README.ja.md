# py-pomo

[English](README.md) | **日本語**

`py-pomo` は Python 向けのシンプルで厳密型付け（strict typing）な gettext 互換の国際化ライブラリです。

`.po` ファイルを自前でパースし、外部依存なしで `gettext()` / `ngettext()` を使用できるようにします。

---

## 特長

- ✔ `.po` ファイルをパース（gettext 形式）
- ✔ 複数形ルール（`Plural-Forms:`） を解析し、複雑な複数形ルールに対応
- ✔ mypy / Pylance 完全対応（strict モード）
- ✔ gettext 互換 API `gettext` / `ngettext` / `translation`
- ✔ OS 依存なし（libintl 不要）
- ✔ Linux / macOS / Windows で動作

CLI ツールや API サーバ、バッチ処理など
Python プロジェクトへの組み込みを想定しています。

---

## インストール

```sh
pip install py-pomo
```

もしくは `src/` 内に同梱して使用することもできます。

```
src/
 └─ pypomo/
```

---

## クイックスタート

```python
from pypomo.gettext import translation

t = translation(
    domain="messages",
    localedir="locales",
    languages=["ja"],
)

_ = t.gettext

print(_("Hello"))                     # -> 「こんにちは」等
print(t.ngettext("apple", "apples", 1))   # -> 「りんご」
print(t.ngettext("apple", "apples", 3))   # -> 「りんご」(日本語は単数のみ)
```

フォルダ構成例：

```
locales/
 └─ ja/
     └─ LC_MESSAGES/
         └─ messages.po
```

---

## `.po` の解析

`py-pomo` の POParser は、gettext の基本要素をサポートします：

- `msgid` / `msgstr`
- 複数形：`msgid_plural` / `msgstr[n]`
- 複数行文字列
- コメント（`#`, `#.`, `#:`, `#,` など）
- ヘッダー（`msgid ""`）の解析 -> ここから 複数形ルール（`Plural-Forms:`） を抽出

---

## 複数形ルール（Plural Forms）

`.po` には次のような行が含まれます：

```python
Plural-Forms: nplurals=2; plural=(n != 1);
```

ロシア語の例：

```python
Plural-Forms: nplurals=3;
 plural=(n%10==1 && n%100!=11 ? 0 :
        n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
```

`py-pomo` は C 風構文（`&&` / `||` / `? :`）を Python 構文に変換し、制限付き `eval()` で安全に評価します。

---

## API リファレンス

### Catalog

```python
from pypomo.catalog import Catalog
```

| メソッド                        | 説明                        |
| ------------------------------- | --------------------------- |
| `gettext(msgid)`                | 単純翻訳                    |
| `ngettext(singular, plural, n)` | 複数形に対応した翻訳        |
| `bulk_update(messages)`         | メッセージ辞書のマージ      |
| `from_po_entries(entries)`      | POEntry から Catalog を構築 |

---

### トップレベル API

```python
from pypomo.gettext import gettext, ngettext, translation
```

| 関数                                        | 説明                                       |
| ------------------------------------------- | ------------------------------------------ |
| `gettext(msgid)`                            | デフォルトカタログでの翻訳                 |
| `ngettext(singular, plural, n)`             | 複数形を考慮した翻訳                       |
| `translation(domain, localedir, languages)` | 特定の .po を読み込んで新規 Catalog を返す |

---

## ベンチマーク

2 種類のベンチマークがあります:

### 1. Micro benchmark (timeit)

```sh
make bench
```

### 2. pytest-benchmark

```sh
make bench-pytest
```

### 🏎 複数形評価（Plural Expression） ベンチマーク

複数形選択（plural rule evaluation）は gettext の内部処理で最も頻繁に実行されるため、
キャッシュ方式によりパフォーマンスが大きく変わります。
以下は実際のベンチマーク結果です。

#### 計測環境

- Python 3.10
- macOS Tahoe 26.1 (Apple Silicon, M4)
- pytest-benchmark
- pypomo default settings

#### キャッシュ方式ごとの比較結果

| Backend  | Simple Rule (µs) | Complex Rule (µs) | コメント                              |
| -------- | ---------------- | ----------------- | ------------------------------------- |
| **none** | 約 2.54          | 約 4.83           | キャッシュなし。デバッグ向け。        |
| **weak** | 約 2.69          | 約 4.89           | Python の dict による簡易キャッシュ。 |
| **lru**  | 約 2.49          | 約 4.92           | もっとも高速（CPython の LRU 実装）。 |

#### まとめ

- 本番利用では **`LRU` キャッシュを推奨**
- `weak` は軽量キャッシュとして扱いやすい
- `none` は比較実験やデバッグ用途に最適

#### キャッシュ方式の切り替え方法

環境変数でキャッシュ backend を切り替えできます：

```bash
# キャッシュ無効化（デバッグ向け）
export PYPOMO_CACHE=none

# dict ベースの簡易キャッシュ
export PYPOMO_CACHE=weak

# LRU キャッシュ（推奨）
export PYPOMO_CACHE=lru

# LRU サイズ変更（デフォルト: 256）
export PYPOMO_PLURAL_CACHE_SIZE=512
```

プログラム中で切り替えることも可能です：

```python
from pypomo.utils.cache_manager import get_default_cache
cache = get_default_cache(backend="lru")
```

---

## 今後の予定

- `.mo` バイナリファイルの読み込み
- 複数言語のフォールバック対応
- コメント（`#, fuzzy`、`#.` など）の強化
- `.pot` の自動生成ツール
- CLI ツールの提供

---

## ライセンス

MIT License
© 2025 Kiminori Kato

---
