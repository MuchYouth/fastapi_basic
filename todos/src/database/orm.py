from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base
from src.schema.request import CreateToDoRequest

Base = declarative_base()

class ToDo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, default=False)

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