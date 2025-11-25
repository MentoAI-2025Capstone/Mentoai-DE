from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from utils.config import Config

QDRANT_URL = Config.QDRANT_URL
QDRANT_API_KEY = Config.QDRANT_API_KEY
COLLECTION_NAME = "linkareer_contest"    

# ==========================================
# 2. 클라이언트 및 모델 준비
# ==========================================
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
model = SentenceTransformer('BM-K/KoSimCSE-roberta-multitask')

# ==========================================
# 3. 진짜 검색 해보기! (query_points 사용)
# ==========================================
query_text = "it 관련 공모전 있어?" 
print(f"질문: '{query_text}' 검색 중...\n")

query_vector = model.encode(query_text).tolist()

# [수정된 부분] search 대신 query_points 사용
result_object = client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,   # 검색할 벡터
    limit=3,              # 3개만 가져오기
    with_payload=True     # 제목, 링크 등 내용도 같이 가져오기 (필수!)
)

# query_points는 결과가 .points 안에 들어있습니다.
search_results = result_object.points

# 결과 출력
for result in search_results:
    print(f"[{result.score:.4f}] {result.payload['title']}")
    print(f"   - 주최: {result.payload['organization']}")
    print(f"   - 링크: {result.payload['url']}")
    print("-" * 30)