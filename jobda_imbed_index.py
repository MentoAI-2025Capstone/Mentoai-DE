import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from utils.config import Config

QDRANT_URL = Config.QDRANT_URL
QDRANT_API_KEY = Config.QDRANT_API_KEY
COLLECTION_NAME = "jobda_recruit"  

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
file_path = 'output/jobda_recruit_detail_20251125.json'

print("📂 데이터 로드 중...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# ✅ 핵심: 검색 정확도를 위해 중요한 정보를 합쳐서 임베딩용 텍스트 생성
# 예: "[하나금융티아이] 금융IT 서비스 개발 및 운영 (금융 IT) - 상세설명..."
df['text_to_embed'] = (
    "[" + df['company_name'] + "] " + 
    df['title'] + 
    " (" + df['job_sector'] + ") - " + 
    df['description'].fillna("") # 설명이 비어있을 경우 대비
)

print(f"총 {len(df)}건의 채용 공고를 로드했습니다.")

# ==========================================
# 3. 임베딩 (벡터 변환)
# ==========================================
print("🤖 모델 로딩 및 벡터 변환 중...")
# 기존과 동일한 한국어 특화 모델 사용
model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')
vectors = model.encode(df['text_to_embed'].tolist(), show_progress_bar=True)

# ==========================================
# 4. Qdrant 업로드
# ==========================================
print("☁️ Qdrant 클라우드 연결 및 업로드 중...")
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# 새 컬렉션 생성 (기존에 있으면 초기화)
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=768,           # KoSimCSE 차원
        distance=Distance.COSINE
    ),
)

points = []
for idx, row in df.iterrows():
    # 원본 데이터(Payload) 준비
    payload = {
        "company_name": row['company_name'],
        "title": row['title'],
        "rank": row['rank'],
        "job_sector": row['job_sector'],
        "work_place": row['work_place'],
        "requirements": row['requirements'],
        "link": row['link'],
        "deadline": row['deadline'],
        "description": row['description'] # 검색 결과에서 요약 보여주기 위해 저장
    }
    
    points.append(PointStruct(
        id=idx,
        vector=vectors[idx].tolist(),
        payload=payload
    ))

# 업로드 실행
client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"✅ '{COLLECTION_NAME}' 컬렉션에 업로드 완료!")