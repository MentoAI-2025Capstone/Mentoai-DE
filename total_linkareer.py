################################## total crawling
import requests
from datetime import datetime
from time import sleep

import csv
import json
from datetime import datetime
from pathlib import Path
from time import sleep

import requests

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

# category ID -> 이름 매핑
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
structured_rows = []
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

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
        print(f"요청 실패: {e}")
        break

    if "errors" in data:
        print("GraphQL 에러 발생:")
        for err in data["errors"]:
            print(f"- {err['message']}")
        break

    activities = data.get("data", {}).get("activities", {}).get("nodes", [])
    if not activities:
        break

    all_activities.extend(activities)
    total_collected += len(activities)

    print(f"{page}페이지 불러옴 (누적: {total_collected})")

    if len(activities) < page_size:
        break

    page += 1
    sleep(0.5)


print(f"\n 전체 공모전 개수: {total_collected}\n")

for item in all_activities:
    title = item.get("title")
    activity_url = f"https://linkareer.com/activity/{item['id']}"
    deadline = datetime.fromtimestamp(item["recruitCloseAt"] / 1000).strftime("%Y-%m-%d") if item.get("recruitCloseAt") else "없음"
    org = item.get("organizationName", "미정")
    category = "공모전"  # 타입 = 3

    print(f"제목: {title}")
    print(f"링크: {activity_url}")
    print(f"분야: {category}")
    print(f"주최/주관: {org}")
    print(f"접수 마감: {deadline}")
    print("-" * 40)


    structured_rows.append(
        {
            "title": title,
            "url": activity_url,
            "category": category,
            "organization": org,
            "deadline": deadline,
            "recruit_start": datetime.fromtimestamp(item["recruitStartAt"] / 1000).strftime("%Y-%m-%d")
            if item.get("recruitStartAt")
            else "없음",
            "created_at": datetime.fromtimestamp(item["createdAt"] / 1000).strftime("%Y-%m-%d")
            if item.get("createdAt")
            else "알수없음",
        }
    )

if structured_rows:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"linkareer_total_{timestamp}.json"
    csv_path = output_dir / f"linkareer_total_{timestamp}.csv"

    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(structured_rows, fp, ensure_ascii=False, indent=2)

    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=structured_rows[0].keys())
        writer.writeheader()
        writer.writerows(structured_rows)

    print(f"\nJSON 파일 저장: {json_path}")
    print(f"CSV 파일 저장(엑셀 열기 가능): {csv_path}")
else:
    print("저장할 데이터가 없습니다.")
