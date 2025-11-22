# py-pomo

[English](README.md) | **日本語**

`py-pomo` は Python 向けのシンプルで厳密型付け（strict typing）な gettext 互換の国際化ライブラリです。

`.po` ファイルを自前でパースし、外部依存なしで `gettext()` / `ngettext()` を使用できるようにします。

---

## 特長

- ✔ `.po` ファイルをパース（gettext 形式）
- ✔ `Plural-Forms:` を解析し、複雑な複数形ルールに対応
- ✔ mypy / Pylance 完全対応（strict モード）
- ✔ gettext 互換 API `gettext` / `ngettext` / `translation`
- ✔ OS 依存なし（libintl 不要）
- ✔ Linux / macOS / Windows で動作

MSM（MangaSeitonMaid）や Kuraban backend といった
Python 製プロジェクトへの組み込みを想定しています。

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
- ヘッダー（`msgid ""`）の解析 -> ここから `Plural-Forms:` を抽出

---

## プロラルフォーム（複数形ルール）

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
