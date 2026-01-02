import requests
from datetime import datetime, timedelta
import os
import json
import feedparser
from googletrans import Translator
import time

# 翻訳器の初期化
translator = Translator()

def translate_text(text, max_retries=3):
    """テキストを日本語に翻訳（リトライ機能付き）"""
    if not text:
        return ""

    for attempt in range(max_retries):
        try:
            result = translator.translate(text, src='en', dest='ja')
            return result.text
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 1秒待ってリトライ
                continue
            print(f"翻訳エラー: {e}")
            return text  # 翻訳失敗時は原文を返す

def fetch_hacker_news(days=7, min_score=100):
    """Hacker Newsから過去N日間の高評価記事を取得"""
    print("📰 Hacker Newsから記事を取得中...")

    try:
        # HN Algolia APIを使用（過去7日間のトップ記事）
        cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        url = f"https://hn.algolia.com/api/v1/search?tags=story&numericFilters=created_at_i>{cutoff_timestamp},points>{min_score}&hitsPerPage=10"

        response = requests.get(url, timeout=10)
        data = response.json()

        articles = []
        for hit in data.get('hits', [])[:5]:  # 上位5件
            title = hit.get('title', '')
            url = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            points = hit.get('points', 0)
            comments = hit.get('num_comments', 0)

            # 翻訳
            title_ja = translate_text(title)

            articles.append({
                'source': 'Hacker News',
                'title': title,
                'title_ja': title_ja,
                'url': url,
                'score': points,
                'comments': comments
            })

        print(f"  ✅ {len(articles)}件取得")
        return articles

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return []

def fetch_reddit_rss(subreddit, limit=5):
    """RedditのRSSフィードから高評価投稿を取得"""
    print(f"📱 r/{subreddit}から投稿を取得中...")

    try:
        # Reddit RSSフィード（トップ投稿）
        rss_url = f"https://www.reddit.com/r/{subreddit}/top/.rss?t=week"
        feed = feedparser.parse(rss_url)

        posts = []
        for entry in feed.entries[:limit]:
            title = entry.title
            url = entry.link

            # 翻訳
            title_ja = translate_text(title)

            posts.append({
                'source': f'r/{subreddit}',
                'title': title,
                'title_ja': title_ja,
                'url': url,
                'score': 0,  # RSSからは正確な数値取得困難
                'comments': 0
            })

        print(f"  ✅ {len(posts)}件取得")
        return posts

    except Exception as e:
        print(f"  ❌ エラー: {e}")
        return []

def send_slack_notification(all_discoveries):
    """Slack Webhook URLに通知を送信"""
    webhook_url = os.environ.get('SLACK_WEBHOOK_URL')

    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL が設定されていません")
        return False

    # 総件数を計算
    total_count = sum(len(items) for items in all_discoveries.values())

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
                "text": f"*{datetime.now().strftime('%Y年%m月%d日')}*\n今週発見: *{total_count}件*"
            }
        },
        {
            "type": "divider"
        }
    ]

    # 各ソースごとにセクション作成
    for source_name, items in all_discoveries.items():
        if not items:
            continue

        # ソースヘッダー
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*【{source_name}】 {len(items)}件*"
            }
        })

        # 各記事
        for i, item in enumerate(items, 1):
            title_ja = item.get('title_ja', item.get('title', ''))
            title_en = item.get('title', '')
            url = item.get('url', '')
            score = item.get('score', 0)
            comments = item.get('comments', 0)

            # メタ情報
            meta = []
            if score > 0:
                meta.append(f"⭐ {score}")
            if comments > 0:
                meta.append(f"💬 {comments}")

            meta_str = " | ".join(meta) if meta else ""

            # タイトル表示（日本語訳 + 英語原文）
            title_display = f"*{title_ja}*\n_{title_en}_"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{i}. {title_display}\n{meta_str}\n<{url}|記事を見る>"
                }
            })

        blocks.append({"type": "divider"})

    payload = {"blocks": blocks}

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


print("=== Weekly Discovery System ===")
print(f"実行時刻: {datetime.now()}")
print("")

try:
    all_discoveries = {}

    # 1. Hacker News
    hn_articles = fetch_hacker_news(days=7, min_score=100)
    if hn_articles:
        all_discoveries['Hacker News'] = hn_articles

    # 2. r/BuyItForLife
    bifl_posts = fetch_reddit_rss('BuyItForLife', limit=5)
    if bifl_posts:
        all_discoveries['r/BuyItForLife'] = bifl_posts

    # 3. r/malefashionadvice
    mfa_posts = fetch_reddit_rss('malefashionadvice', limit=5)
    if mfa_posts:
        all_discoveries['r/malefashionadvice'] = mfa_posts

    # 4. r/LocalLLaMA
    llama_posts = fetch_reddit_rss('LocalLLaMA', limit=5)
    if llama_posts:
        all_discoveries['r/LocalLLaMA'] = llama_posts

    print("")
    print(f"✅ 合計 {sum(len(v) for v in all_discoveries.values())}件の記事を発見")
    print("")

    # Slackに通知
    if all_discoveries:
        send_slack_notification(all_discoveries)
    else:
        print("⚠️ 記事が見つかりませんでした")

except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("=== 完了 ===")
