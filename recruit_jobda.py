import json  # JSON 저장을 위한 라이브러리
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

BASE_URL = "https://www.jobda.im"
POSITION_URL = "https://www.jobda.im/position"

def fetch_jobda_html_with_scroll():
    """스크롤을 끝까지 내려 모든 공고를 로딩한 후 HTML을 가져옵니다."""
    
    options = webdriver.ChromeOptions()
    options.add_argument('headless') 
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print("🌍 잡다(Jobda) 사이트 접속 중...")
        driver.get(POSITION_URL)
        time.sleep(3) # 초기 로딩 대기

        # --- [핵심] 무한 스크롤 로직 ---
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while True:
            # 1. 스크롤을 맨 아래로 내림
            print("⬇️ 스크롤을 내리는 중...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # 2. 데이터 로딩 대기 (인터넷 속도에 따라 조절 필요, 2~3초 권장)
            time.sleep(2)
            
            # 3. 스크롤 후 높이 비교 (더 이상 내려갈 곳이 없으면 종료)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("✅ 스크롤 완료! 더 이상 불러올 공고가 없습니다.")
                break
            last_height = new_height
        # -----------------------------
        
        html = driver.page_source
        return html
    except Exception as e:
        print(f"❌ Selenium 오류 발생: {e}")
        return None
    finally:
        driver.quit()

def parse_jobda_detail(html: str):
    """HTML에서 공고 정보를 상세 분리하여 추출합니다."""
    soup = BeautifulSoup(html, "html.parser")
    items = []

    all_links = soup.find_all("a", href=True)
    job_links = [a for a in all_links if "/position/" in a["href"] and len(a["href"]) > 10]
    
    # 중복 제거 (가끔 스크롤 과정에서 중복된 요소가 잡힐 수 있음)
    # 링크(href)를 기준으로 중복을 제거하기 위해 딕셔너리 사용 후 리스트 변환 고려 가능하지만,
    # 여기서는 일단 리스트로 다 받습니다.
    
    print(f"🔎 발견된 공고 요소 개수: {len(job_links)}개")

    for item in job_links:
        link = urljoin(BASE_URL, item.get("href"))
        
        img_tag = item.find("img")
        img_url = img_tag["src"] if img_tag else ""
        
        text_parts = list(item.stripped_strings)
        title = text_parts[0] if len(text_parts) > 0 else ""
        company = text_parts[1] if len(text_parts) > 1 else ""
        etc_info = " / ".join(text_parts[2:]) if len(text_parts) > 2 else ""

        items.append({
            "title": title,
            "company": company,
            "etc": etc_info,
            "img_url": img_url,
            "link": link
        })

    return items

if __name__ == "__main__":
    # 1. 스크롤까지 포함해서 HTML 가져오기
    html = fetch_jobda_html_with_scroll()
    
    if html:
        # 2. 파싱
        job_postings = parse_jobda_detail(html)

        print("-" * 50)
        print(f"📊 최종 수집된 공고 개수: {len(job_postings)}개")
        print("-" * 50)
        
        # 3. JSON 파일로 저장
        json_filename = "jobda_result.json"
        
        try:
            with open(json_filename, "w", encoding="utf-8") as f:
                # ensure_ascii=False : 한글이 깨지지 않고 보이게 함
                # indent=4 : 들여쓰기를 해서 보기 좋게 저장함
                json.dump(job_postings, f, ensure_ascii=False, indent=4)
                
            print(f"💾 '{json_filename}' 파일로 예쁘게 저장되었습니다!")
            
        except Exception as e:
            print(f"❌ JSON 저장 중 오류 발생: {e}")
            
    else:
        print("❌ HTML을 가져오지 못했습니다.")