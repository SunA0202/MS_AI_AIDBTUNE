from datetime import datetime
import random
import sys

sys.path.append("/home/site/wwwroot")
# sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from UTIL.db_connection import get_connection

# DB 연결
conn = get_connection()
cursor = conn.cursor()

# 테이블 초기화
    # 외래키 삭제
# cursor.execute("ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CAMP")
# cursor.execute("ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CUST")
# cursor.execute("ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CONT")
    # 기존 테이블 삭제
cursor.execute("DROP TABLE IF EXISTS SA.CAMP_TGT")
cursor.execute("DROP TABLE IF EXISTS SA.CAMP_BAS")
conn.commit()

# 테이블 생성
cursor.execute(""" --test5 
    CREATE TABLE SA.CAMP_BAS (
    ROW_ID INT IDENTITY(1,1) PRIMARY KEY,                -- 행 ID 
    CAMP_ID VARCHAR(10) UNIQUE NOT NULL,                 -- 캠페인 ID
    CAMP_NM NVARCHAR(100) NOT NULL,                      -- 캠페인명
    CAMP_CRET_DT DATE NOT NULL,                          -- 캠페인 생성일
    CAMP_EXE_DT DATE,                                    -- 캠페인 수행일
    CAMP_STTUS NVARCHAR(50),                             -- 캠페인 상태
    CRET_NM VARCHAR(20),                                 -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),          -- 생성일시
    CHG_NM VARCHAR(20),                                  -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME()            -- 변경일시
)
""")
conn.commit()

cursor.execute(""" --test5 
    CREATE TABLE SA.CAMP_TGT (
    ROW_ID INT IDENTITY(1,1) PRIMARY KEY,               -- 행 ID (AUTO_INCREMENT)
    CAMP_TGT_ID VARCHAR(50) NOT NULL,                   -- 캠페인대상 ID
    CAMP_ID VARCHAR(10) NOT NULL,                       -- 캠페인 ID
    CUST_ID VARCHAR(10) NOT NULL,                       -- 고객 ID
    SVC_CONT_ID VARCHAR(12),                            -- 회선 ID
    CAMP_ST_DT DATETIME2 NOT NULL,                      -- 수행시작일시
    CAMP_END_DT DATETIME2 NOT NULL,                     -- 수행종료일시
    CAMP_RSLT NVARCHAR(10),                             -- 캠페인결과
    CRET_NM VARCHAR(20),                                -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),         -- 생성일시
    CHG_NM VARCHAR(20),                                 -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME(),          -- 변경일시
    CONSTRAINT FK_CAMP_TGT_CUST FOREIGN KEY (CUST_ID) REFERENCES SA.CUST(CUST_ID),
    CONSTRAINT FK_CAMP_TGT_CONT FOREIGN KEY (SVC_CONT_ID) REFERENCES SA.CONT(SVC_CONT_ID),
    CONSTRAINT FK_CAMP_TGT_CAMP FOREIGN KEY (CAMP_ID) REFERENCES SA.CAMP_BAS(CAMP_ID)
)
""")
conn.commit()
cursor.close()
conn.close()

print("✅ 캠페인 기본 및 대상 테이블 생성 완료")
