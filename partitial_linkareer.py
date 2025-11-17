##################################partial crawling
import requests
from datetime import datetime

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

