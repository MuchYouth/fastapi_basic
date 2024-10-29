from src.database.repository import UserRepository
from src.service.user import UserService
from src.database.orm import User
def test_user_sign_up(client, mocker):
    # 비밀번호 해싱하는 함수 모킹
    hash_password = mocker.patch.object(
        UserService,
        "hash_password",
        return_value="hashed"
    )
    # 유저의 create 함수 모킹
    # 아직 아이디는 비어있다.
    user_create = mocker.patch.object(
        User,
        "create",
        return_value=User(id=None, username="test", password="hashed")
    )
    # UserRepository 의 save_user 모킹
    # 정수아이디가 할당된 채로 반환되어야한다.
    mocker.patch.object(
        UserRepository,
        "save_user",
        return_value=User(id=1, username="test", password="hashed")
    )
    body = {
        "username": "test",
        "password": "plain"
    }
    # 원래는 해싱하는 과정도 테스트에 포함해야하지만, 여기서는 해싱함수가 정상적으로 작동한다는 가정하에 진행
    response = client.post("/users/sign-up", json=body)
    # assert_called_once_with에서 with가 붙으면 호출여부와 반환 값까지 검증 가능
    hash_password.assert_called_once_with(
        plain_password="plain"
    )
    user_create.assert_called_once_with(
        username="test", hashed_password="hashed"
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "test"}

