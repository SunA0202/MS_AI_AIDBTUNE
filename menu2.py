import streamlit as st
import pandas as pd
import datetime
import sqlparse
import re
from openai import AzureOpenAI
import sys
import xml.etree.ElementTree as ET
import xmltodict
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import json
import os
from dotenv import load_dotenv

sys.path.append("/home/site/wwwroot/UTIL")
# sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from db_connection import get_connection

load_dotenv()

def menu2_ui():
    col1, col2 = st.columns(2)
    # 오늘 날짜를 기본값으로 설정
    with col1:
        tuning_button = st.button("Table Tuning")
        col11, col12 = st.columns(2)
        today = datetime.date.today()
        # 날짜 2개 따로 입력
        start_date = col11.date_input("시작 날짜", today-datetime.timedelta(days=30))
        end_date = col12.date_input("종료 날짜", today)

        # 유효성 검사
        if start_date > end_date:
            st.error("❌ 시작 날짜는 종료 날짜보다 앞서야 합니다.")
        else:
            st.success(f"선택한 기간: {start_date} ~ {end_date}")

    if tuning_button:
        # 쿼리 수행 이력 조회 및 통계 진행
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
                        SELECT
                            qt.text as query_text, 
                            qs.execution_count,
                            qs.total_logical_reads,
                            qs.total_logical_writes,
                            qp.query_plan
                        FROM
                            sys.dm_exec_query_stats qs
                            CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) qt
                            CROSS APPLY sys.dm_exec_query_plan(qs.plan_handle) qp
                        WHERE qs.last_execution_time >= '{start_date}'
                            AND qs.last_execution_time < '{end_date+datetime.timedelta(days=1)}'
                            AND qt.text LIKE '%--test5%'
                            AND qt.text NOT LIKE '%SYS.DM_EXEC_SQL_TEXT%'
                        """)   
        
        query_stats = cursor.fetchall()
        qsDF = pd.DataFrame([tuple(row) for row in query_stats], columns=[col[0] for col in cursor.description])
        qsDF['query_text'] = qsDF['query_text'].apply(lambda x: normalize_sql(x))

        # cost 컬럼 추가
        qsDF['cost'] = qsDF['query_plan'].apply(extract_cost_from_plan)

        # 그룹별 집계
        grouped = qsDF.groupby('query_text').agg(
            count=('execution_count', 'sum'),
            max_reads=('total_logical_reads', 'max'),
            max_writes=('total_logical_writes', 'max'),
            max_cost=('cost', 'max')
        ).reset_index()

        # cost 최대인 행 추출 (optional, query_plan 포함)
        idx = qsDF.groupby('query_text')['cost'].idxmax()
        max_cost_rows = qsDF.loc[idx, ['query_text', 'query_plan', 'cost']]

        # grouped에 query_plan 붙이기 (비용 최대인 query_plan)
        result = grouped.merge(max_cost_rows[['query_text', 'query_plan']], on='query_text').sort_values(by='count', ascending=False).head(10)
        result['query_plan'] = result['query_plan'].apply(lambda x: plan_parse(x) if isinstance(x, str) else x)   

        with col1:
            # 결과를 Streamlit에 표시
            st.markdown(f'<div style="margin-bottom: 0px; font-weight: bold; font-size: 30px; text-align: center;">쿼리 수행 이력 통계</div>', unsafe_allow_html=True)
            col_res = result[['query_text','count']]    
            col_res['query_text'] = col_res['query_text'].apply(lambda x: extract_sql_statement(x))
            st.dataframe(col_res.reset_index(drop=True))
        with col2:    
            st.markdown(f'<div style="margin-bottom: 0px; font-weight: bold; font-size: 30px; text-align: center;">DB 테이블 최적화 목록</div>', unsafe_allow_html=True)
            tb_tuned_result = tune_sql_with_openai(result)

            # DataFrame으로 변환
            df = pd.DataFrame(json.loads(tb_tuned_result))

            for idx, row in df.head(3).iterrows():
                st.code(row['sql'], language='sql')
                st.write("**설명:**", row['sql설명'])
                st.write("**이유:**", row['이유'])  
                st.markdown("---")
            
     
def normalize_sql(sql):
    sql = sqlparse.format(sql, strip_comments=True)
    # 모두 대문자
    sql = sql.upper()
    # 줄바꿈과 탭은 공백으로 대체
    sql = re.sub(r'[\n\t\r;]+', ' ', sql)
    # 공백 여러 개는 하나로 줄이기
    sql = re.sub(r'\s+', ' ', sql)
    # 양쪽 공백 제거
    return sql.strip()

def extract_cost_from_plan(xml_text):
    try:
        root = ET.fromstring(xml_text)
        # TotalCost 속성 추출 (없으면 0)
        total_cost = root.attrib.get('TotalCost')
        if total_cost is not None:
            return float(total_cost)
        # 또는 RelOp Cost 속성 중 최대값 찾아도 됨
        costs = [float(node.attrib.get('Cost', 0)) for node in root.iter('RelOp')]
        if costs:
            return max(costs)
        return 0.0
    except Exception:
        return 0.0

def plan_parse(plan_xml):
    """
    XML 문자열을 JSON 문자열로 변환합니다.

    Args:
        xml_str (str): XML 문자열
        pretty (bool): True이면 보기 좋게 들여쓰기를 추가함

    Returns:
        str: JSON 문자열
    """
    # xmltodict로 파싱
    parsed_dict = xmltodict.parse(plan_xml)['ShowPlanXML']['BatchSequence']['Batch']['Statements']['StmtSimple']

    # 튜닝에 필요한 부분만 추출
    result = {}

    keys_to_extract = [
        '@StatementId',
        "@ParentObjectId",
        "@StatementParameterizationType",
        "@RetrievedFromCache",
        "@StatementSubTreeCost",
        "@StatementEstRows",
        "@StatementOptmLevel",
        "@StatementOptmEarlyAbortReason",
        "@CardinalityEstimationModelVersion"
    ]

    if type(parsed_dict) != list:
        parsed_dict = [parsed_dict]

    for i in range(len(parsed_dict)):
        result[i] = {}
        # 최상위 Statement 정보 추출
        for key in keys_to_extract:
            if key in parsed_dict[i]:
                result[i][key] = parsed_dict[i][key]
        
        # QueryPlan 내부 필요한 키만 추출
        query_plan_keys = [
            "@NonParallelPlanReason",
            "@CachedPlanSize",
            "@CompileTime",
            "@CompileCPU",
            "@CompileMemory",
            "MemoryGrantInfo",
            "OptimizerHardwareDependentProperties",
        ]
        result[i]["QueryPlan"] = {}
        for key in query_plan_keys:
            if key in parsed_dict[i]["QueryPlan"]:
                result[i]["QueryPlan"][key] = parsed_dict[i]["QueryPlan"][key]
        # RelOp 재귀 추출
        relop_data = extract_relop_fields(parsed_dict[i]["QueryPlan"])
        result[i]["QueryPlan"]["RelOp"] = relop_data

    return result

def extract_relop_fields(node):
    """
    RelOp가 dict 또는 list일 수 있으며, 리스트일 때 순차적으로 처리
    """
    results = []

    relops = node.get("RelOp")
    if not relops:
        return results

    # RelOp가 list인지 dict인지 구분
    if isinstance(relops, dict):
        relops = [relops]

    for relop_node in relops:
        # 추출할 키
        keys_to_extract = [
            "@NodeId",
            "@PhysicalOp",
            "@LogicalOp",
            "@EstimateRows",
            "@EstimateIO",
            "@EstimateCPU",
            "@AvgRowSize",
            "@EstimatedTotalSubtreeCost",
            "@Parallel",
            "@EstimateRebinds",
            "@EstimateRewinds",
            "@EstimatedExecutionMode"
        ]

        extracted = {}
        for k in keys_to_extract:
            if k in relop_node:
                extracted[k] = relop_node[k]

        if extracted:
            results.append(extracted)

        # 자식 RelOp 순차 처리
        for child_key, child_value in relop_node.items():
            if isinstance(child_value, dict):
                # 자식이 dict면 재귀 처리
                child_results = extract_relop_fields(child_value)
                results.extend(child_results)
            elif isinstance(child_value, list):
                # 자식이 list면 하나씩 순서대로 재귀 처리
                for item in child_value:
                    if isinstance(item, dict):
                        child_results = extract_relop_fields(item)
                        results.extend(child_results)

    return results

def search_schema_for_schema(schema_name: str) -> list[dict]:
    """
    Azure Cognitive Search에서 특정 스키마에 속한 모든 테이블 스키마 문서 조회
    """
    load_dotenv()
    SEARCH_KEY = os.getenv("SEARCH_KEY")
    SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")

    credential = AzureKeyCredential(SEARCH_KEY)
    client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name="db-schema-index", credential=credential)
    
    schema_docs = []

    # schema_name으로 필터
    results = client.search(
        search_text="*",  # 전체 문서 중
        filter=f"schema_name eq '{schema_name}'",
        top=1000  # 최대 1000개까지 가져오기 (필요 시 더 큰 값으로 조정)
    )

    for r in results:
        schema_docs.append(r)

    return schema_docs


# OpenAI에게 튜닝 요청
def generate_prompt(sql_text: str, schema_docs: list) -> str:
    schema_text = ""
    for doc in schema_docs:
        schema_text += f"테이블명: {doc['table_name']}\n컬럼:\n"
        for col in doc["columns"]:
            nullable = "NULL" if col["is_nullable"].lower() == "yes" else "NOT NULL"
            schema_text += f" - {col['name']} ({col['data_type']}, {nullable})\n"
        schema_text += "\n"
    prompt = f"""
                아래 DB 스키마 정보와 쿼리 이력을 참고하여 테이블을 최적화 하세요.
                필요한 인덱스 및 컬럼, 파티션은 생성하고
                불필요하거나 더 사용되지 않는 인덱스 및 컬럼은 지울 수 있게 DDL을 만들어주세요
                파티셔닝에 대해서도 고려해주세요
                데이터가 많아지면 CAMP_TGT 같이 수행 이력을 적재하는 테이블을 데이터 삭제도 필요합니다
                쿼리 이력이 없으면 결과에 수정 사항이 없다고 말해주세요.

                DB 스키마:
                {schema_text}

                가장 많이 실행된 쿼리의 플랜:
                {sql_text}

                해당 형태로 결과 출력:
                sql : <튜닝된 SQL 쿼리>
                이유 : <튜닝 이유>
            """
    return prompt

def tune_sql_with_openai(sql_text: str) -> str:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")

    
    client = AzureOpenAI(
                            api_key=OPENAI_API_KEY,
                            azure_endpoint=OPENAI_ENDPOINT,
                            api_version=OPENAI_API_VERSION
                        )
    schema_docs = search_schema_for_schema('SA')
    prompt = generate_prompt(sql_text, schema_docs)
   
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": """당신은 숙련된 숙련된 DB 튜닝 전문가입니다.  

                                            출력 형식은 반드시 다음 list 형태로 하세요:  
                                            [
                                                {
                                                "sql": "DB 테이블 최적화를 위해 필요한 DDL 쿼리문(큰따옴표 안에 텍스트로)",
                                                "sql설명": "DB 테이블 최적화를 위해 필요한 DDL 쿼리문(큰따옴표 안에 텍스트로)",
                                                "이유": "튜닝한 이유를 간결하게 설명"
                                                },
                                                {
                                                "sql": "DB 테이블 최적화를 위해 필요한 DDL 쿼리문(큰따옴표 안에 텍스트로)",
                                                "sql설명": "DB 테이블 최적화를 위해 필요한 DDL 쿼리문(큰따옴표 안에 텍스트로)",
                                                "이유": "튜닝한 이유를 간결하게 설명"
                                                }, ...
                                            ]
 

                                            - SQL 쿼리만 따옴표 안에 넣고, JSON 형식으로 정확히 출력하세요.  
                                            - JSON 이외의 다른 텍스트, 설명, 코드 블록 등은 포함하지 마세요.  
                                            - 변경사항이 없으면 [{"sql":"변경 사항 없음","sql설명":"변경 사항 없음","이유":"변경 사항 없음"}] 이렇게 출력해주세요."""},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

def extract_sql_statement(s):
    keywords = ["SELECT", "INSERT", "DELETE", "UPDATE"]
    positions = []
    
    # 각 키워드가 등장하는 인덱스 저장
    for kw in keywords:
        idx = s.upper().find(kw)
        if idx != -1:
            positions.append(idx)
    
    # 키워드가 하나도 없으면 원본 반환
    if not positions:
        return s
    
    # 가장 앞에 등장하는 키워드의 위치
    first_idx = min(positions)
    return s[first_idx:].lstrip()



