from typing import List
from sqlalchemy import select, delete
from fastapi import Depends
from database.connection import get_db
from sqlalchemy.orm import Session
from database.orm import ToDo

class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    # 단일 todo 가져오기
    def get_todo_by_todo_id(self, todo_id:int) -> ToDo | None:
        return self.session.scalar(select(ToDo).where(ToDo.id == todo_id))

    # 세션 연결후 todo라는  orm 객체로 받아온다.
    def create_todo(self, todo:ToDo) -> ToDo:
        # sqlalchemy에서 데이터를 추가하는 방법
        self.session.add(instance=todo) # 인스턴스가 세션에 쌓인다.
        self.session.commit() # 실제로 데이터베이스에 저장되는 시기 => 이때 아이디 값이 할당된다.
        self.session.refresh(instance=todo) # 하지만 아직 서버는 아이디값이 몇번이 지정되었는지 모르기때문에 refresh로 다시 가져온다.
        return todo

    def update_todo(self, todo:ToDo) -> ToDo:
        # create와 로직은 동일
        self.session.add(instance=todo)
        self.session.commit()
        self.session.refresh(instance=todo) # 굳이 안해도 된다. 벗, 최신 데이터 확인을 위해 작성
        return todo

    def delete_todo(self, todo_id:int) -> None:
        self.session.execute(delete(ToDo).where(ToDo.id == todo_id)) # delete는 sqlalchemy의 내장함수
        # autocommit을 false로 지정해줬기 때문에 데이터 변경이후에는 반드시 commit 함수 수행해야한다.
        self.session.commit()