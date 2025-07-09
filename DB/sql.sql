-- 캠페인 상태 완료 변경 쿼리
UPDATE SA.CAMP_BAS
SET
    CAMP_STTUS = '완료',
    CHG_NM = 'adimin',
    CHG_DT = '202507100000'
WHERE
    CAMP_ID IN (
        SELECT T1.CAMP_ID
        FROM SA.CAMP_BAS T1
        LEFT JOIN SA.CAMP_BAS T2
            ON T1.CAMP_ID = T2.CAMP_ID
        WHERE T1.CAMP_ID = 'CAMP0001'
    )

