from uuid import UUID

import pytest
from jose import jwt

from src.core.exceptions import InvalidVerificationCodeError, UserNotFoundError
from src.services.auth import AuthService


@pytest.mark.asyncio
class TestAuthService:
    async def test_send_verification_code(self, session, phone_number, settings):
        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )
        await service.send_verification_code(phone_number)

        from src.repositories.user import UserRepository

        repo = UserRepository(session)
        verifications = await repo.get_verifications(phone_number)
        assert len(verifications) == 1
        assert len(verifications[0].code) == 4

    async def test_verify_code_new_user(self, session, phone_number, phone_verification, settings):
        session.add(phone_verification)
        await session.commit()

        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )
        token = await service.verify_code(phone_number, phone_verification.code)

        assert token is not None
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert "sub" in payload

        from src.repositories.user import UserRepository

        repo = UserRepository(session)
        user = await repo.get_by_phone(phone_number)
        assert user is not None
        assert user.is_phone_verified is True

    async def test_verify_code_existing_user(self, session, user, phone_number, phone_verification, settings):
        session.add(user)
        session.add(phone_verification)
        await session.commit()

        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )
        token = await service.verify_code(phone_number, phone_verification.code)

        assert token is not None
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == str(user.id)

    async def test_verify_code_invalid(self, session, phone_number, settings):
        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )

        with pytest.raises(InvalidVerificationCodeError):
            await service.verify_code(phone_number, "9999")

    async def test_create_access_token(self, session, settings):
        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )
        data = {"sub": "test-user-id"}
        token = service.create_access_token(data)

        assert token is not None
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test-user-id"
        assert "exp" in payload

    async def test_get_current_user_success(self, session, user, user_id, settings):
        session.add(user)
        await session.commit()

        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )
        token = service.create_access_token({"sub": str(user_id)})
        result = await service.get_current_user(token)

        assert result is not None
        assert result.id == user_id

    async def test_get_current_user_invalid_token(self, session, settings):
        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )

        with pytest.raises(UserNotFoundError):
            await service.get_current_user("invalid-token")

    async def test_get_current_user_expired_token(self, session, user, user_id, settings):
        session.add(user)
        await session.commit()

        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=-1,
        )
        token = service.create_access_token({"sub": str(user_id)})

        with pytest.raises(UserNotFoundError):
            await service.get_current_user(token)

    async def test_get_current_user_not_found(self, session, settings):
        service = AuthService(
            session=session,
            secret_key=settings.secret_key,
            algorithm=settings.algorithm,
            token_expire_days=settings.access_token_expire_days,
        )
        token = service.create_access_token({"sub": str(UUID("00000000-0000-0000-0000-000000000000"))})

        with pytest.raises(UserNotFoundError):
            await service.get_current_user(token)
