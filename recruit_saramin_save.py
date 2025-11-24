import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import csv
import os

BASE_URL = "https://www.saramin.co.kr"
HOT100_URL = "https://www.saramin.co.kr/zf_user/jobs/hot100"


def fetch_hot100_html():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": BASE_URL,
    }
    resp = requests.get(HOT100_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text


def parse_hot100(html: str):
    soup = BeautifulSoup(html, "html.parser")
    items = []

    for item in soup.select(".list_recruiting.list_hot_type .list_body .list-container .list_item"):
        box = item.select_one(".box_item")
        if not box:
            continue

        raw_id = item.get("id", "")
        rec_id = raw_id.replace("rec-", "") if raw_id.startswith("rec-") else None

        rank_el = box.select_one(".col.ranking_info strong.tit")
        rank = rank_el.get_text(strip=True) if rank_el else None

        company_el = box.select_one(".col.company_nm .str_tit")
        company = company_el.get_text(strip=True) if company_el else None

        title_a = box.select_one(".col.notification_info .job_tit a.str_tit")
        title = title_a.get_text(strip=True) if title_a else None
        link = urljoin(BASE_URL, title_a["href"]) if title_a and title_a.has_attr("href") else None

        job_sector_spans = box.select(".col.notification_info .job_meta .job_sector span")
        job_sectors = [s.get_text(strip=True) for s in job_sector_spans]

        work_place_el = box.select_one(".col.recruit_info .work_place")
        work_place = work_place_el.get_text(strip=True) if work_place_el else None

        career_el = box.select_one(".col.recruit_info .career")
        career = career_el.get_text(strip=True) if career_el else None

        edu_el = box.select_one(".col.recruit_info .education")
        education = edu_el.get_text(strip=True) if edu_el else None

        date_el = box.select_one(".col.support_info .support_detail .date")
        deadline_text = date_el.get_text(strip=True) if date_el else None

        reg_el = box.select_one(".col.support_info .support_detail .deadlines")
        registered_text = reg_el.get_text(strip=True) if reg_el else None

        items.append(
            {
                "rec_id": rec_id,
                "rank": rank,
                "company": company,
                "title": title,
                "link": link,
                "job_sectors": job_sectors,
                "work_place": work_place,
                "career": career,
                "education": education,
                "deadline": deadline_text,
                "registered": registered_text,
            }
        )

    return items


def ensure_output_dir():
    os.makedirs("output", exist_ok=True)


def save_json(data, filename="saramin_hot100.json"):
    ensure_output_dir()
    path = os.path.join("output", filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"📁 JSON 저장 완료 → {path}")


def save_csv(data, filename="saramin_hot100.csv"):
    ensure_output_dir()
    path = os.path.join("output", filename)

    if not data:
        print("❌ 저장할 데이터가 없습니다.")
        return
    
    keys = list(data[0].keys())

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()

        for row in data:
            row_copy = row.copy()
            row_copy["job_sectors"] = ", ".join(row_copy.get("job_sectors", []))
            writer.writerow(row_copy)

    print(f"📁 CSV 저장 완료 → {path}")


if __name__ == "__main__":
    html = fetch_hot100_html()
    hot100 = parse_hot100(html)

    print(f"총 {len(hot100)}개 공고 파싱됨")
    for item in hot100:
        print(item)

    save_json(hot100)
    save_csv(hot100)