from utils.config import Config
from datetime import datetime
import requests
import os


API_URL = "https://oapi.saramin.co.kr/job-search"
SARAMIN_API_KEY = Config.SARAMIN_API_KEY

if not SARAMIN_API_KEY:
    raise ValueError("환경변수 SARAMIN_API_KEY가 설정되지 않았습니다.")

def fetch_jobs(keyword: str, start: int = 0, count: int = 50):
    """
    keyword : 검색 키워드 (예: '백엔드 개발자')
    start   : 0-base 페이지 번호
    count   : 한 번에 가져올 공고 수 (최대 110)
    """
    headers = {
        # JSON으로 응답받기
        "Accept": "application/json",
    }

    params = {
        "access-key": SARAMIN_API_KEY,   # 필수
        "keywords": keyword,        # 검색어
        "start": start,             # 페이지 시작 번호
        "count": count,             # 가져올 공고 개수
        "sort": "pd",               # 게시일 역순(pd)  [oai_citation:3‡Saramin API](https://oapi.saramin.co.kr/guide/job-search?utm_source=chatgpt.com)
        "fields": "posting-date,expiration-date",
    }

    res = requests.get(API_URL, headers=headers, params=params)
    res.raise_for_status()
    data = res.json()

    # JSON 구조 방어적으로 파싱 
    root = data.get("job-search", data)
    jobs_block = root.get("jobs", {})
    jobs = jobs_block.get("job", [])

    return jobs


def format_timestamp(ts):
    """Unix timestamp(초)를 YYYY-MM-DD로 바꾸는 헬퍼 함수"""
    if not ts:
        return "없음"
    return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")


if __name__ == "__main__":
    keyword = "백엔드 개발자"
    jobs = fetch_jobs(keyword, start=0, count=20)

    print(f"검색 키워드: {keyword}")
    print(f"가져온 공고 수: {len(jobs)}\n")

    for job in jobs:
        job_id = job.get("id")
        url = job.get("url")
        active = job.get("active")  # 1: 진행중, 0: 마감  [oai_citation:4‡Saramin API](https://oapi.saramin.co.kr/guide/job-search?utm_source=chatgpt.com)

        company = job.get("company", {})
        company_name = company.get("name")

        position = job.get("position", {})
        title = position.get("title")

        posting_ts = job.get("posting-timestamp")
        expiration_ts = job.get("expiration-timestamp")

        posting_date = format_timestamp(posting_ts)
        expiration_date = format_timestamp(expiration_ts)

        print(f"[공고 ID] {job_id}")
        print(f"[제목] {title}")
        print(f"[회사명] {company_name}")
        print(f"[진행 여부] {'진행중' if active == '1' else '마감'}")
        print(f"[게시일] {posting_date}")
        print(f"[마감일] {expiration_date}")
        print(f"[URL] {url}")
        print("-" * 60)