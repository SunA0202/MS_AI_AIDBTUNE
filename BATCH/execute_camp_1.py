import random
from datetime import datetime
import sys

sys.path.append("/home/site/wwwroot")
# sys.path.append("D:\\MS AI 개발역량 향상과정_박선아\\MVP\\UTIL")
from UTIL.db_connection import get_connection

# 캠페인 이름 리스트
campaign_list = [
    "CAMP2024_여름",
    "CAMP2024_가을",
    "CAMP2024_겨울",
    "CAMP2025_봄",
    "CAMP2025_여름"
]

# 랜덤 결과
possible_results = ["성공", "실패"]

# DB 연결
conn = get_connection()
cursor = conn.cursor()

for campaign_name in campaign_list:
    campaign_date = datetime.now()

    # 1️⃣ CUST 대상자 랜덤 선택
    cursor.execute(""" --test5 
                   SELECT CUST_ID FROM SA.CUST""")
    all_cust_ids = [row[0] for row in cursor.fetchall()]
    selected_cust_ids = random.sample(all_cust_ids, random.randint(3, 4))

    # 2️⃣ CONT 대상자 랜덤 선택
    cursor.execute(""" --test5 
                   SELECT SVC_CONT_ID FROM SA.CONT""")
    all_cont_ids = [row[0] for row in cursor.fetchall()]
    selected_cont_ids = random.sample(all_cont_ids, random.randint(3, 4))

    print(f"\n🌟 캠페인 '{campaign_name}' 대상 고객 {selected_cust_ids}")
    print(f"🌟 캠페인 '{campaign_name}' 대상 회선 {selected_cont_ids}")

    # 3️⃣ CUST 캠페인 시작
    for cust_id in selected_cust_ids:
        cursor.execute(
            """ --test5 
            UPDATE SA.CUST
            SET
                CAMP_NM = ?,
                CAMP_EXE_DT = ?,
                CAMP_RSLT = ?,
                CHG_NM = ?,
                CHG_DT = ?
            WHERE
                CUST_ID = ?
            """,
            (
                campaign_name,
                campaign_date,
                "진행중",
                "system_batch",
                datetime.now(),
                cust_id
            )
        )

    # 4️⃣ CONT 캠페인 시작
    for cont_id in selected_cont_ids:
        cursor.execute(
            """ --test5 
            UPDATE SA.CONT
            SET
                CAMP_NM = ?,
                CAMP_EXE_DT = ?,
                CAMP_RSLT = ?,
                CHG_NM = ?,
                CHG_DT = ?
            WHERE
                SVC_CONT_ID = ?
            """,
            (
                campaign_name,
                campaign_date,
                "진행중",
                "system_batch",
                datetime.now(),
                cont_id
            )
        )

    conn.commit()
    print(f"✅ '{campaign_name}' 캠페인 시작 상태로 업데이트 완료")

    # 5️⃣ 캠페인 수행 결과 랜덤 업데이트
    cust_result = random.choice(possible_results)
    cont_result = random.choice(possible_results)

    for cust_id in selected_cust_ids:
        cursor.execute(
            """ --test5 
            UPDATE SA.CUST
            SET
                CAMP_RSLT = ?,
                CHG_NM = ?,
                CHG_DT = ?
            WHERE
                CUST_ID = ?
            """,
            (
                cust_result,
                "system_batch",
                datetime.now(),
                cust_id
            )
        )

    for cont_id in selected_cont_ids:
        cursor.execute(
            """ --test5 
            UPDATE SA.CONT
            SET
                CAMP_RSLT = ?,
                CHG_NM = ?,
                CHG_DT = ?
            WHERE
                SVC_CONT_ID = ?
            """,
            (
                cont_result,
                "system_batch",
                datetime.now(),
                cont_id
            )
        )

    conn.commit()
    print(f"🎯 '{campaign_name}' 결과 업데이트 완료 (CUST: {cust_result}, CONT: {cont_result})")

cursor.close()
conn.close()
print("\n🎉 모든 캠페인 배치 수행 완료")