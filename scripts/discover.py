import requests
from bs4 import BeautifulSoup
from datetime import datetime

print("=== Fashion Discovery System ===")
print(f"実行時刻: {datetime.now()}")
print("")

# Makuakeのファッションカテゴリをスクレイピング
try:
    url = "https://www.makuake.com/projects/?category_id=8&sort=new"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # プロジェクトカードを探す（セレクタは要調整）
        projects = soup.find_all('div', class_='project-card')[:5]  # 最新5件
        
        print(f"✅ {len(projects)}件のプロジェクトを発見")
        print("")
        
        for i, project in enumerate(projects, 1):
            try:
                title_elem = project.find('h3')
                title = title_elem.text.strip() if title_elem else "タイトル不明"
                
                link_elem = project.find('a')
                link = "https://www.makuake.com" + link_elem['href'] if link_elem and link_elem.get('href') else ""
                
                print(f"{i}. {title}")
                if link:
                    print(f"   🔗 {link}")
                print("")
                
            except Exception as e:
                print(f"⚠️ プロジェクト{i}の解析エラー: {e}")
                
    else:
        print(f"⚠️ ステータスコード: {response.status_code}")
        
except Exception as e:
    print(f"❌ エラー: {e}")

print("=== 完了 ===")
