ALTER TABLE SA.CONT DROP CONSTRAINT FK_CONT_CUST;
-- ALTER TABLE SA.CUST DROP CONSTRAINT FK_CAMP_TGT_CUST;
-- ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CONT;
-- ALTER TABLE SA.CAMP_TGT DROP CONSTRAINT FK_CAMP_TGT_CAMP;

DROP TABLE IF EXISTS SA.CUST;
--CUST 테이블 생성
CREATE TABLE SA.CUST (
    ROW_ID INT IDENTITY(1,1) PRIMARY KEY,                        -- 행 ID
    CUST_ID VARCHAR(10) UNIQUE NOT NULL,                  -- 고객 ID
    CUST_NM VARCHAR(10) NOT NULL,                  -- 고객명
    REGISTER_DT DATETIME2 NOT NULL,                 -- 가입일자
    MOBILE VARCHAR(20),                            -- 핸드폰번호
    EMAIL VARCHAR(100),                            -- 이메일
    ADRESS VARCHAR(255),                           -- 주소
    BIRTH_DT DATE,                                 -- 생년월일
    CAMP_NM VARCHAR(100),                          -- 캠페인명
    CAMP_EXE_DT DATETIME2,                         -- 캠페인 수행일
    CAMP_RSLT VARCHAR(10),                         -- 캠페인 결과
    CRET_NM VARCHAR(20),                           -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),   -- 생성일시
    CHG_NM VARCHAR(20),                            -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME()     -- 변경일시
);


DROP TABLE IF EXISTS SA.CONT;
--CONT 테이블 생성
CREATE TABLE SA.CONT (
    ROW_ID INT IDENTITY(1,1) PRIMARY KEY,                           -- 행 ID
    SVC_CONT_ID VARCHAR(12) UNIQUE NOT NULL,                 -- 회선 ID
    CUST_ID VARCHAR(10) NOT NULL,                      -- 고객 ID
    CUST_NM VARCHAR(10) NOT NULL,                      -- 고객명
    REGISTER_DT DATETIME2 NOT NULL,                     -- 가입일자
    SVC_NO_ID VARCHAR(20),                             -- 서비스 번호
    BPROD_NM VARCHAR(100),                             -- 가입상품명
    LOB VARCHAR(10),                                   -- 가입 그룹
    CONT_STTUS VARCHAR(10),                            -- 회선 상태
    CAMP_NM VARCHAR(100),                              -- 캠페인명
    CAMP_EXE_DT DATETIME2,                             -- 캠페인 수행일
    CAMP_RSLT VARCHAR(10),                             -- 캠페인 결과
    CRET_NM VARCHAR(20),                               -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),       -- 생성일시
    CHG_NM VARCHAR(20),                                -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME(),         -- 변경일시
    CONSTRAINT FK_CONT_CUST FOREIGN KEY (CUST_ID) REFERENCES SA.CUST(CUST_ID)
);

DROP TABLE IF EXISTS SA.CAMP_BAS;
CREATE TABLE SA.CAMP_BAS (
    ROW_ID INT IDENTITY(1,1) PRIMARY KEY,                              -- 행 ID 
    CAMP_ID VARCHAR(10) UNIQUE NOT NULL,                        -- 캠페인 ID
    CAMP_NM VARCHAR(100) NOT NULL,                       -- 캠페인명
    CAMP_CRET_DT DATE NOT NULL,                          -- 캠페인 생성일
    CAMP_EXE_DT DATE,                                    -- 캠페인 수행일
    CAMP_STTUS VARCHAR(50),                               -- 캠페인 상태
    CRET_NM VARCHAR(20),                                 -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),         -- 생성일시
    CHG_NM VARCHAR(20),                                  -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME()          -- 변경일시
);

DROP TABLE IF EXISTS SA.CAMP_TGT;
CREATE TABLE SA.CAMP_TGT (
    ROW_ID INT IDENTITY(1,1) PRIMARY KEY,               -- 행 ID (AUTO_INCREMENT)
    CAMP_TGT_ID VARCHAR(50) NOT NULL,                   -- 캠페인대상 ID
    CAMP_ID VARCHAR(10) NOT NULL,                       -- 캠페인 ID
    CUST_ID VARCHAR(10) NOT NULL,                       -- 고객 ID
    SVC_CONT_ID VARCHAR(12),                                -- 회선 ID
    CAMP_ST_DT DATETIME2 NOT NULL,                      -- 수행시작일시
    CAMP_END_DT DATETIME2 NOT NULL,                     -- 수행종료일시
    CAMP_RSLT VARCHAR(10),                              -- 캠페인결과
    CRET_NM VARCHAR(20),                                -- 생성자
    CRET_DT DATETIME2 DEFAULT SYSUTCDATETIME(),         -- 생성일시
    CHG_NM VARCHAR(20),                                  -- 변경자
    CHG_DT DATETIME2 DEFAULT SYSUTCDATETIME(),          -- 변경일시
    CONSTRAINT FK_CAMP_TGT_CUST FOREIGN KEY (CUST_ID) REFERENCES SA.CUST(CUST_ID),
    CONSTRAINT FK_CAMP_TGT_CONT FOREIGN KEY (SVC_CONT_ID) REFERENCES SA.CONT(SVC_CONT_ID),
    CONSTRAINT FK_CAMP_TGT_CAMP FOREIGN KEY (CAMP_ID) REFERENCES SA.CAMP_BAS(CAMP_ID)
);


-- SELECT 
--     fk.name AS ForeignKeyName,
--     tp.name AS ParentTable
-- FROM 
--     sys.foreign_keys fk
--     INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id;
