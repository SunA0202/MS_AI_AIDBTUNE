import pyodbc
import os
from dotenv import load_dotenv

def get_connection():
    """
    Azure SQL Database 연결 반환 함수.
    환경변수를 이용하도록 권장합니다.
    """
    load_dotenv()  # .env 파일에서 환경변수 로드
    
    # 환경변수 읽기
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DB")
    username = os.getenv("SQL_USER")
    password = os.getenv("SQL_PASSWORD")

    # 연결 문자열 구성
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    # DB 연결
    conn = pyodbc.connect(conn_str)


    return conn