# Discovery - 週次スクレイピング & Slack通知システム

週次でウェブスクレイピングを行い、発見したプロジェクトをSlackに通知するGitHub Actionsベースのシステムです。

## 機能

- 毎週月曜日0時（UTC）= 日本時間9時に自動実行
- Makuakeの新着プロジェクトを収集
- 発見したプロジェクトをSlackに通知（上位10件）
- 手動実行にも対応

## セットアップ手順

### 1. Slack Webhook URLの取得

1. [Slack API](https://api.slack.com/apps) にアクセス
2. "Create New App" → "From scratch" を選択
3. アプリ名と通知先のワークスペースを選択
4. "Incoming Webhooks" を有効化
5. "Add New Webhook to Workspace" で通知先チャンネルを選択
6. 生成されたWebhook URLをコピー

### 2. GitHub Secretsの設定

1. GitHubリポジトリの Settings → Secrets and variables → Actions へ移動
2. "New repository secret" をクリック
3. 以下を設定:
   - Name: `SLACK_WEBHOOK_URL`
   - Secret: 先ほどコピーしたWebhook URL

### 3. ワークフローの有効化

- リポジトリの "Actions" タブで、ワークフローが有効になっていることを確認
- 初回は "Run workflow" ボタンで手動実行して動作確認

## ローカルでのテスト実行

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数を設定して実行
export SLACK_WEBHOOK_URL="your-webhook-url-here"
python scripts/discover.py
```

## スケジュール

- 自動実行: 毎週月曜日 0:00 UTC（日本時間 9:00）
- スケジュール変更: [.github/workflows/weekly-discovery.yml](.github/workflows/weekly-discovery.yml) の `cron` を編集

## ファイル構成

```
.
├── .github/
│   └── workflows/
│       └── weekly-discovery.yml  # GitHub Actionsワークフロー
├── scripts/
│   └── discover.py              # スクレイピング & Slack通知スクリプト
├── requirements.txt             # Python依存パッケージ
└── README.md                    # このファイル
```

## カスタマイズ

- スクレイピング対象の変更: [scripts/discover.py](scripts/discover.py) の `url` を編集
- 通知形式の変更: `send_slack_notification()` 関数を編集
- 実行頻度の変更: ワークフローファイルの `cron` を編集