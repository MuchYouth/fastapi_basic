# orm 데이터 구조와 같은데 굳이 응답 객체를 나눠서 만들어야하는 이유가 뭐냐
# -> 응답객체는 이후에 3개의 필드중에 한두개만 보낸다던가 하는 다양한 활용방법이 있을 수 있다.
from pydantic import BaseModel
from typing import List

# TO0
class ToDoSchema(BaseModel):
    id : int
    contents: str
    is_done: bool
    # pydantic 에서 sqlalchemy를 바로 읽어줄수있도록 하기 위해서는 따로 정의가 필요하다.
    # orm 객체를 schema로 바로 불러줄수있게하는 from_orm 함수 사용이 가능해진다.
    class Config:
        orm_mode = True

class ToDoListSchema(BaseModel):
    todos: List[ToDoSchema]

class UserSchema(BaseModel):
    id: int
    username:str

    class Config:
        orm_mode = True
