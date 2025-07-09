import os
import pyodbc
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import pandas as pd
import sys
from dotenv import load_dotenv

sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from db_connection import get_connection

load_dotenv(r"D:\MS AI 개발역량 향상과정_박선아\MVP\UTIL\.env")  # .env 파일에서 환경변수 로드

# Azure Search 환경변수
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = "db-schema-index"

# 스키마 크롤링
def crawl_schema(cursor):
    query = """
    SELECT
        TABLE_SCHEMA,
        TABLE_NAME,
        COLUMN_NAME,
        DATA_TYPE,
        IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
    """
    df = pd.read_sql(query, cursor.connection)
    return df

# AI Search 문서 생성
def create_documents(df):
    grouped = df.groupby(["TABLE_SCHEMA", "TABLE_NAME"])
    docs = []
    for (schema, table), group in grouped:
        columns = []
        for _, row in group.iterrows():
            columns.append({
                "name": row.COLUMN_NAME,
                "data_type": row.DATA_TYPE,
                "is_nullable": row.IS_NULLABLE
            })
        doc = {
            "schema_name": schema,
            "table_name": table,
            "columns": columns
        }
        docs.append(doc)
    return docs

# 업로드
def upload_documents(docs):
    credential = AzureKeyCredential(SEARCH_KEY)
    client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=credential)
    result = client.upload_documents(documents=docs)
    print(f"업로드 완료. 결과: {result}")

# 실행
if __name__ == "__main__":
    conn = get_connection()
    df_schema = crawl_schema(conn.cursor())
    documents = create_documents(df_schema)
    upload_documents(documents)
