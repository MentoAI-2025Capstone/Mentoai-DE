import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from utils.config import Config

QDRANT_URL = Config.QDRANT_URL
QDRANT_API_KEY = Config.QDRANT_API_KEY
COLLECTION_NAME = "linkareer_contest"     

# ==========================================
# 2. 데이터 로드 및 임베딩 (아까 성공한 부분)
# ==========================================
file_path = 'output/linkareer_partial_20251125_221643.json'

print("📂 데이터 로드 중...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
# 제목 + 주최사 + 카테고리를 합쳐서 풍부한 정보를 임베딩합니다.
df['text_to_embed'] = df['title'] + " (주최: " + df['organization'] + ") - " + df['category']

print("🤖 모델 로딩 및 벡터 변환 중...")
model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')
vectors = model.encode(df['text_to_embed'].tolist(), show_progress_bar=True)

# ==========================================
# 3. Qdrant 클라우드 연결 및 업로드
# ==========================================
print("☁️ Qdrant 클라우드 연결 중...")
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# 컬렉션 생성 (기존에 있으면 삭제하고 새로 만듭니다 - 초기화용)
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=768,           # 모델 차원과 일치 (필수!)
        distance=Distance.COSINE
    ),
)

print(f"🚀 {len(df)}개의 데이터를 업로드합니다...")

points = []
for idx, row in df.iterrows():
    # JSON의 모든 정보를 Payload(메타데이터)로 함께 저장합니다.
    # 이렇게 해야 나중에 검색했을 때 원본 링크나 마감일도 알 수 있습니다.
    payload = {
        "title": row['title'],
        "url": row['url'],
        "category": row['category'],
        "organization": row['organization'],
        "deadline": row['deadline']
    }
    
    points.append(PointStruct(
        id=idx,                 # 고유 ID (0, 1, 2...)
        vector=vectors[idx].tolist(), # 벡터 값
        payload=payload         # 원본 데이터
    ))

# 실제 업로드 수행
operation_info = client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print("✅ 업로드 및 인덱싱 완료!")
print(f"상태: {operation_info.status}")