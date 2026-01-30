import pytest

from src.repositories.user import UserRepository


@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_by_phone_not_found(self, session, phone_number):
        repo = UserRepository(session)
        result = await repo.get_by_phone(phone_number)
        assert result is None

    async def test_get_by_phone_found(self, session, user, phone_number):
        session.add(user)
        await session.commit()

        repo = UserRepository(session)
        result = await repo.get_by_phone(phone_number)
        assert result is not None
        assert result.id == user.id
        assert result.phone_number == phone_number

    async def test_get_by_id_not_found(self, session, user_id):
        repo = UserRepository(session)
        result = await repo.get_by_id(user_id)
        assert result is None

    async def test_get_by_id_found(self, session, user, user_id):
        session.add(user)
        await session.commit()

        repo = UserRepository(session)
        result = await repo.get_by_id(user_id)
        assert result is not None
        assert result.id == user_id

    async def test_create(self, session, user):
        repo = UserRepository(session)
        result = await repo.create(user)
        assert result.id == user.id
        assert result.phone_number == user.phone_number

    async def test_update(self, session, user):
        session.add(user)
        await session.commit()

        user.full_name = "Updated Name"
        repo = UserRepository(session)
        result = await repo.update(user)
        assert result.full_name == "Updated Name"

    async def test_get_verifications_empty(self, session, phone_number):
        repo = UserRepository(session)
        result = await repo.get_verifications(phone_number)
        assert result == []

    async def test_get_verifications_active_only(
        self, session, phone_verification, expired_phone_verification, phone_number
    ):
        session.add(phone_verification)
        session.add(expired_phone_verification)
        await session.commit()

        repo = UserRepository(session)
        result = await repo.get_verifications(phone_number)
        assert len(result) == 1
        assert result[0].code == phone_verification.code

    async def test_create_verification(self, session, phone_verification):
        repo = UserRepository(session)
        result = await repo.create_verification(phone_verification)
        assert result.id == phone_verification.id
        assert result.code == phone_verification.code

    async def test_delete_verification(self, session, phone_verification):
        session.add(phone_verification)
        await session.commit()

        repo = UserRepository(session)
        await repo.delete_verification(phone_verification)

        result = await repo.get_verifications(phone_verification.phone_number)
        assert len(result) == 0
