from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:todos@127.0.0.1:3306/todos"

engine = create_engine(DATABASE_URL, echo=True) # 쿼리시에 디버깅을 위한 로그를 남기기 위해 echo 옵션 true
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# fastapi의 세션 관리
def get_db():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()