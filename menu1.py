import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
import matplotlib.pyplot as plt
import base64
import sys
from dotenv import load_dotenv

sys.path.append("/home/site/wwwroot/UTIL")
# sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from db_connection import get_connection


load_dotenv()

def menu1_ui():
    col1, col2 = st.columns(2) 

    # DB 연결
    conn = get_connection()
    cursor = conn.cursor()

    schem_nm = 'SA' #스키마는 SA가 default

    # 1. 테이블 목록 조회
    cursor.execute("""
        SELECT 
            TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
            AND TABLE_SCHEMA = 'SA'
    """)
    tables = [row[0] for row in cursor.fetchall()]

    # 2. 테이블 컬럼, FK 정보 수집
    edges = []

    for table in tables:
        cursor.execute(f"""SELECT 
                            tp.name AS table_name, 
                            tr.name AS referenced_table, 
                            cp.name AS fk_column
                        FROM sys.foreign_keys fk, 
                            sys.foreign_key_columns fkc, 
                            sys.tables tp, sys.columns cp, 
                            sys.tables tr
                        WHERE fk.object_id = fkc.constraint_object_id 
                            AND fkc.parent_object_id = tp.object_id 
                            AND fkc.parent_object_id = cp.object_id 
                            AND fkc.parent_column_id = cp.column_id 
                            AND fkc.referenced_object_id = tr.object_id 
                            AND tp.name = '{table}'""")
        fks = cursor.fetchall()
        for fk in fks:
            # fk 구조: (id, seq, table, from, to, on_update, on_delete, match)
            # from: FK가 걸린 컬럼 (현재 테이블)
            # table: 참조 테이블 이름
            # to: 참조 테이블 컬럼
            edges.append(Edge(source=table, target=fk[1], label=f"FK_{fk[2]}", font={"size": 13, "face": "arial", "color": "red"}))
            

    # 3. 노드 생성 (테이블명 + 컬럼 나열)  
    nodes = []
    for table in tables:  
        df_to_image(get_table_schema(cursor, table,schem_nm)[['name','type']], f"./static/{table}.png")  
        nodes.append(Node(id=table, label=wrap_label(table),shape="image", 
                          size=50, color="#f0a500",
                          image=image_to_base64(f"./static/{table}.png"),
                          font={"size": 15, "face": "arial", "color": "black", "bold": True, "vadjust": 0}))
   
    # 4. 그래프 설정   
    config = Config(
                    width=1000,
                    height=700,
                    directed=False,
                    physics={
                        "enabled": True,
                        "barnesHut": {
                            "gravitationalConstant": -20000,  # 더 큰 음수로 퍼짐을 강하게
                            "centralGravity": 0.1,           # 0에 가까울수록 퍼짐
                            "springLength": 300,             # 연결 거리
                            "springConstant": 0.02           # 연결 강도
                        },
                        "minVelocity": 0.75
                    },
                    hierarchical=False,
                    )

    with col1: 
        # 5. 그래프 출력
        global selected
        selected = agraph(nodes=nodes, edges=edges, config=config) 
        st.markdown(
                """
                <style>
                div[data-testid="stVerticalBlock"] > div:first-child {
                    border-right: 2px solid #ddd;
                    padding-right: 10px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

    with col2:                    
        idx_query = """
            SELECT 
                ind.name AS index_name,
                ind.type_desc AS index_type,
                ind.is_primary_key,
                ind.is_unique,
                col.name AS column_name
            FROM sys.indexes ind
            INNER JOIN sys.index_columns ic
                ON ind.object_id = ic.object_id AND ind.index_id = ic.index_id
            INNER JOIN sys.columns col
                ON ic.object_id = col.object_id AND ic.column_id = col.column_id
            INNER JOIN sys.tables t
                ON ind.object_id = t.object_id
            INNER JOIN sys.schemas s
                ON t.schema_id = s.schema_id
            WHERE t.name = ? AND s.name = ?
            ORDER BY ind.name, ic.key_ordinal
            """
        cursor.execute(idx_query, (selected, 'SA'))     
        rows = cursor.fetchall()
        columns = ["index_name", "index_type", "is_primary_key", "is_unique", "column_name"]
        idxs = pd.DataFrame([tuple(row) for row in rows], columns=columns)

        if selected:
            st.markdown(f'<div style="margin-bottom: 0px; font-weight: bold; font-size: 30px; text-align: center;">{selected}</div>', unsafe_allow_html=True)
            st.markdown('<div style="margin-bottom: 0px; font-weight: bold;">테이블 스키마</div>', unsafe_allow_html=True)
            with st.spinner("스키마를 조회 중입니다..."):
                render_hover_table(get_table_schema(cursor, selected,schem_nm))
                if len(idxs) != 0:
                    st.markdown('<div style="margin-bottom: 0px; font-weight: bold;">인덱스</div>', unsafe_allow_html=True)
                    render_hover_table(idxs)   



def render_hover_table(df):    
    # CSS 스타일
    styles = """
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 0 auto;
        margin-left: 0;
    }
    th {
        background-color: #f2f2f2;
    }
    th, td {
        border: 1px solid #ccc;
        padding: 8px 12px;
        text-align: center !important;
    }
    tr:hover {
        background-color: #add8e6; /* 연한 파랑색 */
    }

    </style>
    """

    # DataFrame을 HTML로 변환
    table_html = df.to_html(index=False, escape=False)

    st.markdown(styles, unsafe_allow_html=True)
    st.write(table_html, unsafe_allow_html=True)


def wrap_label(text, line_length=5):
    """
    긴 문자열을 일정 길이마다 <br> 태그로 줄바꿈 처리
    """
    if not text:
        return ""
    return "\n".join(
        [text[i:i+line_length] for i in range(0, len(text), line_length)]
    )



def get_table_schema(cursor, table_name: str, schema_name: str = 'dbo') -> pd.DataFrame:
    query = """
    SELECT 
        COLUMN_NAME AS name,
        DATA_TYPE AS type,
        CHARACTER_MAXIMUM_LENGTH AS max_length,
        IS_NULLABLE AS is_nullable
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = ? AND TABLE_SCHEMA = ?
    ORDER BY ORDINAL_POSITION
    """
    cursor.execute(query, (table_name, schema_name))
    rows = cursor.fetchall()
    columns = ["name", "type", "max_length", "is_nullable"]
    return pd.DataFrame([tuple(row) for row in rows], columns=columns) 

def df_to_image(df: pd.DataFrame, filename: str):
    fig, ax = plt.subplots(figsize=(len(df.columns), len(df) * 0.2))
    ax.axis('off')
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='center',
                     loc='center',
                     edges='horizontal')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)


def image_to_base64(image_path):
    """
    절대경로 이미지를 base64로 변환해 data URI로 반환
    """
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded}"