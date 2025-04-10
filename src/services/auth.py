import random
from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import InvalidVerificationCodeError, UserNotFoundError
from src.models import PhoneVerification, User
from src.repositories.user import UserRepository


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        secret_key: str,
        algorithm: str,
        token_expire_days: int,
    ) -> None:
        self.user_repo = UserRepository(session)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_days = token_expire_days

    async def send_verification_code(self, phone_number: str) -> None:
        # В реальном приложении здесь будет интеграция с сервисом отправки SMS
        code = "".join([str(random.randint(0, 9)) for _ in range(4)])
        verification = PhoneVerification(
            phone_number=phone_number,
            code=code,
            expires_at=datetime.now() + timedelta(minutes=5),
        )
        await self.user_repo.create_verification(verification)
        print(f"Verification code for {phone_number}: {code}")  # Для тестирования

    async def verify_code(self, phone_number: str, code: str) -> str:
        verification = await self.user_repo.get_verification(phone_number)
        if not verification or verification.code != code:
            raise InvalidVerificationCodeError()

        user = await self.user_repo.get_by_phone(phone_number)
        if not user:
            # Если пользователя нет, создаем его
            user = User(
                phone_number=phone_number,
                is_phone_verified=True,
                # пока работаем только с Москвой
                city="moscow",
                preferences=[],  # Пустой список интересов
            )
            user = await self.user_repo.create(user)

        await self.user_repo.delete_verification(verification)
        return self.create_access_token({"sub": str(user.id)})

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=self.token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                raise UserNotFoundError()
        except JWTError:
            raise UserNotFoundError()

        user = await self.user_repo.get_by_id(UUID(user_id))
        if user is None:
            raise UserNotFoundError()

        return user
