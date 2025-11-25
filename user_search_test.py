from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from utils.config import Config

QDRANT_URL = Config.QDRANT_URL
QDRANT_API_KEY = Config.QDRANT_API_KEY
COLLECTION_NAME = "user_profiles"

# ==========================================
# 2. 클라이언트 연결 및 검색
# ==========================================
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')

query_text = "노드를 잘 다루는 백엔드 개발자를 찾아줘"
print(f"🔍 질문: '{query_text}' 검색 중...\n")

query_vector = model.encode(query_text).tolist()

result = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=3,
    with_payload=True
)

# 결과 출력
for i, hit in enumerate(result.points):
    user_id = hit.payload.get('userId', 'N/A')
    major = hit.payload.get('university', {}).get('major', 'N/A')
    interests = ', '.join(hit.payload.get('interestDomains', []))
    
    print(f"[{i+1}] 유저 ID: {user_id} (점수: {hit.score:.4f})")
    print(f"    - 학과/관심: {major} / {interests}")
    tech_stacks = [f"{t['name']}({t['level']})" for t in hit.payload.get('techStack', [])]
    print(f"    - 기술 스택: {', '.join(tech_stacks) if tech_stacks else '없음'}")
    print("-" * 40)