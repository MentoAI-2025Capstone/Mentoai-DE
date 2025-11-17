# # Crawling server

# from fastapi import FastAPI, Query
# import requests
# from bs4 import BeautifulSoup

# app = FastAPI()

# @app.get("/crawl")
# def crawl_webtoon(url: str = Query(...)):
#     print(f"Crawling URL: {url}")

#     try:
#         response = requests.get(url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         print(soup)
        
#         return {"status": "success", "data": soup.prettify()}
#     except Exception as e:
#         print(f"Error: {e}")
#         return {"status": "error", "message": str(e)}
    
# @app.get("/favicon.ico")
# def favicon():
#     return {"message": "Favicon not found"}


################################## total crawling
import requests
import json
from datetime import datetime
from time import sleep

# 요청 URL
url = "https://api.linkareer.com/graphql"

# 요청 헤더
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://linkareer.com",
    "Referer": "https://linkareer.com/",
    "Content-Type": "application/json"
}

# 필터용 category ID -> 이름 매핑
category_map = {
    "28": "기획/아이디어",
    "29": "광고/마케팅",
    "30": "사진/영상/UCC",
    "31": "디자인/순수미술/공예",
    "32": "네이밍/슬로건",
    "33": "캐릭터/만화/게임",
    "34": "건축/건설/인테리어",
    "35": "과학/공학",
    "36": "예체능/패션",
    "37": "전시/페스티벌",
    "38": "문학/시나리오",
    "39": "해외",
    "40": "학술",
    "41": "창업",
    "42": "기타"
}

page_size = 50
page = 1
total_collected = 0
all_activities = []

# 페이지 반복
while True:
    payload = {
        "operationName": "ActivityList_Activities",
        "variables": {
            "filterBy": {
                "status": "OPEN",
                "activityTypeID": 3
            },
            "pageSize": page_size,
            "page": page,
            "activityOrder": {
                "field": "CREATED_AT",
                "direction": "DESC"
            }
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "23b5c0dd9f7f00b35d76db2f2b1604a049b17a5b064c977a43a7258a2fe3d07b"
            }
        }
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
    except Exception as e:
        print(f"❌ 요청 실패: {e}")
        break

    if "errors" in data:
        print("❌ GraphQL 에러 발생:")
        for err in data["errors"]:
            print(f"- {err['message']}")
        break

    activities = data.get("data", {}).get("activities", {}).get("nodes", [])
    if not activities:
        break

    all_activities.extend(activities)
    total_collected += len(activities)

    print(f"✅ {page}페이지 불러옴 (누적: {total_collected})")

    if len(activities) < page_size:
        break

    page += 1
    sleep(0.5)

# 출력
print(f"\n✅ 전체 공모전 개수: {total_collected}\n")

for item in all_activities:
    title = item.get("title")
    activity_url = f"https://linkareer.com/activity/{item['id']}"
    deadline = datetime.fromtimestamp(item["recruitCloseAt"] / 1000).strftime("%Y-%m-%d") if item.get("recruitCloseAt") else "없음"
    org = item.get("organizationName", "미정")
    category = "공모전"  # activityTypeID == 3

    print(f"제목: {title}")
    print(f"링크: {activity_url}")
    print(f"분야: {category}")
    print(f"주최/주관: {org}")
    print(f"접수 마감: {deadline}")
    print("-" * 40)


