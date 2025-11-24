import sys
import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.saramin.co.kr",
}


def fetch_detail_html(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.text


def _extract_section_by_keyword(soup: BeautifulSoup, keywords):
    """
    '자격요건', '우대사항' 같은 키워드가 들어간 제목 근처에서
    <ul><li> 목록을 찾아 리스트로 반환.
    """
    if isinstance(keywords, str):
        keywords = [keywords]

    target_heading = None

    def match_tag(tag):
        if tag.name not in ["h2", "h3", "h4", "strong", "span", "p"]:
            return False
        text = tag.get_text(strip=True)
        if not text:
            return False
        return any(k in text for k in keywords)

    target_heading = soup.find(match_tag)
    if not target_heading:
        return []

    # 우선 같은 블록 안의 ul, 없으면 다음 ul
    container = target_heading.parent
    ul = container.find("ul")
    if not ul:
        ul = target_heading.find_next("ul")

    items = []
    if ul:
        for li in ul.find_all("li"):
            txt = li.get_text(" ", strip=True)
            if txt:
                items.append(txt)
    return items


def parse_detail(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # 제목 / 회사명 (relay view 상단 영역 기준, 안 맞으면 클래스 수정 필요)
    title_tag = soup.find("h1", class_="title") or soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None

    company_tag = soup.find("a", class_="company") or soup.find("strong", class_="corp_name")
    company = company_tag.get_text(strip=True) if company_tag else None

    # 자격요건 / 우대사항 / 담당업무 등
    required_conds = _extract_section_by_keyword(soup, ["자격요건", "지원자격"])
    preferred_conds = _extract_section_by_keyword(soup, ["우대사항", "우대조건"])
    duties = _extract_section_by_keyword(soup, ["담당업무", "주요업무"])

    # 모집/접수 기간 텍스트 (블록 전체를 한 줄로 가져오는 식)
    period_tag = soup.find(
        lambda tag: tag.name in ["li", "p", "span", "div"]
        and tag.get_text(strip=True)
        and ("모집기간" in tag.get_text() or "접수기간" in tag.get_text())
    )
    period_text = period_tag.get_text(" ", strip=True) if period_tag else None

    # 기타 근무조건 비슷한 블록도 필요하면 비슷한 방식으로 추가 가능
    # ex) _extract_section_by_keyword(soup, ["급여", "근무조건"])

    return {
        "title": title,
        "company": company,
        "required_conditions": required_conds,
        "preferred_conditions": preferred_conds,
        "duties": duties,
        "period": period_text,
    }


def main():
    if len(sys.argv) < 2:
        print("사용법: python detail_recruit_saramin.py <공고 URL>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"🔍 상세 페이지 크롤링: {url}")

    html = fetch_detail_html(url)
    data = parse_detail(html)

    # 서버 연동용이라면 JSON으로 직렬화해서 반환하는 형태를 맞춰두면 좋음
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()