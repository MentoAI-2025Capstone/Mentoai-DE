import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from utils.config import Config

QDRANT_URL = Config.QDRANT_URL
QDRANT_API_KEY = Config.QDRANT_API_KEY
COLLECTION_NAME = "user_profiles" 

# ==========================================
# 2. 임베딩 텍스트 생성 함수
# ==========================================
def create_embedding_text(user):
    """중첩된 유저 데이터를 하나의 설명적인 문장으로 만듭니다."""
    
    # 학교/학과/학년 정보
    university_info = (
        f"{user['university']['universityName']} "
        f"{user['university']['grade']}학년 "
        f"{user['university']['major']} 학생입니다."
    )

    # 관심 분야
    interests = ", ".join(user.get('interestDomains', []))
    interests_info = f"주요 관심 분야는 {interests}입니다."

    # 기술 스택
    tech_stacks = user.get('techStack', [])
    if tech_stacks:
        tech_list = [f"{t['name']} ({t['level']})" for t in tech_stacks]
        tech_info = f"보유 기술 스택은 {', '.join(tech_list)} 입니다."
    else:
        tech_info = "보유 기술 스택은 따로 명시되어 있지 않습니다."

    # 전체 문장 결합
    full_text = f"{university_info} {interests_info} {tech_info}"
    return full_text.strip()

# ==========================================
# 3. 데이터 로드 및 임베딩
# ==========================================
file_path = 'output/userdata.json'

print("📂 유저 데이터 로드 중...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 임베딩 텍스트 생성
texts_to_embed = [create_embedding_text(user) for user in data]

print("🤖 모델 로딩 및 벡터 변환 중...")
model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')
vectors = model.encode(texts_to_embed, show_progress_bar=True)

print(f"총 {len(data)}개의 유저 프로필 벡터화 완료.")

# ==========================================
# 4. Qdrant 업로드 (인덱싱)
# ==========================================
print("☁️ Qdrant 클라우드 연결 및 업로드 중...")
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# 컬렉션 생성 (768 차원 고정)
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

points = []
for idx, user_data in enumerate(data):
    # Payload로 원본 JSON 구조 그대로 저장
    # user['userId']를 고유 ID로 사용하거나, 인덱스를 사용
    points.append(PointStruct(
        id=user_data['userId'], # userId를 Qdrant의 고유 ID로 사용
        vector=vectors[idx].tolist(),
        payload=user_data       # 원본 유저 데이터 전체를 payload로 저장
    ))

client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"✅ '{COLLECTION_NAME}' 컬렉션에 {len(data)}개 프로필 업로드 및 인덱싱 완료!")