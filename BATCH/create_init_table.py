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
# cursor.execute("ALTER TABLE SA.CONT DROP CONSTRAINT FK_CONT_CUST")
cursor.execute("ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CAMP")
cursor.execute("ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CUST")
cursor.execute("ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CONT")

cursor.execute("DROP TABLE IF EXISTS SA.CONT")
cursor.execute("DROP TABLE IF EXISTS SA.CUST")
cursor.execute("DROP TABLE IF EXISTS SA.CAMP_TGT")
cursor.execute("DROP TABLE IF EXISTS SA.CAMP_BAS")
conn.commit()

# 테이블 생성
cursor.execute(""" 
    CREATE TABLE SA.CUST (
    ROW_ID INT PRIMARY KEY,                        -- 행 ID
    CUST_ID VARCHAR(10) UNIQUE NOT NULL,                  -- 고객 ID
    CUST_NM NVARCHAR(10) NOT NULL,                  -- 고객명
    REGISTER_DT DATETIME2 NOT NULL,                 -- 가입일자
    MOBILE VARCHAR(20),                            -- 핸드폰번호
    EMAIL VARCHAR(100),                            -- 이메일
    ADRESS NVARCHAR(255),                           -- 주소
    BIRTH_DT DATE,                                 -- 생년월일
    CAMP_NM NVARCHAR(100),                          -- 캠페인명
    CAMP_EXE_DT DATETIME2,                         -- 캠페인 수행일
    CAMP_RSLT NVARCHAR(10),                         -- 캠페인 결과
    CRET_NM VARCHAR(20),                           -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),   -- 생성일시
    CHG_NM VARCHAR(20),                            -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME()     -- 변경일시
)
""")
conn.commit()

cursor.execute(""" 
    CREATE TABLE SA.CONT (
    ROW_ID INT PRIMARY KEY,                           -- 행 ID
    SVC_CONT_ID VARCHAR(12) UNIQUE NOT NULL,                 -- 회선 ID
    CUST_ID VARCHAR(10) NOT NULL,                      -- 고객 ID
    CUST_NM NVARCHAR(10) NOT NULL,                      -- 고객명
    REGISTER_DT DATETIME2 NOT NULL,                     -- 가입일자
    SVC_NO_ID VARCHAR(20),                             -- 서비스 번호
    BPROD_NM NVARCHAR(100),                             -- 가입상품명
    LOB VARCHAR(10),                                   -- 가입 그룹
    CONT_STTUS NVARCHAR(10),                            -- 회선 상태
    CAMP_NM NVARCHAR(100),                              -- 캠페인명
    CAMP_EXE_DT DATETIME2,                             -- 캠페인 수행일
    CAMP_RSLT NVARCHAR(10),                             -- 캠페인 결과
    CRET_NM VARCHAR(20),                               -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),       -- 생성일시
    CHG_NM VARCHAR(20),                                -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME(),         -- 변경일시
    CONSTRAINT FK_CONT_CUST FOREIGN KEY (CUST_ID) REFERENCES SA.CUST(CUST_ID)
)
""")
conn.commit()


# 이름 리스트
name_list = [
    "김민준", "이서연", "박지후", "최예린", "정하준",
    "윤도윤", "조은서", "한유진", "서지호", "오하린",
    "배수아", "권지민", "임현우", "백서준", "홍지아",
    "양채원", "강시우", "문도현", "신가은", "노윤서",
    "오은우", "남유나", "유정민", "황서윤", "송다은"
]

# CUST 데이터 생성 및 삽입
cust_data = []
for i in range(1, 21):  # 20명
    cust_id = f"CUST{i:03d}"
    cust_nm = random.choice(name_list)
    row = (
        i,  # ROW_ID
        cust_id,
        cust_nm,
        datetime.now(),
        f"010-1234-{1000+i}",
        f"user{i}@email.com",
        f"서울시 중구 {i}길",
        datetime(1980+i % 30, 1, 1),
        None,
        None,
        None,
        "admin",
        datetime.now(),
        None,
        None
    )
    cust_data.append(row)

cursor.executemany(""" 
    INSERT INTO SA.CUST (
        ROW_ID, CUST_ID, CUST_NM, REGISTER_DT, MOBILE, EMAIL, ADRESS, BIRTH_DT,
        CAMP_NM, CAMP_EXE_DT, CAMP_RSLT, CRET_NM, CRET_DT, CHG_NM, CHG_DT
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", cust_data)

conn.commit()

# 2️⃣ CONT 데이터 생성 및 삽입
cont_data = []
for i in range(1, 26):  # 25개 회선
    cust = random.choice(cust_data)
    cust_id = cust[1]
    cust_nm = cust[2]
    row = (
        i,  # ROW_ID
        f"SVC{i:04d}",  # SVC_CONT_ID
        cust_id,
        cust_nm,
        datetime.now(),
        f"02-1234-{1000+i}",
        f"상품{i%5}",
        random.choice(["MOBILE", "INTERNET", "TV"]),
        random.choice(["정상", "해지", "일시중지"]),
        None,
        None,
        None,
        "admin",
        datetime.now(),
        None,
        None
    )
    cont_data.append(row)

cursor.executemany(""" 
    INSERT INTO SA.CONT (
        ROW_ID, SVC_CONT_ID, CUST_ID, CUST_NM, REGISTER_DT, SVC_NO_ID,
        BPROD_NM, LOB, CONT_STTUS, CAMP_NM, CAMP_EXE_DT, CAMP_RSLT,
        CRET_NM, CRET_DT, CHG_NM, CHG_DT
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", cont_data)

# 커밋 및 종료
conn.commit()
cursor.close()
conn.close()

print("✅ 고객 및 회선 데이터 배치 완료 (다양한 이름 포함)")
