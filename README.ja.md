# pomo-i18n

[English](README.md) | **日本語**

![Tests](https://github.com/kimikato/pomo-i18n/actions/workflows/tests.yml/badge.svg?branch=main)
[![coverage](https://img.shields.io/codecov/c/github/kimikato/pomo-i18n/main?label=coverage&logo=codecov)](https://codecov.io/gh/kimikato/pomo-i18n)
[![PyPI version](https://img.shields.io/pypi/v/pomo-i18n.svg)](https://pypi.org/project/pomo-i18n/)
[![Python](https://img.shields.io/pypi/pyversions/pomo-i18n.svg)](https://pypi.org/project/pomo-i18n/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**pomo-i18n** は、GNU gettext 翻訳データを扱うための軽量な Python ライブラリです。
実用的で明示的な `Catalog` モデルを中心に設計されています。

バージョン 0.2.0 では、**gettext 互換** かつ **インメモリ** な翻訳カタログを提供し、**dict-like API** を通じて、従来の gettext ワークフロー (`.po`, `.mo`, `gettext()`, `ngettext()`)との互換性を保ちます。

---

## 概要

`pomo-i18n` は、以下のような開発者を対象に設計されています。

- グローバル状態に依存せずに、 gettext 翻訳データを扱いたい
- 翻訳を **明示的な Python オブジェクト** として管理したい
- gettext 互換の挙動を保ちつつ、Python らしい API を使いたい

本ライブラリの中核となるのが `Catalog` クラスです。
`Catalog` は gettext メッセージカタログを **インメモリで表現** します。

`Catalog` は次の特徴を持ちます。

- `msgid` をキーとしてメッセージを管理
- ヘッダ (`msgid == ""`) をファーストクラスデータとして扱う
- gettext セマンティクスに準拠した dict-like API
- 複数形ルールの解析・評価・キャッシュのサポート
- `.po` / `.mo` ファイルからの読み込み、および `.mo` への書き出しが可能

標準の `gettext` モジュールと異なり、`pomo-i18n` は
モジュールレベルのグローバル状態に翻訳データを隠しません。

すべての翻訳データは明示的な `Catalog` インスタンスとして保持されるため、
挙動は予測可能で、テストしやすく、合成可能です。

---

## 対象外・スコープ

`pomo-i18n` は **明示的なインメモリ gettext カタログ** にフォーカスしています。

以下の機能は意図的に提供しません。

- グローバルな翻訳状態
- 自動的な言語切り替え
- フレームワーク固有の統合 (Django, Flask など)

これらは `Catalog` を基盤として、上位レイヤで構築されることを想定します。

---

## gettext 互換性

`pomo-i18n` は、重要な点において **GNU gettext と互換の挙動**を目指しています。

- 翻訳が存在しない場合は、`msgid` にフォールバック
- ヘッダの扱いは gettext の仕様に準拠
- `gettext()` / `ngettext()` API を提供
- 複数形ルールは gettext 仕様に基づいて評価

同時に、これらの概念を **明確なオブジェクトモデル** として公開することで、
翻訳データを直接検査・操作できるようにしています。

---

## インストール

```bash
pip install pomo-i18n
```

要件:

- Python 3.10 以上

### GNU gettext 依存について

`pomo-i18n` は実行時に GNU gettext を必要としません。
必要なのは Python のみです。

`.mo` ファイルの読み込み、複数形ルールの評価、
`gettext()` / `ngettext()` の実行はすべて Python だけで完結します。

そのため、GNU gettext ツールチェインを導入しづらい Windows 環境でも
問題なく利用できます。

`.po` ファイルは現在インポート形式としてサポートしています。
`.po` → `.mo` の完全な変換サポートは、将来のバージョンで予定されています。

---

## クイックスタート

`pomo-i18n` の中心となるオブジェクトは `Catalog` です。

`Catalog` は gettext メッセージカタログをインメモリで表現し、
Python の辞書に近い感覚で扱うことができます。

---

### `Catalog` を作成する

```python
from pypomo.catalog import Catalog

catalog = Catalog()
```

---

### dict-like API の基本

辞書と同様の構文で翻訳を登録・取得できます。

```python
catalog["hello"] = "こんにちは"

print(catalog["hello"])
# -> "こんにちは"
```

翻訳が存在しない場合は、`msgid` 自体が返されます。(gettext 互換の挙動です)

```python
print(catalog["missing"])
# -> "missing"
```

---

### ヘッダの扱い (`msgid == ""`)

gettext のヘッダはファーストクラスデータとして扱われます。

```python
catalog[""] = (
    "Language: ja\n"
    "Plural-Forms: nplurals=2; plural=(n != 1);\n"
)
```

ヘッダに含まれる Plural-Forms は自動的に解析され、複数形評価に使用されます。

---

### get() を使った取得

`Catalog.get()` は `dict.get()` に似た挙動をしますが、
gettext 互換のフォールバックを持ちます。

```python
catalog.get("hello")
# -> CatalogMessage

catalog.get("missing")
# -> "missing"

catalog.get("missing", "fallback")
# -> "fallback"
```

- キーが存在する場合は `CatalogMessage` を返します
- キーが存在しない場合は `default` または、`msgid` を返します

---

### gettext / ngettext API

`Catalog` は gettext 互換の API を提供します。

```python
catalog.gettext("hello")
# -> "こんにちは"

catalog.ngettext("apple", "apples", 1)
# -> "apple"

catalog.ngettext("apple", "apples", 2)
# -> "apples"
```

- `gettext()` は単数形の取得に使用されます
- `ngettext()` は複数形ルールに基づいて翻訳を選択します

---

### `.po` / `.mo` の読み込みと書き出し

`Catalog` は `.po` および `.mo` ファイルから生成でき、
`.mo` ファイルとして書き出すことができます。

```python
from pypomo.mo.loader import load_mo
from pypomo.mo.writer import write_mo

catalog = load_mo("messages.mo")
write_mo("messages_out.mo", catalog)
```

`.mo` ファイルは実行時の利用に推奨される形式です。
詳細は後続のセクションを参照してください。

---

## 設計思想：なぜ `Catalog` なのか？

`pomo-i18n` の設計は、次の 1 つの原則に基づいています。

**GNU gettext 互換性を保ちつつ、隠れたグローバル状態を排除する**

### 標準 gettext モジュールの課題

Python 標準の gettext モジュールは強力ですが、
現代的な Python アプリケーションにおいてはいくつかの課題があります。

- 翻訳状態がモジュールレベルのグローバル状態として管理される
- 使用中の言語やドメインが暗黙的になりやすい
- テスト時にグローバル状態の差し替えが必要になる
- 翻訳データの中身を直接確認・操作しづらい

これらは次のようなケースで問題になります。

- 明示的な依存関係を重視する設計
- 複数の翻訳カタログを同時に扱う必要がある場合
- 再現性・テスト容易性が重要な環境

---

### 明示的な翻訳オブジェクトとしての `Catalog`

`pomo-i18n` は、これらの課題に対し、翻訳状態をすべて明示的なオブジェクトとして扱うという方針を取ります。

`Catalog` は次のような存在です。

- 実体を持つ、検査可能な Python オブジェクト
- gettext メッセージカタログのインメモリ表現
- 以下の情報を一元的に保持する単一の情報源：
  - メッセージ定義
  - ヘッダ情報
  - 複数形ルール
  - 言語情報

つまり、

_「現在の翻訳は何か？」_
_ではなく、_
_「この `Catalog` インスタンスの翻訳は何か？」_

という問い方をします。

```python
catalog = Catalog()
catalog["hello"] = "こんにちは"
```

---

### gettext 互換の dict-like API

`Catalog` のもう一つの重要な設計目標は、

**Python 的に自然でありながら、gettext の挙動を壊さない**

ことです。

そのため、`Catalog` は辞書に似た API を持ちますが、単なる Dict ではありません。

- 存在しないキーは `KeyError` を出さずに、 `msgid` を返す
- ヘッダ (`msgid == "") は特別扱いではなく通常のエントリ
- 複数形の挙動は `Plural-Forms` に従う

```python
catalog["missing"]
# -> "missing"
```

---

### 責務の分離

`pomo-i18n` は明確な責務分離を行っています。

- `Catalog`
  - 実行時の翻訳データと挙動を管理
- `CatalogMessage`
  - 1 つの翻訳エントリを表す正規化されたデータ構造
- `.po` / `.mo` ローダ・ライタ
  - ファイル形式の入出力のみを担当

ファイル形式 (`.po`, `.mo`) は永続化・交換のための層であり、実行時の挙動を支配しません。

この構造により、

- 内部実装の整理
- 将来的なリファクタリング
- マージ戦略や拡張 API の追加

が容易になります。

---

### 暗黙的な挙動に頼らない設計

`pomo-i18n` は、便利さのために挙動を隠すことはしません。

- 自動的な言語切り替えは行わない
- グローバルな翻訳レジストリを持たない
- フレームワーク固有の挙動を内包しない

代わりに、

- 明示的
- 組み合わせ可能
- テストしやすい

ビルディングブロックを提供します。

---

### まとめ

`pomo-i18n` の設計思想を要約すると次の通りです。

- gettext の互換性は維持する
- グローバル状態は排除する
- 翻訳データを明示的なオブジェクトとして扱う
- Python らしさと可読性を優先させる
- 将来の拡張を前提にした設計を行う

この思想は `Catalog` を起点として、すべての API に一貫して反映されています。

---

## dict-like API 詳細 (v0.2.0)

`Catalog` は辞書ライクな API を提供しますが、その挙動は通常の Dict とは異なり、gettext 互換のセマンティクスに基づいています。

この API は、`pomo-i18n` v0.2.0 における主要な利用インターフェースです。

---

### `catalog[key]` --- 翻訳の参照

```python
catalog["hello"]
```

挙動:

| 条件                | 結果                         |
| ------------------- | ---------------------------- |
| `key` が存在する    | 翻訳された単数形文字列を返す |
| `key` が存在しない  | `key` 自体を返す             |
| `key == ""`         | ヘッダーの `msgstr` を返す   |
| `key` が `str` 以外 | `TypeError`                  |

例:

```python
catalog["hello"] = "こんにちは"

catalog["hello"]    # -> "こんにちは"
catalog["missing"]  # -> "missing"
catalog[""]         # -> ヘッダー文字列
```

補足:

- `KeyError` は決して送出されない
- gettext のフォールバック挙動と完全互換
- 複数形はここでは扱わない (v0.2.0 の仕様)

---

### `catalog[key] = value` --- 翻訳の代入

```python
catalog["hello"] = "こんにちは"
```

挙動:

- `key` は `str` でなければならない
- `value` は `str` でなければならない
- 単数形の翻訳を作成、または、上書きする
- `key == ""` の場合はヘッダーを更新する

例:

```python
catalog[""] = "Language: ja\nPlural-Forms: nplurals=2; plural=(n != 1);\n"
```

補足:

- 複数形の代入は **意図的にサポートしていない** (v0.2.0)
- ヘッダ更新時、`Plural-Forms` は自動的に解析される

---

### `"key" in catalog` --- メンバーシップ判定

```python
"hello" in catalog
```

挙動:

| 条件              | 結果                    |
| ----------------- | ----------------------- |
| 翻訳が存在する    | `True`                  |
| 翻訳が存在しない  | `False`                 |
| `key == ""`       | ヘッダーがあれば `True` |
| key が `str` 以外 | `False`                 |

例:

```python
"hello" in catalog
"" in catalog
```

---

### イテレーションとビュー

```python
for key in catalog
```

これは次と等価です

```python
catalog.keys()
```

利用可能なビュー:

```python
catalog.keys()    # KeyView[str]
catalog.values()  # ValueView[CatalogMessage]
catalog.items()   # ItemsView[tuple[str, CatalogMessage]]
len(catalog)      # エントリー数(ヘッダーを含む)
```

※ これらはすべて内部構造を隠さない明示的 API です。

---

### `catalog.get(key[, default])`

```python
catalog.get("hello")
catalog.get("hello", default)
```

挙動(gettext 互換):

| 条件                              | 結果             |
| --------------------------------- | ---------------- |
| `key`が存在する                   | `CatalogMessage` |
| `Key`が存在しない + `default`指定 | `default`        |
| `key`が存在しない + `default`無し | `key`を返す      |
| `key`が`str`以外                  | `TypeError`      |

例:

```python
catalog.get("hello")
# -> CatalogMessage
catalog.get("missing")
# -> "missing"
catalog.get("missing", "fallback")
# -> "fallback"
```

補足:

- `dict.get()` と異なり、`default` 未指定の場合、`None`ではなく`key`を返す
- gettext のフォールバック挙動を再現するための設計

---

### 削除はサポートされない

```python
del catalog["hello"]
```

常に:

```python
TypeError
```

理由

- gettext カタログは「追記・上書き」志向の構造
- 暗黙的な状態変化を防ぐため、削除 API は提供しない

---

### 設計上の意図

- `KeyError` を送出しない --- gettext 互換
- ヘッダーを特別扱いしない --- 一貫したモデル
- 単数形ファースト --- 複数形は明示 API (v0.3.0 予定)

---

### まとめ

dict-like API は次の性質を持つ:

- Python 開発者にとって直感的
- gettext 挙動と互換
- 暗黙的な挙動に頼らない
- 拡張可能な設計の基盤

この API が、`gettext()` / `ngettext()` など高レベル API の基礎となっている。

---

## gettext / ngettext API

`Catalog` は、dict-like API に加えて GNU gettext 互換の翻訳 API を提供する。

これらの API は、既存の gettext ベースのコードから違和感なく移行できることを目的として設計されている。

---

### `gettext()`

```python
catalog.gettext("hello")
# -> "こんにちは"
```

挙動:

| 状況                    | 結果                   |
| ----------------------- | ---------------------- |
| 翻訳が存在する          | 翻訳された文字列       |
| 翻訳が存在しない        | 元の `msgid` を返す    |
| `msgid == ""`(ヘッダー) | gettext() では取得不可 |

これは GNU gettext の `gettext()` と同等の挙動です。

補足:

- 戻り値は常に文字列(`str`)
- `CatalogMessage`オブジェクトは返さない
- `dict-like API` よりも利用側に近い高レベル API

---

### `ngettext()`

```python
catalog.ngettext("apple", "apples", 1)
# -> "apple"

catalog.ngettext("apple", "apples", 2)
# -> "apples"
```

`ngettext()` は、数量 n に応じて適切な複数形翻訳を返すための API です。

挙動の流れ

| 手順 | 条件                                  | 結果                                           |
| ---- | ------------------------------------- | ---------------------------------------------- |
| 1    | 翻訳が存在しない                      | `n == 1` なら `singular`、 それ以外は `plural` |
| 2    | 翻訳が存在する                        | `Plural-Forms`ルールでインデックスを計算       |
| 3    | 対応する `msgstr[index]` が存在する   | その翻訳を返す                                 |
| 4    | index が範囲外だが `msgstr[0]` がある | `msgstr[0]` にフォールバック                   |
| 5    | 有効な翻訳が見つからない              | 翻訳済み単数形にフォールバック                 |
| 6    | 最終手段                              | 元の plural 引数を返す                         |

この処理順は GNU gettext の仕様に準拠している。

---

### 複数形ルール (`Plural-Forms`)

複数形の選択は、カタログヘッダー内の `Plural-Forms` フィールドに基づいて行われる。

例:

```text
Plural-Forms: nplurals=2; plural=(n != 1);
```

挙動:

| 状況                             | 内容                                 |
| -------------------------------- | ------------------------------------ |
| ヘッダーに `Plural-Forms` がある | ルールを解析・コンパイル・キャッシュ |
| ヘッダーに存在しない             | gettext 互換のデフォルトルールを使用 |
| デフォルトルール                 | `nplurals=2; plural=(n != 1);`       |

- ルールは初回のみ解析され、以降はキャッシュされる
- 実行時オーバーヘッドは最小限に抑えられている

---

### dict-like API との関係

| API              | 目的                                  |
| ---------------- | ------------------------------------- |
| `catalog["key"]` | 単数形の簡易アクセス                  |
| `catalog.get()`  | メッセージオブジェクトの取得          |
| `gettext()`      | gettext 互換の文字列取得              |
| `ngettext()`     | 複数形対応の gettext 互換の文字列取得 |

v0.2.0 において:

- dict-like API は単数形中心
- 複数形は `ngettext()` によって明示的に扱う

---

### 設計上の意図

- gettext 互換の挙動を維持する
- 文字列 API とオブジェクト API を明確に分離する
- 暗黙的な状態やグローバル依存を持ち込まない
- 将来の dict-like 複数形拡張 (v0.3.0 以降) に備える

---

### 将来の拡張予定

| バージョン | 予定内容                          |
| ---------- | --------------------------------- |
| v0.3.x     | dict-like な複数形アクセス        |
| v0.3.x+    | `CatalogMessage` とのより蜜な統合 |

それまでは、`ngettext()` が複数形翻訳の正規 API となる。

---

## CatalogMessage の設計

`CatalogMessage` は、`Catalog` 内部で使用されるメッセージ単位の内部表現です。

これは、gettext における 1 つの翻訳エントリ (`msgid`, `msgstr`, `msgid_plural`, `msgstr[n]`) に対応していますが、Python で扱いやすい、イミュータブル指向の構造へ正規化されています。

---

### 目的

`CatalogMessage` は、以下の目的のために存在します。

- **完全に解決された翻訳単位**を表現
- 解析用モデル (`POEntry`) と実行時の参照処理を分離
- 次の処理のための安定したオブジェクトモデルを提供
  - dict-like なアクセス
  - `gettext()` / `ngettext()` の評価
  - `.mo` ファイルへの書き出し

`POEntry` とは異なり、`CatalogMessage` は**ファイル形式のモデルではなく**、_「実行時に翻訳がどのように振る舞うか」を表す_ ためのモデルです。

---

### 構造

```python
@dataclass(slots=True)
class CatalogMessage:
    msgid: str
    singular: str
    plural: str | None
    translations: Dict[int, str]
```

各フィールドの意味

| フィールド     | 内容                                       |
| -------------- | ------------------------------------------ |
| `msgid`        | 論理キーとなる元の未翻訳文字列             |
| `singular`     | 単数形の翻訳 (必ず存在します)              |
| `plural`       | 複数形の `msgid` (存在しない場合は `None`) |
| `translations` | {複数形インデックス: 翻訳文字列}           |

---

### 正規化ルール

`CatalogMessage` は、`__post_init__` 内でいくつかの不変条件を強制します。

- `singular` は **非空**
  - 空の場合: `msgid` をフォールバック
- `plural == ""`は `None` で正規化
- `translations[0]` は**必ず存在**
  - 存在しない場合: `singular` をフォールバック
- 複数形の翻訳が空の場合: 保守的にフォールバック
  - index `0`: `singular` をフォールバック
  - index `n`: `singular` または `plural` をフォールバック

これにより、次のことが保証されます。

- 参照側で防御的なチェックを書く必要がない
- 複数形が欠けていても安全に動作する
- `.mo`書き出しでは一貫性のあるデータが想定できる

---

### 生成用ヘルパー

通常、`CatalogMessage` を直接生成する必要はありませんが、明示的な生成用ヘルパーも用意されています。

単数形メッセージ

```python
CatalogMessage.from_singular(
    msgid="hello",
    msgstr="こんにちは",
)
```

主に以下で使用されます。

- `catalog["key"] = value`
- 複数形を持たないシンプルなカタログ

---

### 複数形メッセージ

```python
CatalogMessage.from_plural(
    msgid="apple",
    msgid_plural="apples",
    forms={
        0: "りんご",
        1: "りんごたち",
    }
)
```

これは主に、以下の内部処理で使用されます。

- `.po` ファイルからの読み込み
- `.mo` ローダー内部

不足している forms は、自動的に正規化されます。

---

### アクセス用ヘルパー

```python
msg.as_plain()
```

単数形の翻訳 (`translations[0]`) を返します。

```python
msg_get_plural(index)
```

フォールバックを伴い安全に複数形を取得します。
これらは主に次の箇所で使用されます。

- `Catalog.__getitem__`
- `Catalog.ngettext()`
- `.mo` writer

---

### イミュータブル指向の設計

`CatalogMessage` は、設計上はイミュータブルに近い扱いです。

- `@dataclass(slot=True)`を使われている
- 公開された変更 API はありません
- `Catalog` 内部では「差し替え」として扱っています

これにより、次のような性質が得られます。

- カタログ間での安全な再利用
- 予測可能なマージ / 更新セマンティックス
- 効率のよいキャッシュと複数形評価

---

### 他レイヤーとの関係

| レイヤー         | 役割                       |
| ---------------- | -------------------------- |
| `POEntry`<br>    | `.po` ファイル解析用モデル |
| `CatalogMessage` | 実行時の翻訳表現           |
| `Catalog`        | 検索・複数形評価・API 表面 |

この分離は意図的な設計です。

- 解析用モデル (`POEntry`) は将来変更される可能性があります。
- 実行時の動作 (`CatalogMessage`) は安定しています。

という理由から、責務を明確に分けています。

---

### バージョンに関する注意

- v0.2.0 では、単数形中心の利用が前提です。
- dict-like な複数形代入は、v0.3.0 以降を予定しています。
- `CatalogMessage` 自体は、既に完全な複数形データを保持できます。

---

## 翻訳ファイルの読み込みと書き出し (`.po` / `.mo`)

`pomo-i18n`では、`.po` や `.mo` といったファイル形式を `Catalog` を中心とする抽象化を**シリアライズ層**として扱います。

v0.2.0 では、

- `.mo` ファイル: 実行時の主要フォーマット
- `.po` ファイル: インポート用フォーマット

という位置付けになっています。

---

### `.po` ファイルの読み込み

テキスト形式の `.po` ファイルは、`POParser` を使って解析し、その結果を `Catalog` に変換します。

```python
from pypomo.parser.po_parser import POParser
from pypomo.catalog import Catalog

parser = POParser()
entries = parser.parse("messages.po")

catalog = Catalog.from_po_entries(entries)
```

補足

- 現在の `.po` パーサーは、以下をサポートしています。

  - `msgid`
  - `msgstr`
  - `msgid_plural`
  - `msgstr[n]`
  - 複数行文字列
  - コメント

- `#, fuzzy` やフラグのような高度な機能は**コメントとして保持**されますが、v0.2.0 では**意味的な解釈は行われません**。
- `.po` ファイルは、あくまでもインポート用フォーマットとして扱われます。

---

### `.mo` ファイルの読み込み

バイナリ形式の `.mo` ファイルは、直接 `Catalog` として読み込めます。

```python
from pypomo.mo.loader import load_mo

catalog = load_mo("messages.mo")
```

この処理により、以下のことが自動的に行われます。

- すべてのメッセージがメモリ上にロード
- ヘッダ (`msgid == ""`) の解析
- `Plural-Forms` の抽出・評価
- 以下の API が即座に利用可能
  - `catalog["msgid"]`
  - `catalog.gettext()`
  - `catalog.ngettext()`

---

### `.mo` ファイルの書き出し

`Catalog` の内容は、GNU gettext 互換の `.mo` ファイルとして書き出されます。

```python
from pypomo.mo.writer import write_mo

write_mo("messages_out.mo", catalog)
```

注意点

- 出力される `.mo` ファイルは GNU gettext 完全互換です。
- ヘッダおよび `Plural-Forms` は保持されます。
- dict-like API を通じた変更内容も反映されます。
- 実行時フォーマットとしては `.mo` ファイルの利用を推奨します。

---

### `.po` ファイルの書き出しについて

v0.2.0 では、`.po` ファイルの書き出しはサポートされていません。

`.po` の生成やよりリッチなメタデータの処理へのサポートは今後のバージョンで予定しています。

---

### 設計上の考え方

- `Catalog` は唯一の正 (**source of truth**)
- `.po` / `.mo` は**シリアライズ層**
- 隠れたグローバル状態はない
- 明示的で、テストしやすく、構成可能な翻訳処理

という方針を採用しています。

---

### 今後のロードマップ

今後のバージョンでは、以下を予定しています。

- `.po` モジュール構成のリファクタリング (`pypomo.po.*`)
- `fuzzy` フラグなどの完全対応
- `.po`ファイルの書き出し対応
- より高度なマージ・アップデート戦略

---

## ライセンス

MIT License
© 2025 Kiminori Kato
