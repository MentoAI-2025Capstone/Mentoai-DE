from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from PIL import Image
import pytesseract
import requests
from io import BytesIO
import time

# [중요] Tesseract 경로 설정 (맥은 brew로 설치했으면 보통 설정 안 해도 됨)
# 만약 오류나면 경로 확인 필요: which tesseract 터미널 입력

def get_job_detail_image_ocr(target_url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless') 
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    final_text = ""
    
    try:
        print(f"🚀 페이지 접속 중... {target_url}")
        driver.get(target_url)
        time.sleep(5) # 이미지 로딩 대기

        # 1. 상세 정보를 담고 있는 이미지 태그 찾기
        # 잡다(Jobda) 사이트 구조상 상세 이미지는 보통 .position_view_img 또는 내용 영역 안의 img 태그임
        # 가장 큰 이미지를 찾는 전략을 사용합니다.
        
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"🔎 페이지 내 이미지 {len(images)}개 발견. 상세 공고 이미지 찾는 중...")
        
        target_img_url = ""
        max_height = 0
        
        for img in images:
            try:
                # 이미지의 실제 높이를 확인 (공고 이미지는 보통 세로로 아주 긺)
                height = int(img.get_attribute("naturalHeight"))
                src = img.get_attribute("src")
                
                # 높이가 1000px 이상이거나, src에 'recruit' 같은 키워드가 있으면 공고 이미지로 추정
                if height > 800 and src and ("http" in src):
                    if height > max_height:
                        max_height = height
                        target_img_url = src
            except:
                continue
        
        if target_img_url:
            print(f"✅ 상세 공고 원본 이미지 발견! (높이: {max_height}px)")
            print(f"🔗 이미지 주소: {target_img_url}")
            
            # 2. 이미지 다운로드 (메모리로)
            response = requests.get(target_img_url)
            img_data = Image.open(BytesIO(response.content))
            
            # 3. OCR 수행
            print("📝 고화질 이미지로 OCR 분석 시작...")
            # lang='kor' 필수, --psm 6은 단일 블록 텍스트로 인식(표 읽을 때 유리)
            text = pytesseract.image_to_string(img_data, lang='kor+eng', config='--psm 6')
            
            final_text = text
        else:
            final_text = "❌ 공고로 추정되는 긴 이미지를 찾지 못했습니다."

    except Exception as e:
        print(f"Error: {e}")
        final_text = str(e)
        
    finally:
        driver.quit()
        
    return final_text

if __name__ == "__main__":
    url = "https://www.jobda.im/position/140294/jd"
    result_text = get_job_detail_image_ocr(url)
    
    print("="*50)
    print("OCR 상세 추출 결과:")
    print("-" * 50)
    # 결과가 너무 길면 앞 1000자만 출력, 공백 정리
    clean_text = "\n".join([line for line in result_text.split('\n') if line.strip()])
    print(clean_text[:]) 
    print("="*50)