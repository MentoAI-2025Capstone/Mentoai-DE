from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from utils.config import Config

QDRANT_URL = Config.QDRANT_URL
QDRANT_API_KEY = Config.QDRANT_API_KEY
COLLECTION_NAME = "jobda_recruit" 

# ==========================================
# 2. 클라이언트 연결
# ==========================================
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')

# ==========================================
# 3. 검색 테스트
# ==========================================
# 예: "클라우드"나 "금융" 관련 검색
query_text = "금융권 개발자 채용 있어?"
print(f"🔍 질문: '{query_text}' 검색 중...\n")

query_vector = model.encode(query_text).tolist()

# 검색 실행 (query_points 사용)
result = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=3,
    with_payload=True
)

# 결과 출력
if not result.points:
    print("❌ 검색 결과가 없습니다. 컬렉션 이름(COLLECTION_NAME)을 확인해주세요!")
else:
    for i, hit in enumerate(result.points):
        print(f"[{i+1}] {hit.payload.get('company_name', '회사명없음')} - {hit.payload.get('title', '제목없음')}")
        print(f"    - 직무: {hit.payload.get('job_sector')}")
        print(f"    - 마감: {hit.payload.get('deadline')}")
        print(f"    - 링크: {hit.payload.get('link')}")
        print(f"    - 유사도 점수: {hit.score:.4f}")
        print("-" * 40)