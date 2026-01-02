import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
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
    # Makuakeトップページから新着プロジェクトを取得
    url = "https://www.makuake.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # プロジェクトカードを探す（より柔軟な検索）
        project_urls = []
        seen = set()

        # プロジェクトリンクを複数の方法で探す
        # 方法1: /project/ を含むリンク
        project_links = soup.find_all('a', href=re.compile(r'/project/'))

        for link in project_links:
            href = link.get('href')
            if href and href not in seen and '/project/' in href:
                # 相対パスを絶対パスに変換
                if not href.startswith('http'):
                    href = 'https://www.makuake.com' + href

                # テキストを取得（タイトルなど）
                text = link.get_text(strip=True)
                if not text:
                    # alt属性やtitle属性からテキストを取得
                    img = link.find('img')
                    if img:
                        text = img.get('alt', '') or img.get('title', '')

                if text and href not in seen:
                    seen.add(href)
                    project_urls.append({
                        'url': href,
                        'text': text[:100]  # 最初の100文字
                    })

        print(f"✅ {len(project_urls)}件のプロジェクトを発見")
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

    else:
        print(f"⚠️ ステータスコード: {response.status_code}")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("=== 完了 ===")
