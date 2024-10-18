from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from src.schema.request import CreateToDoRequest
Base = declarative_base()

class ToDo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, default=False)
    # 유저 테이블과 투두 테이블을 조인하기 위해서 foreign key 지정 필수
    user_id = Column(Integer, ForeignKey("user.id"))

    def __repr__(self):
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done}"
    
    # requestbody로부터 전달받은 데이터를 orm 객체로 만들어주는 클래스 함수 작성
    # pydantic으로 받아온 CreateToDoRequest를 orm 객체로 만들어 주는 것
    @classmethod
    def create(cls, request: CreateToDoRequest) -> "ToDo":
        return cls(
            # id 값은 데이터 베이스에 의해 자동으로 지정되기 때문에 지정할 필요 없음
            contents=request.contents,
            is_done=request.is_done,
        )

    def done(self) -> "ToDo":
        self.is_done = True
        # send email ...
        return self

    def undone(self) -> "ToDo":
        self.is_done = False
        return self


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    # user 테이블을 가져와 사용할때 todos 속성으로 todo 테이블에도 접근 가능
    todos = relationship("ToDo", lazy="joined")

    @classmethod
    def create(cls, username:str, hashed_password:str) -> "User":
        return cls(
            username=username,
            password=hashed_password,
        )
