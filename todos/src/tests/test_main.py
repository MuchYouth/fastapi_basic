from database.orm import ToDo
from src.database.repository import ToDoRepository


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}

def test_get_todos(client, mocker):
    # order = asc
    mocker.patch.object(ToDoRepository,"get_todos", return_value=[
        ToDo(id=1, contents="FastAPI Section 0", is_done=True),
        ToDo(id=2, contents="FastAPI Section 1", is_done=False),
    ])
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {
        "todos":[
            {"id": 1, "contents":"FastAPI Section 0", "is_done":True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False}
        ]
    }
    # order=desc
    response = client.get("/todos?order=DESC")
    assert response.status_code == 200
    assert response.json() == {
        "todos":[
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }

def test_get_todo(client, mocker):
    # 200
    mocker.patch.object(ToDoRepository,"get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id":1, "contents":"todo", "is_done":True}
    # 404
    mocker.patch(
        "api.todo.get_todo_by_todo_id", return_value=None
    )
    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail":"ToDo Not Found"}


def test_create_todo(client,mocker):
    create_spy = mocker.spy(ToDo, "create")
    # 아래의 코드를 보면 의문이 들수 있다.
    # 요청으로 주고 있는 데이터와 응답으로 확인 하는 데이터의 값이 다르기 때문이다.
    # 이유는 테스트를 하는 과정에서 mocking 된 데이터가 전달되기 때문이다.
    # 이렇게 되면 todo: ToDo = ToDo.create(request=request) 와 같은 생성부분에 대한 검증이 미비 -> spy 기능 이용
    mocker.patch.object(ToDoRepository,"create_todo",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )
    body= {"contents":"test", "is_done":False}
    response = client.post("/todos", json=body)
    # 요청한 데이터에 대해서 생성이 잘 이루어지는지 검증
    assert create_spy.spy_return.id is not None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False
    # 응답이 잘 되는지 확인
    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}

def test_update_todo(client, mocker):
    # 여기서도 create 와 같이 검증이 잘 되지않는다.
    # 200
    mocker.patch.object(ToDoRepository,"get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )
    undone = mocker.patch.object(ToDo, "undone")
    mocker.patch(
        "api.todo.update_todo",
        return_value=ToDo(id=1, contents="todo", is_done=False),
    )
    response = client.patch("/todos/1", json={"is_done":False})
    undone.assert_called_once_with() # undone이 실행되지않으면 이 부분이 잘 되지않는다 => 에러발생
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": False}
    # 404
    mocker.patch.object(ToDoRepository,"get_todo_by_todo_id", return_value=None
    )
    response = client.patch("/todos/1", json={"is_done":True})
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}

def test_delete_todo(client, mocker):
    # 204
    mocker.patch.object(ToDoRepository,"get_todo_by_todo_id",
        return_value=ToDo(id=1, contents="todo", is_done=True),
    )
    mocker.patch("api.todo.delete_todo", return_value=None)
    response = client.delete("/todos/1")
    assert response.status_code == 204

    # 404
    mocker.patch.object(ToDoRepository,"get_todo_by_todo_id", return_value=None
    )
    response = client.delete("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail":"ToDo Not Found"}