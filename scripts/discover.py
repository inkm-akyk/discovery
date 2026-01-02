import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

print("=== Fashion Discovery System ===")
print(f"実行時刻: {datetime.now()}")
print("")

try:
    # Makuakeトップページから新着プロジェクトを探す
    url = "https://www.makuake.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # プロジェクトへのリンクを探す
        all_links = soup.find_all('a', href=re.compile(r'/project/'))
        
        # 重複を除去
        project_urls = []
        seen = set()
        for link in all_links:
            href = link.get('href')
            if href and href not in seen and '/project/' in href:
                if not href.startswith('http'):
                    href = 'https://www.makuake.com' + href
                seen.add(href)
                project_urls.append({
                    'url': href,
                    'text': link.get_text(strip=True)[:100]  # 最初の100文字
                })
        
        print(f"✅ {len(project_urls)}件のプロジェクトを発見")
        print("")
        
        # 最初の5件を表示
        for i, proj in enumerate(project_urls[:5], 1):
            print(f"{i}. {proj['text']}")
            print(f"   🔗 {proj['url']}")
            print("")
            
    else:
        print(f"⚠️ ステータスコード: {response.status_code}")
        
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()

print("=== 完了 ===")
