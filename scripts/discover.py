import requests
from datetime import datetime
import os
import json

def send_slack_notification(projects):
    """Slack Webhook URLに通知を送信"""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL が設定されていません")
        return False

    # Slack メッセージを構築
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔍 週次Discovery Report",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{datetime.now().strftime('%Y年%m月%d日')}*\n今週発見したプロジェクト: *{len(projects)}件*"
            }
        },
        {
            "type": "divider"
        }
    ]

    # 上位10件をSlackに表示
    for i, proj in enumerate(projects[:10], 1):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}. {proj['text'][:80]}*\n<{proj['url']}|プロジェクトを見る>"
            }
        })

    if len(projects) > 10:
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"_他 {len(projects) - 10} 件のプロジェクトあり_"
                }
            ]
        })

    payload = {
        "blocks": blocks
    }

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            print("✅ Slack通知を送信しました")
            return True
        else:
            print(f"⚠️ Slack通知失敗: ステータスコード {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Slack通知エラー: {e}")
        return False


print("=== Fashion Discovery System ===")
print(f"実行時刻: {datetime.now()}")
print("")

try:
    # テスト用のサンプルデータ（実際のスクレイピングは後で実装）
    # TODO: 実際のスクレイピング対象URLに変更してください
    project_urls = [
        {
            'url': 'https://www.makuake.com/project/sample1/',
            'text': 'サンプルプロジェクト1: 革新的なファッションアイテム'
        },
        {
            'url': 'https://www.makuake.com/project/sample2/',
            'text': 'サンプルプロジェクト2: 次世代のウェアラブルデバイス'
        },
        {
            'url': 'https://www.makuake.com/project/sample3/',
            'text': 'サンプルプロジェクト3: エコフレンドリーな日用品'
        }
    ]

    print(f"✅ {len(project_urls)}件のプロジェクトを発見（テストデータ）")
    print("")

    # 最初の5件をコンソールに表示
    for i, proj in enumerate(project_urls[:5], 1):
        print(f"{i}. {proj['text']}")
        print(f"   🔗 {proj['url']}")
        print("")

    # Slackに通知
    if project_urls:
        send_slack_notification(project_urls)
    else:
        print("⚠️ プロジェクトが見つかりませんでした")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("=== 完了 ===")
