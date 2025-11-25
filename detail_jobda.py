from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def get_job_detail(target_url):
    """
    특정 URL에 접속하여 상세 채용 정보를 크롤링합니다.
    """
    # 1. Selenium 설정 (상세 페이지도 동적 로딩일 수 있으므로 Selenium 사용)
    options = webdriver.ChromeOptions()
    options.add_argument('headless') # 브라우저 창 숨김
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    result = {}
    
    try:
        print(f"🚀 상세 페이지 접속 중: {target_url}")
        driver.get(target_url)
        
        # 페이지 로딩 대기 (핵심 요소가 뜰 때까지 최대 10초 대기)
        # 보통 공고 제목이 가장 먼저 뜨므로 제목 요소를 기다립니다.
        # 잡다 상세페이지 제목 클래스 추정: .position_title (변경될 수 있음, 실패시 except로 이동)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
        except:
            print("⚠️ 로딩 대기 시간 초과 (그래도 진행 시도)")
        
        time.sleep(2) # 안전 마진

        # HTML 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # --- [데이터 추출 로직] ---
        
        # 1. 공고 제목 (h1 태그일 확률이 높음)
        title_tag = soup.find("h1")
        result['title'] = title_tag.get_text(strip=True) if title_tag else "제목 없음"
        
        # 2. 본문 내용 (주요업무, 자격요건 등)
        # 잡다의 상세 내용은 보통 'div.view_editor' 또는 특정 컨테이너 안에 있습니다.
        # 클래스 이름을 정확히 모를 때는 본문 영역을 통째로 긁어오는 것이 안전합니다.
        
        # 전략 A: '주요업무'라는 단어가 포함된 부모 태그 찾기 (스마트 추출)
        content_found = False
        target_keywords = ["주요업무", "자격요건", "주요 업무", "자격 요건", "담당업무"]
        
        # 텍스트가 있는 모든 div를 검사해서 키워드가 있는 덩어리를 찾음
        main_content = ""
        for div in soup.find_all("div"):
            text = div.get_text()
            # 키워드가 포함되어 있고, 글자 수가 적당히 많은(50자 이상) 블록을 본문으로 간주
            if any(keyword in text for keyword in target_keywords) and len(text) > 50:
                 # 너무 상위 부모(body 등)는 제외하기 위해 글자수 제한 등을 둘 수 있음
                 # 여기서는 가장 먼저 발견된 구체적인 블록을 사용하거나, 
                 # 단순히 전체 텍스트를 가져오는 방식을 씁니다.
                 pass

        # 전략 B: (가장 확실한 방법) 페이지 전체 텍스트에서 불필요한 헤더/푸터 제거
        # 상세 페이지의 특징적인 클래스 이름(개발자 도구로 확인 필요)을 알면 좋지만,
        # 모르를 때는 'main' 태그나 큰 컨테이너를 찾습니다.
        
        # 임시 방편: 본문 텍스트 전체 추출 (줄바꿈 보존)
        # 잡다 상세페이지 구조상 <div class="position_view_container"> 같은 것이 있을 것입니다.
        # 여기서는 전체 텍스트를 긁어서 보여줍니다.
        body_text = soup.get_text(separator="\n", strip=True)
        
        # 너무 긴 텍스트(메뉴 등 포함)를 다듬기 위해 키워드 기준으로 자르기 시도
        start_idx = -1
        for kw in target_keywords:
            idx = body_text.find(kw)
            if idx != -1:
                start_idx = idx
                break
        
        if start_idx != -1:
            # 키워드 위치부터 텍스트를 가져옴 (메뉴 등 앞부분 쓰레기 데이터 제거 효과)
            final_desc = body_text[start_idx:]
            # 뒷부분 자르기 (예: "접수기간" 뒤는 필요 없다면 자름)
        else:
            final_desc = body_text[:1000] + "... (키워드 못 찾음)"

        result['description'] = final_desc
        
        # 3. 마감일 정보 (보통 'D-' 또는 날짜 형식)
        # 이 부분은 페이지 구조에 따라 다릅니다.
        
    except Exception as e:
        print(f"❌ 크롤링 중 오류: {e}")
        result['error'] = str(e)
        
    finally:
        driver.quit()
        
    return result

# --- 실행부 ---
if __name__ == "__main__":
    # 아까 JSON 결과 중 하나를 예시로 넣습니다.
    # 사용자가 링크를 준다고 가정:
    target_link = "https://www.jobda.im/position/163457/jd" # [KG이니시스] 예시 링크
    
    print(f"User: 이 링크 상세 정보 좀 줘 -> {target_link}")
    
    detail_info = get_job_detail(target_link)
    
    print("-" * 50)
    print(f"📌 제목: {detail_info.get('title')}")
    print("-" * 50)
    print("📝 상세 내용 (일부분):")
    # 내용이 너무 길 수 있으니 앞 500자만 출력
    print(detail_info.get('description')[:]) 
    print("-" * 50)
    
    # 팁: 여기서 결과가 잘 나오면 JSON으로 전체를 저장하는 코드로 확장하면 됩니다.