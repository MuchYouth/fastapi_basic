import random
import time
import bcrypt
from datetime import datetime, timedelta
from jose import jwt

class UserService:
    encoding: str = "UTF-8"
    # jwt에 사용할 시크릿 키
    secret_key: str = "123456789de21s2e5f2se"
    # 암호화 알고리즘
    jwt_algorithm: str = "HS256"
    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding),
            salt=bcrypt.gensalt())
        return hashed_password.decode(self.encoding)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding)
        )

# sub 라는 키로 사용자 이름을 전달하고, exp라는 키로 시간을 전달하였다. (토큰의 만료시간 하루로 설정)
    def create_jwt(self, username:dict) -> str:
        return jwt.encode(
        {
                    "sub":username, # unique id
                    "exp":datetime.now() + timedelta(days=1)
                },
                self.secret_key,
                algorithm=self.jwt_algorithm,
        )
# 액세스 토큰을 통해 사용자를 알아내고, 해당 사용자을 출력해보자
    def decode_jwt(self, access_token: str):
        payload: dict = jwt.decode(
            access_token, self.secret_key, algorithms=[self.jwt_algorithm]
        )
        # expire (만료 확인코드 필요)
        return payload["sub"] # username

    @staticmethod
    # 이 애너테이션을 사용하면 self 키워드 삭제 가능
    def create_otp() -> int:
        return random.randint(1000, 9999) # 네자리 정수 랜덤 생성

    @staticmethod
    def send_email_to_user(email:str) -> None:
        time.sleep(10)
        print(f"Sending email to {email}!")