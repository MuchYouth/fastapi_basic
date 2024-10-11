from typing import List

from fastapi import Depends, HTTPException, Body, APIRouter
from sqlalchemy.orm import Session
from src.database.connection import get_db
from src.database.orm import ToDo
from src.database.repository import ToDoRepository
from src.schema.request import CreateToDoRequest
from src.schema.response import ToDoListSchema, ToDoSchema

# 조회를 하는 부분 : database에서 데이터 조회 -> orm 객체를 불러옴 -> orm 객체를 리턴해주는 부분에서 pydantic에 맞게 변환
# 생성을 하는 부분 : pydantic으로 들어온 데이터 -> orm으로 변환 -> database에 저장

router = APIRouter(prefix="/todos")

@router.get("", status_code=200)
# fastapi 에서 파라미터 전달 방법 (함 수
def get_todos_handler(
        order:str | None = None,
        todo_repo: ToDoRepository = Depends(),
) -> ToDoListSchema:
    # 데이터를 조회하는 부분은 따로 파일로 관리 (레포지토리 패턴)
    todos:List[ToDo] = todo_repo.get_todos()
    if order and order == "DESC":
        return ToDoListSchema(
            todos=[ToDoSchema.from_orm(todo) for todo in todos[::-1]]
        )
    # 아래와 같은 방식으로 데이터를 직접 리턴하지않고,
    # return todos
    # 데이터 reponse를 만들어서 리턴한다.
    return ToDoListSchema(
        todos=[ToDoSchema.from_orm(todo) for todo in todos]
    )


@router.get("/{todo_id}",status_code=200)
def get_todo_handler(
    todo_id: int,
    todo_repo: ToDoRepository = Depends(),
) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id = todo_id)
    if todo:
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")


@router.post("", status_code=201)
def create_todo_handler(
        request: CreateToDoRequest,
        todo_repo: ToDoRepository = Depends(),
) -> ToDoSchema:
    # orm 파일에 있는 ToDo 클래스 내부의 create 메소드에 의해 orm 객체가 넘어온다.
    todo: ToDo = ToDo.create(request=request) # id : None
    todo: ToDo = todo_repo.create_todo(todo=todo) # id값 지정된 상태
    # (데이터 베이스 사용전) todo_data[request.id] = request.dict() # dict()를 붙여주는 이유 : todo_data는 딕셔너리 자료형이고, request는 basemodel의 객체이기 때문이다.
    return ToDoSchema.from_orm(todo) # 저장된 데이터를 다시 사용자에 보여준다.


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
        todo_id: int,
        is_done: bool = Body(..., embed=True),
        todo_repo: ToDoRepository = Depends(),
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id) # 접근하려는 todo가 유효한 접근인지 확인 먼저
    if todo:
        # todo가 있다면 update (인스턴스 메소드를 이용해 구현)
        # 인스턴스 메소드를 이용해 구현하는 이유는 유지보수가 편리하기때문이다.
        # main 파일에서 is_done 값을 변경할 수도 있지만, 변경하는 코드를 orm 파일에서 메소드로 구현해두면
        # 업데이트가 이루어졌을때 이메일을 보내는 서비스를 넣으려고 한다면 관련 메소드로 이동해서 이메일 전송 로직을 추가하면 된다.
        todo.done() if is_done else todo.undone() # 삼항 연산자 사용
        # 업데이트는 되었지만 아직 데이터 베이스에 저장된 것은 아니다.
        todo:ToDo = update_todo(session=session, todo=todo)
        return ToDoSchema.from_orm(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")


@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
        todo_id: int,
        todo_repo: ToDoRepository = Depends(),
):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id = todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo Not Found")

    delete_todo(session=session, todo_id=todo_id)
# 204 상태코드의 경우 반환문을 적지않아도 문제되지 않는다.