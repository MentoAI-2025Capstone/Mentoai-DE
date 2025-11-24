import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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


if __name__ == "__main__":
    html = fetch_hot100_html()
    hot100 = parse_hot100(html)

    print(f"총 {len(hot100)}개 공고 파싱됨")
    for item in hot100[:]:
        print(item)


