import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import xml.etree.ElementTree as ET
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import re
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import json
import sqlparse
import sys

sys.path.append("/home/site/wwwroot/UTIL")
# sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from UTIL.db_connection import get_connection
load_dotenv()

def menu3_ui():
    st.write("아래에 SQL문을 입력하고 실행해보세요.")

    col1, col2 = st.columns(2)
    with col1:
        # 서브 열
        col11,col12,col13,col13,col13  = st.columns(5)
        with col11:
            plan_button = st.button("EXPLAIN PLAN")
        with col12:
            tunuing_button = st.button("SQL Tuning")

        input_query = "SELECT * FROM SA.CUST"
        input_query = st.text_area("SQL문 입력",input_query, height=300)

    query1_plan = None

    if plan_button:
        try:
             # 입력된 SQL문의 plan 조회
            query1_plan = explain_plan(input_query)

            with col1:
                st.write("결과:")
                st.dataframe(query1_plan)
        except Exception as e:
            st.error(f"에러: {e}")


    if tunuing_button:
        # 해당 버튼 클릭시 sql_query를 OPEN AI를 통해 튜닝하고 화면에 노출
        # 튜닝된 쿼리 플랜까지 보여주기
        if query1_plan is None:
            query1_plan = explain_plan(input_query) 
        try:
            tuned_query = json.loads(tune_sql_with_openai(input_query))['sql']
            tuned_query = sqlparse.format(tuned_query, reindent=True, keyword_case='upper')
            query2_plan = explain_plan(tuned_query) 

            with col1:
                st.write("결과:")
                st.dataframe(query1_plan)

            with col2:
                st.write("결과:")
                st.code(tuned_query, language='sql')
                st.dataframe(query2_plan)
        except Exception as e:
            st.error(f"에러: {e}")



def explain_plan(SQL):
    # DB 연결
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SET SHOWPLAN_XML ON")
    cursor.execute(SQL)
    plan_xml_row = cursor.fetchone()  # 실행 계획 XML이 담긴 첫 번째(유일한) 행
    plan_xml = plan_xml_row[0]        # XML 문자열 추출
    cursor.execute("SET SHOWPLAN_XML OFF")

    # XML namespace 처리용
    ns = {'p': 'http://schemas.microsoft.com/sqlserver/2004/07/showplan'}

    root = ET.fromstring(plan_xml)

    rows = []
    for relop in root.findall(".//p:RelOp", ns):
        node_id = relop.attrib.get("NodeId")
        physical_op = relop.attrib.get("PhysicalOp")
        logical_op = relop.attrib.get("LogicalOp")
        est_rows = relop.attrib.get("EstimateRows")
        est_io = relop.attrib.get("EstimateIO")
        est_cpu = relop.attrib.get("EstimateCPU")
        avg_row_size = relop.attrib.get("AvgRowSize")
        total_cost = relop.attrib.get("EstimatedTotalSubtreeCost")

        rows.append({
            "NodeId": node_id,
            "PhysicalOp": physical_op,
            "LogicalOp": logical_op,
            "EstimateRows": est_rows,
            "EstimateIO": est_io,
            "EstimateCPU": est_cpu,
            "AvgRowSize": avg_row_size,
            "EstimatedTotalSubtreeCost": total_cost,
        })

    return pd.DataFrame(rows)



# 환경변수설정




# 1. SQL에서 테이블명 추출
def extract_table_names(sql: str) -> list[str]:
    pattern = re.compile(r'\bFROM\s+([\w\.]+)|\bJOIN\s+([\w\.]+)', re.IGNORECASE)
    matches = pattern.findall(sql)
    tables = set()
    for match in matches:
        table = match[0] if match[0] else match[1]
        tables.add(table)
    return list((i.split('.')[0], i.split('.')[1]) for i in tables)

# 2. Azure Cognitive Search에서 스키마 조회
def search_schema_for_tables(table_names: list[str]) -> list[dict]:
    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
    SEARCH_KEY = os.getenv("SEARCH_KEY")
    credential = AzureKeyCredential(SEARCH_KEY)
    client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name="db-schema-index", credential=credential)
    schema_docs = []
    for table in table_names:
        # 필터 검색도 가능하지만 간단히 텍스트 검색으로 예시 작성
        results = client.search(
        search_text="*",  # 전체 문서 중 필터링
        filter=f"table_name eq '{table[1]}'",
        top=1
    )
    
    for r in results:
        schema_docs.append(r)
    return schema_docs

# 3. OpenAI에게 튜닝 요청
def generate_prompt(sql_text: str, schema_docs: list) -> str:
    schema_text = ""
    for doc in schema_docs:
        schema_text += f"테이블명: {doc['table_name']}\n컬럼:\n"
        for col in doc["columns"]:
            nullable = "NULL" if col["is_nullable"].lower() == "yes" else "NOT NULL"
            schema_text += f" - {col['name']} ({col['data_type']}, {nullable})\n"
        schema_text += "\n"
    prompt = f"""
                아래 DB 스키마 정보를 참고하여 SQL 쿼리를 튜닝하세요. 인덱스를 활용하고, 불필요한 SELECT * 를 제거하며, 조건을 최적화해 주세요.

                DB 스키마:
                {schema_text}

                튜닝할 SQL:
                {sql_text}

                해당 형태로 결과 출력:
                sql : <튜닝된 SQL 쿼리>
                이유 : <튜닝 이유>
            """
    return prompt

def tune_sql_with_openai(sql_text: str) -> str:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    OPENAI_ENDPOINT =  os.getenv("OPENAI_ENDPOINT")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
    client = AzureOpenAI(
                            api_key=OPENAI_API_KEY,
                            azure_endpoint=OPENAI_ENDPOINT,
                            api_version=OPENAI_API_VERSION
                        )
    tables = extract_table_names(sql_text)
    schema_docs = search_schema_for_tables(tables)
    prompt = generate_prompt(sql_text, schema_docs)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": """당신은 숙련된 숙련된 SQL 튜닝 전문가입니다.  
                                            아래 SQL 쿼리를 성능 최적화하세요.  

                                            출력 형식은 반드시 다음 JSON 형태로 하세요:  
                                            {
                                            "sql": "튜닝된 SQL 쿼리문(큰따옴표 안에 텍스트로)",
                                            "이유": "튜닝한 이유를 간결하게 설명"
                                            }  

                                            - SQL 쿼리만 따옴표 안에 넣고, JSON 형식으로 정확히 출력하세요.  
                                            - JSON 이외의 다른 텍스트, 설명, 코드 블록 등은 포함하지 마세요.  
                                            - 변경사항이 없으면 원본 쿼리를 그대로 "sql" 값에 넣고, 이유에는 '변경사항 없음'이라고 작성하세요."""},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()
    
