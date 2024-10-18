from fastapi import APIRouter, Depends
from src.database.repository import UserRepository
from src.schema.request import SignUpRequest
from src.service.user import UserService
from src.schema.response import UserSchema
from src.database.orm import User

router = APIRouter(prefix="/users")

@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
        request: SignUpRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends()
):
    # 1. request body(username, password)
    # 2. password -> hashing -> hased_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
    )
    # 3. User(username, hashed_password)
    user: User = User.create(
        username=request.username,
        hashed_password=hashed_password
    )
    # 4. user -> db save
    user: User = user_repo.save_user(user=user)
    # 5. return user(id, username)
    return UserSchema.from_orm(user)