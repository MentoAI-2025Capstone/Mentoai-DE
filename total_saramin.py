from utils.config import Config
import os
import json
import time
import requests

API_URL = "https://oapi.saramin.co.kr/job-search"
SARAMIN_API_KEY = Config.SARAMIN_API_KEY

if not SARAMIN_API_KEY:
    raise ValueError("환경변수 SARAMIN_API_KEY가 설정되지 않았습니다.")


PAGE_SIZE = 50           
SLEEP_SEC = 0.3          


def fetch_jobs(start: int, count: int):
    """
    start, count 기준으로 사람인 API에서 공고 한 '페이지'를 가져오는 함수
    """
    params = {
        "access-key": SARAMIN_API_KEY,
        "start": start,       # 0, 50, 100, ... 이런 식으로 증가
        "count": count,       # 페이지당 개수
        "output": "json",     # JSON 응답
        # 필요한 경우 검색조건 추가 (키워드, 지역, 산업, 직무 등)
        # 예시) "keywords": "백엔드",
    }

    resp = requests.get(API_URL, params=params, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    # 사람인 JSON 구조 
    # 예시) 
    # {
    #   "jobs": {
    #       "job": [ {...}, {...}, ... ],
    #       "total": 1234,
    #       ...
    #   }
    # }
    jobs = data.get("jobs", {}).get("job", [])
    total = data.get("jobs", {}).get("total", None)

    return jobs, total


def normalize_job(raw_job: dict) -> dict:
    """
    사람인에서 온 한 개의 raw job을 우리가 쓰기 좋은 형태로 정리
    (키 이름은 실제 응답 구조에 맞게 필요하면 수정)
    """
    company = raw_job.get("company", {}) if isinstance(raw_job.get("company"), dict) else {}
    position = raw_job.get("position", {}) if isinstance(raw_job.get("position"), dict) else {}
    # company / position이 리스트로 올 수도 있으니 실제 응답 보면서 맞추기

    return {
        "id": raw_job.get("id"),
        "url": raw_job.get("url"),
        "company_name": company.get("name"),
        "title": position.get("title"),
        "location": position.get("location"),
        "job_type": position.get("job_type"),
        "industry": raw_job.get("industry"),
        "expiration_date": raw_job.get("expiration-date") or raw_job.get("expiration_date"),
        "salary": raw_job.get("salary"),
        "raw": raw_job,  
    }


def main():
    if SARAMIN_API_KEY == "YOUR_SARAMIN_API_KEY_HERE":
        print("❌ 먼저 SARAMIN_API_KEY 를 환경변수로 설정하거나 코드 안에 실제 키를 넣어줘야 합니다.")
        return

    all_jobs = []
    start = 0

    print("🔍 사람인 전체 공고 크롤링 시작...")

    while True:
        print(f"start={start}, count={PAGE_SIZE} 페이지 요청 중...")

        try:
            jobs, total = fetch_jobs(start=start, count=PAGE_SIZE)
        except Exception as e:
            print(f"요청 실패: {e}")
            break

        if not jobs:
            print("더 이상 가져올 공고가 없습니다. 크롤링 종료.")
            break

        # 정규화 후 리스트 추가
        for j in jobs:
            all_jobs.append(normalize_job(j))

        print(f"   → 이번 페이지에서 {len(jobs)}건 수집 (누적: {len(all_jobs)}건)")
        # total 값 있으면 참고용으로 출력
        if total is not None:
            print(f"   → API가 알려준 전체 개수: {total}건")

        # 마지막 페이지인지 체크
        if len(jobs) < PAGE_SIZE:
            print("마지막 페이지까지 수집 완료.")
            break

        # 다음 페이지
        start += PAGE_SIZE
        time.sleep(SLEEP_SEC)

    print(f"\n 최종 수집 공고 수: {len(all_jobs)}건")


    for job in all_jobs[:5]:
        print("-" * 60)
        print(f"[{job['company_name']}] {job['title']}")
        print(f"  • 링크: {job['url']}")
        print(f"  • 마감일: {job['expiration_date']}")
        print(f"  • 근무지: {job['location']}")
        print(f"  • 산업: {job['industry']}")

    out_path = "jobs_saramin.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)

    print(f"\n 전체 공고를 '{out_path}' 파일로 저장했습니다.")


if __name__ == "__main__":
    main()