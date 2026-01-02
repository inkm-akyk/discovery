import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("=== Fashion Discovery System ===")
print(f"実行時刻: {datetime.now()}")
print("")

# Makuakeのトップページから試す
try:
    url = "https://www.makuake.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print(f"アクセス先: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"ステータスコード: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ページタイトルを取得
        title = soup.find('title')
        print(f"ページタイトル: {title.text if title else '不明'}")
        print("")
        
        # リンクを探す（デバッグ用）
        links = soup.find_all('a', href=True)[:10]
        print(f"✅ 最初の10個のリンク:")
        for i, link in enumerate(links, 1):
            print(f"{i}. {link.get('href')}")
        
    else:
        print(f"⚠️ アクセス失敗")
        
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("")
print("=== 完了 ===")
