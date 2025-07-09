import random
from datetime import datetime, timedelta
import sys

sys.path.append("/home/site/wwwroot")
# sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from UTIL.db_connection import get_connection

# DB 연결
conn = get_connection()
cursor = conn.cursor()

# ---------------------------
# 1️⃣ 캠페인 기획: 캠페인 생성 및 대상 등록
# ---------------------------

# 캠페인 기본 정보 생성

# camp_id와 camp_nm에 분과 초 붙이기
now = datetime.now()
camp_id = f"CAMP{now.strftime('%M%S')}" 
camp_nm = f"2025 여름 프로모션 {now.strftime('%M:%S')}"
camp_cret_dt = datetime.now().date()

# 캠페인 상태: 기획
cursor.execute(""" --test2
    INSERT INTO SA.CAMP_BAS (
        CAMP_ID, CAMP_NM, CAMP_CRET_DT, CAMP_STTUS, CRET_NM, CRET_DT
    )
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    camp_id,
    camp_nm,
    camp_cret_dt,
    "기획",
    "marketer",
    datetime.now().date()
))
print(f"✅ 캠페인 {camp_id} 생성 완료")

# 캠페인 대상 고객·회선 선택
# CONT에서 (SVC_CONT_ID, CUST_ID) 쌍 조회
cursor.execute("""--test5 
                    SELECT SVC_CONT_ID, CUST_ID FROM SA.CONT""")
cont_data = cursor.fetchall()

# 5개 랜덤 샘플링 (회선 기준)
selected_conts = random.sample(cont_data, 5)

for idx, (svc_id, cust_id) in enumerate(selected_conts, start=1):
    camp_tgt_id = f"TGT{camp_id[4:]}{idx:03d}"
    cursor.execute(""" --test5 
        INSERT INTO SA.CAMP_TGT (
            CAMP_TGT_ID, CAMP_ID, CUST_ID, SVC_CONT_ID, CAMP_ST_DT, CAMP_END_DT, CAMP_RSLT, CRET_NM, CRET_DT
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        camp_tgt_id,
        camp_id,
        cust_id,
        svc_id,
        datetime.now(),
        datetime.now() + timedelta(days=7),
        None,  # 수행 결과 없음
        "admin",
        datetime.now().date()
    ))
print("✅ 캠페인 대상 등록 완료")


conn.commit()

# ---------------------------
# 2️⃣ 캠페인 수행: 상태 및 수행일자 업데이트
# ---------------------------

# 캠페인 상태 수행중으로 변경
cursor.execute(""" --test5 
    UPDATE SA.CAMP_BAS
    SET
        CAMP_STTUS = ?,
        CAMP_EXE_DT = ?,
        CHG_NM = ?,
        CHG_DT = ?
    WHERE CAMP_ID = ?
""", (
    "수행",
    datetime.now().date(),
    "admin",
    datetime.now(),
    camp_id
))

# 대상 테이블 수행일자 업데이트
cursor.execute(""" --test5 
    UPDATE SA.CAMP_TGT
    SET
        CAMP_ST_DT = ?,
        CHG_NM = ?,
        CHG_DT = ?
    WHERE CAMP_ID = ?
""", (
    datetime.now(),
    "admin",
    datetime.now(),
    camp_id
))

conn.commit()
print("✅ 캠페인 수행 상태로 업데이트 완료")

# ---------------------------
# 3️⃣ 캠페인 결과: 결과 업데이트
# ---------------------------

possible_results = ["성공", "실패"]

# 캠페인 상태 완료로 변경 ()
cursor.execute(""" --test5 
    UPDATE SA.CAMP_BAS
    SET
        CAMP_STTUS = ?,
        CHG_NM = ?,
        CHG_DT = ?
    WHERE CAMP_ID = ?
""", (
    "완료",
    "admin",
    datetime.now(),
    camp_id
))

# 대상 결과 업데이트
cursor.execute(""" --test5 
    UPDATE SA.CAMP_TGT
    SET
        CAMP_RSLT = ?,
        CAMP_END_DT = ?,
        CHG_NM = ?,
        CHG_DT = ?
    WHERE CAMP_ID = ?
""", (
    random.choice(possible_results),
    datetime.now(),
    "admin",
    datetime.now(),
    camp_id
))

conn.commit()
print("✅ 캠페인 결과 업데이트 완료")

cursor.close()
conn.close()
print("🎉 캠페인 배치 수행 완료")