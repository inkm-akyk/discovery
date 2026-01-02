import requests
from datetime import datetime

print("=== Fashion Discovery System ===")
print(f"実行時刻: {datetime.now()}")
print("")

# テスト: Makuakeの新着プロジェクトを取得
try:
    url = "https://www.makuake.com/projects/?category_id=8"  # ファッションカテゴリ
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        print("✅ Makuake接続成功")
        print(f"取得データサイズ: {len(response.text)} 文字")
    else:
        print(f"⚠️ ステータスコード: {response.status_code}")
        
except Exception as e:
    print(f"❌ エラー: {e}")

print("")
print("=== テスト完了 ===")
