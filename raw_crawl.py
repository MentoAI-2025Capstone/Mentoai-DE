import requests

url = "https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=list&rec_idx=52302190"
html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

with open("detail_raw.html", "w", encoding="utf-8") as f:
    f.write(html)