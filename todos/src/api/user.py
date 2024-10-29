from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from src.cache import redis_client
from src.database.repository import UserRepository
from src.schema.request import SignUpRequest, LogInRequest, CreateOTPRequest, VerifyOTPRequest
from src.service.user import UserService
from src.schema.response import UserSchema, JWTResponse
from src.database.orm import User
from src.security import get_access_token
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

@router.post("/log-in")
def user_log_in_handler(
        request: LogInRequest,
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
):
    # 1. request body(username, password)
    # 2. db read user
    user: User | None = user_repo.get_user_by_username(
        username=request.username
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 3. user.password, request.password -> bcrypt.checkpw
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password,
    )
    if not verified:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # 4. create jwt
    access_token: str = user_service.create_jwt(username=user.username)
    # 5. return jwt
    return JWTResponse(access_token=access_token)

# 회원가입 이후 이메일 인증(otp활용)
# POST /users/email/otp -> (key:email, value:1234, exp:3min)
@ router.post("/email/otp")
def create_otp_handler(
    request: CreateOTPRequest,
    _: str = Depends(get_access_token),
    user_service: UserService = Depends(),
):
    # 1. access_token 을 활용해서 회원가입을 통해 인증된 유저만 사용할 수 있도록 한다.
    # 2. request_body (email) => request modeling
    # 3. otp create (random 4 digit)
    otp: int = user_service.create_otp()
    # 4. redis otp(email, 1234, exp=3min)
    redis_client.set(request.email, otp)
    redis_client.expire(request.email, 3 * 60) # 3min
    # 5. send otp to email
    return {"otp": otp}

# POST /users/email/otp/verify -> request(email.otp) -> user(email)
@ router.post("/email/otp/verify")
def verify_otp_handler(
        request: VerifyOTPRequest,
        background_tasks: BackgroundTasks,
        access_token: str = Depends(get_access_token),
        user_service: UserService = Depends(),
        user_repo: UserRepository = Depends(),
):
    # 1. access_token
    # 2. request body(email, otp)
    otp: str | None = redis_client.get(request.email)
    if not otp:
        raise HTTPException(status_code=400, detail="Bad Request")

    if request.otp != int(otp):
        raise HTTPException(status_code=400, detail="Bad Request")
    # 3. request.otp == redis.get(email)
    username: str = user_service.decode_jwt(access_token=access_token)
    user: User | None = user_repo.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # 4. user(email)
    # 따로 이메일을 저장하고 싶다면 이메일 관련 데이터 테이블 열을 만들어야 한다.
    # 여기서는 로직을 만들지 않고 주석으로만 해두고 넘어감
    # save email to user
    # send email to user
    background_tasks.add_task(
        user_service.send_email_to_user,
        email="admin@fastapi.com"
    )
    return UserSchema.from_orm(user)