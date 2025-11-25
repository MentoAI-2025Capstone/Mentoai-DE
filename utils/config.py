from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Saramin
    SARAMIN_API_KEY = os.getenv("SARAMIN_API_KEY")

    # Linkareer
    LINKAREER_QUERY_HASH = os.getenv("LINKAREER_QUERY_HASH")

    # DB 정보
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_DB = os.getenv("MYSQL_DB")

    #Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")