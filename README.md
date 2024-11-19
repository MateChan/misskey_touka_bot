# Misskey Touka Bot

メンションで送りつけられた画像を透過してリプライするMisskey botです．

## 使用方法

[uv](https://github.com/astral-sh/uv) の使用を想定しています．

### 依存関係のインストール

```bash
uv sync
```

### 実行

```bash
uv run main.py
```

## 環境変数

以下の環境変数の設定が必要です．実行時に設定するか，`main.py`と同じ階層に`.env`ファイルを配置してください．

| 変数名          | 内容                                             |
| --------------- | ------------------------------------------------ |
| `MISSKEY_HOST`  | Misskeyインスタンスのホスト名 (例: `misskey.io`) |
| `MISSKEY_TOKEN` | MisskeyのAPIトークン                             |

## Thanks

- [yupix/MiPA: Python Misskey Bot Framework](https://github.com/yupix/MiPA)
  - Misskey Botフレームワーク
- [briaai/RMBG\-2\.0 · Hugging Face](https://huggingface.co/briaai/RMBG-2.0)
  - 背景除去用の深層学習モデル
