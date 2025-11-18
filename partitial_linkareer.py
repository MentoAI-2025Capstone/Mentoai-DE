##################################partial crawling
import csv
import json
from datetime import datetime
from pathlib import Path

import requests

url = "https://api.linkareer.com/graphql"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Origin": "https://linkareer.com",
    "Referer": "https://linkareer.com/",
    "Content-Type": "application/json"
}

payload = {
    "operationName": "ActivityList_Activities",
    "variables": {
        "filterBy": {
            "status": "OPEN",
            "activityTypeID": 3  # 공모전
        },
        "pageSize": 30,
        "page": 1,
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

res = requests.post(url, headers=headers, json=payload)
data = res.json()

if "errors" in data:
    print("GraphQL 에러 발생:")
    for err in data["errors"]:
        print(f"- {err['message']}")
    exit()

activities = data.get("data", {}).get("activities", {}).get("nodes", [])
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)
structured_rows = []

print(f"공모전 개수: {len(activities)}\n")

for item in activities:
    title = item.get("title")
    activity_url = f"https://linkareer.com/activity/{item['id']}"
    deadline = datetime.fromtimestamp(item["recruitCloseAt"] / 1000).strftime("%Y-%m-%d") if item.get("recruitCloseAt") else "없음"
    org = item.get("organizationName", "미정")
    category = "공모전"

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
        }
    )

if structured_rows:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"linkareer_partial_{timestamp}.json"
    csv_path = output_dir / f"linkareer_partial_{timestamp}.csv"

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
