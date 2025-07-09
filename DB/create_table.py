import sqlite3

def create_table_own1():
    # 인메모리 DB 연결 OWN1.db
    conn = sqlite3.connect('OWN1.db')
    c = conn.cursor()

    # 테이블 생성
    c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
    c.execute('INSERT INTO users (name) VALUES (?)', ('홍길동',))
    c.execute('INSERT INTO users (name) VALUES (?)', ('김철수',))
    conn.commit()

    # 데이터 조회
    c.execute('SELECT * FROM users')
    rows = c.fetchall()

def create_table_own2():
    # 인메모리 DB 연결 OWN2.db
    conn = sqlite3.connect('OWN2.db')
    c = conn.cursor()

    # 테이블 생성
    c.execute("""CREATE TABLE CUST(
                    ROW_ID INTEGER PRIMARY KEY,   -- 행 ID
                    CUST_ID VARCHAR(10) NOT NULL,                -- 고객 ID
                    CUST_NM VARCHAR(10) NOT NULL,                -- 고객명
                    REGISTER_DT TIMESTAMP NOT NULL,              -- 가입일자
                    MOBILE VARCHAR(20),                          -- 핸드폰번호
                    EMAIL VARCHAR(100),                          -- 이메일
                    ADRESS VARCHAR(255),                         -- 주소
                    BIRTH_DT DATE,                          -- 생년월일
                    CAMP_NM VARCHAR(100),                        -- 캠페인명
                    CAMP_EXE_DT TIMESTAMP,                       -- 캠페인 수행일
                    CAMP_RSLT VARCHAR(10),                       -- 캠페인 결과
                    CRET_NM VARCHAR(20),                         -- 생성자
                    CRET_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
                    CHG_NM VARCHAR(20),                          -- 변경자
                    CHG_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 변경일시
                    )""")
    
    c.execute("""CREATE TABLE CONT(
                    ROW_ID INT PRIMARY KEY,       -- 행 ID
                    SVC_CONT_ID VARCHAR(12) NOT NULL,            -- 회선 ID
                    CUST_ID VARCHAR(10) NOT NULL,                -- 고객 ID
                    CUST_NM VARCHAR(10) NOT NULL,                -- 고객명
                    REGISTER_DT TIMESTAMPNOT NULL,               -- 가입일자
                    SVC_NO_ID VARCHAR(20),                       -- 서비스 번호
                    BPROD_NM VARCHAR(100),                       -- 가입상품명
                    LOB VARCHAR(10),                             -- 가입 그룹
                    CONT_STTUS VARCHAR(10),                      -- 회선 상태
                    CAMP_NM VARCHAR(100),                       -- 캠페인명
                    CAMP_EXE_DT TIMESTAMP,                       -- 캠페인 수행일
                    CAMP_RSLT VARCHAR(10),                       -- 캠페인 결과
                    CRET_NM VARCHAR(20),                         -- 생성자
                    CRET_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
                    CHG_NM VARCHAR(20),                          -- 변경자
                    CHG_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 변경일시
                )""")
    
    c.execute("""CREATE TABLE CAMP_BAS(
                    ROW_ID INT PRIMARY KEY,                     -- 행 ID 
                    CAMP_ID VARCHAR(10) NOT NULL,               -- 캠페인 ID
                    CAMP_NM VARCHAR(100) NOT NULL,              -- 캠페인명
                    CAMP_CRET_DT DATE NOT NULL,                 -- 캠페인 생성일
                    CAMP_EXE_DT DATE ,                          -- 캠페인 수행일
                    CAMP_RSLT VARCHAR(50),                      -- 캠페인 상태
                    CRET_NM VARCHAR(20),                         -- 생성자
                    CRET_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
                    CHG_NM VARCHAR(20),                          -- 변경자
                    CHG_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 변경일시
                    FOREIGN KEY (CAMP_ID) REFERENCES CAMP_TGT(CAMP_ID)
                )""")
    
    c.execute("""CREATE TABLE CAMP_TGT(
                    ROW_ID INT PRIMARY KEY AUTO_INCREMENT,       -- 행 ID
                    CAMP_TGT_ID VARCHAR(50) NOT NULL,            -- 캠페인대상 ID
                    CAMP_ID VARCHAR(50) NOT NULL,                -- 캠페인 ID
                    CUST_ID VARCHAR(50) NOT NULL,                -- 고객 ID
                    CONT_ID VARCHAR(50) ,                        -- 회선 ID
                    CAMP_ST_DT TIMESTAMP NOT NULL,               -- 수행시작일시
                    CAMP_END_DT TIMESTAMP NOT NULL,              -- 수행종료일시
                    CAMP_RSLT VARCHAR(10),                       -- 캠페인결과
                    CRET_NM VARCHAR(20),                         -- 생성자
                    CRET_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
                    CHG_NM VARCHAR(20),                          -- 변경자
                    CHG_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 변경일시
                    FOREIGN KEY (CUST_ID) REFERENCES CUST(CUST_ID),
                    FOREIGN KEY (CONT_ID) REFERENCES CONT(CONT_ID)
                )""")

    conn.commit()

    # 데이터 조회
    # c.execute('SELECT * FROM users')
    rows = c.fetchall()

def insert_dummy_cust():
    # 인메모리 DB 연결 OWN2.db
    conn = sqlite3.connect('OWN2.db')
    c = conn.cursor()

    # ...existing code...

    # CUST 테이블 더미 데이터 10개 입력 (이름 마스킹 적용)
    cust_dummy = [
        ('CUST001', '홍길동', '2023-01-01 10:00:00', '010-1111-1111', 'hong1@email.com', '서울시 강남구', '1990-01-01', '봄이벤트', '2023-03-01 09:00:00', '성공', '관리자', '관리자'),
        ('CUST002', '김철수', '2023-01-02 11:00:00', '010-2222-2222', 'kim2@email.com', '서울시 서초구', '1985-02-02', '여름이벤트', '2023-06-01 09:00:00', '실패', '관리자', '관리자'),
        ('CUST003', '이영희', '2023-01-03 12:00:00', '010-3333-3333', 'lee3@email.com', '서울시 송파구', '1992-03-03', '가을이벤트', '2023-09-01 09:00:00', '성공', '관리자', '관리자'),
        ('CUST004', '박민수', '2023-01-04 13:00:00', '010-4444-4444', 'park4@email.com', '서울시 노원구', '1988-04-04', '겨울이벤트', '2023-12-01 09:00:00', '성공', '관리자', '관리자'),
        ('CUST005', '최지우', '2023-01-05 14:00:00', '010-5555-5555', 'choi5@email.com', '서울시 마포구', '1995-05-05', '봄이벤트', '2023-03-01 09:00:00', '실패', '관리자', '관리자'),
        ('CUST006', '정해인', '2023-01-06 15:00:00', '010-6666-6666', 'jung6@email.com', '서울시 용산구', '1991-06-06', '여름이벤트', '2023-06-01 09:00:00', '성공', '관리자', '관리자'),
        ('CUST007', '한지민', '2023-01-07 16:00:00', '010-7777-7777', 'han7@email.com', '서울시 은평구', '1987-07-07', '가을이벤트', '2023-09-01 09:00:00', '실패', '관리자', '관리자'),
        ('CUST008', '오세훈', '2023-01-08 17:00:00', '010-8888-8888', 'oh8@email.com', '서울시 강동구', '1993-08-08', '겨울이벤트', '2023-12-01 09:00:00', '성공', '관리자', '관리자'),
        ('CUST009', '서지수', '2023-01-09 18:00:00', '010-9999-9999', 'seo9@email.com', '서울시 동작구', '1996-09-09', '봄이벤트', '2023-03-01 09:00:00', '성공', '관리자', '관리자'),
        ('CUST010', '문채원', '2023-01-10 19:00:00', '010-1010-1010', 'moon10@email.com', '서울시 종로구', '1989-10-10', '여름이벤트', '2023-06-01 09:00:00', '실패', '관리자', '관리자')
    ]
    c.executemany("""
        INSERT INTO CUST (
            CUST_ID, CUST_NM, REGISTER_DT, MOBILE, EMAIL, ADRESS, BIRTH_DT,
            CAMP_NM, CAMP_EXE_DT, CAMP_RSLT, CRET_NM, CHG_NM
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, cust_dummy)

    conn.commit()


def insert_dummy_cont():
    # 인메모리 DB 연결 OWN2.db
    conn = sqlite3.connect('OWN2.db')
    c = conn.cursor()

    # ...existing code...

    # CUST 테이블 더미 데이터 10개 입력 (이름 마스킹 적용)
    dummy = [
        ('SVC00000001', 'CUST001', '홍길동', '2023-01-01 10:00:00','010-1111-1111', 'LTE 베이직', '모바일', '활성','봄이벤트', '2023-03-01 09:00:00', '성공','관리자', '2023-01-01 10:00:00', '관리자', '2023-03-01 09:00:00'),
        ('SVC00000002', 'CUST002', '김철수', '2023-01-02 11:00:00','010-2222-2222', '5G 프리미엄', '모바일', '해지','여름이벤트', '2023-06-01 09:00:00', '실패','관리자', '2023-01-02 11:00:00', '관리자', '2023-06-01 09:00:00'),
        ('SVC00000003', 'CUST003', '이영희', '2023-01-03 12:00:00','010-3333-3333', '인터넷 결합', '모바일', '활성','가을이벤트', '2023-09-01 09:00:00', '성공','관리자', '2023-01-03 12:00:00', '관리자', '2023-09-01 09:00:00'),
        ('SVC00000004', 'CUST004', '박민수', '2023-01-04 13:00:00','010-4444-4444', 'IPTV 베이직', '모바일', '활성','겨울이벤트', '2023-12-01 09:00:00', '성공','관리자', '2023-01-04 13:00:00', '관리자', '2023-12-01 09:00:00'),
        ('SVC00000005', 'CUST005', '최지우', '2023-01-05 14:00:00','010-5555-5555', '5G 라이트', '모바일', '일시정지','봄이벤트', '2023-03-01 09:00:00', '실패','관리자', '2023-01-05 14:00:00', '관리자', '2023-03-01 09:00:00'),
        ('SVC00000006', 'CUST006', '정해인', '2023-01-06 15:00:00','010-6666-6666', '인터넷 단독', '모바일', '활성','여름이벤트', '2023-06-01 09:00:00', '성공','관리자', '2023-01-06 15:00:00', '관리자', '2023-06-01 09:00:00'),
        ('SVC00000007', 'CUST007', '한지민', '2023-01-07 16:00:00','010-7777-7777', 'IPTV 프리미엄', '모바일', '해지','가을이벤트', '2023-09-01 09:00:00', '실패','관리자', '2023-01-07 16:00:00', '관리자', '2023-09-01 09:00:00'),
        ('SVC00000008', 'CUST008', '오세훈', '2023-01-08 17:00:00','010-8888-8888', 'LTE 요금제', '모바일', '활성','겨울이벤트', '2023-12-01 09:00:00', '성공','관리자', '2023-01-08 17:00:00', '관리자', '2023-12-01 09:00:00'),
        ('SVC00000009', 'CUST009', '서지수', '2023-01-09 18:00:00','010-9999-9999', '5G 라이트', '모바일', '일시정지','봄이벤트', '2023-03-01 09:00:00', '성공','관리자', '2023-01-09 18:00:00', '관리자', '2023-03-01 09:00:00'),
        ('SVC00000010', 'CUST010', '문채원', '2023-01-10 19:00:00','010-1010-1010', '인터넷 결합', '모바일', '해지','여름이벤트', '2023-06-01 09:00:00', '실패','관리자', '2023-01-10 19:00:00', '관리자', '2023-06-01 09:00:00')
    ]



    c.executemany("""
        INSERT INTO CONT (
            SVC_CONT_ID, CUST_ID, CUST_NM, REGISTER_DT,
            SVC_NO_ID, BPROD_NM, LOB, CONT_STTUS, 
            CAMP_NM, CAMP_EXE_DT, CAMP_RSLT,
            CRET_NM, CRET_DT, CHG_NM, CHG_DT
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, dummy)

    conn.commit()







#create_table_own1()
# create_table_own2()
# insert_dummy_cust()
# insert_dummy_cont()



def FK_ADD():
    # 인메모리 DB 연결 OWN2.db
    conn = sqlite3.connect('OWN2.db')
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS CAMP_BAS")
    
    c.execute("""CREATE TABLE CAMP_BAS(
                    ROW_ID INT PRIMARY KEY,                     -- 행 ID 
                    CAMP_ID VARCHAR(10) NOT NULL,               -- 캠페인 ID
                    CAMP_NM VARCHAR(100) NOT NULL,              -- 캠페인명
                    CAMP_CRET_DT DATE NOT NULL,                 -- 캠페인 생성일
                    CAMP_EXE_DT DATE ,                          -- 캠페인 수행일
                    CAMP_RSLT VARCHAR(50),                      -- 캠페인 상태
                    CRET_NM VARCHAR(20),                         -- 생성자
                    CRET_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 생성일시
                    CHG_NM VARCHAR(20),                          -- 변경자
                    CHG_DT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- 변경일시
                    FOREIGN KEY (CAMP_ID) REFERENCES CAMP_TGT(CAMP_ID)
                )""")

    conn.commit()

FK_ADD()