import pytest

from src.services.user import UserService


@pytest.mark.asyncio
class TestUserService:
    async def test_update_user_email(self, session, user):
        session.add(user)
        await session.commit()

        service = UserService(session)
        updated = await service.update_user(user, email="newemail@example.com")

        assert updated.email == "newemail@example.com"
        assert updated.full_name == user.full_name

    async def test_update_user_full_name(self, session, user):
        session.add(user)
        await session.commit()

        service = UserService(session)
        updated = await service.update_user(user, full_name="New Name")

        assert updated.full_name == "New Name"
        assert updated.email == user.email

    async def test_update_user_preferences(self, session, user):
        session.add(user)
        await session.commit()

        service = UserService(session)
        new_preferences = ["museum", "park"]
        updated = await service.update_user(user, preferences=new_preferences)

        assert updated.preferences == new_preferences

    async def test_update_user_multiple_fields(self, session, user):
        session.add(user)
        await session.commit()

        service = UserService(session)
        updated = await service.update_user(
            user,
            email="newemail@example.com",
            full_name="New Name",
            preferences=["museum"],
        )

        assert updated.email == "newemail@example.com"
        assert updated.full_name == "New Name"
        assert updated.preferences == ["museum"]

    async def test_update_user_no_changes(self, session, user):
        session.add(user)
        await session.commit()

        original_email = user.email
        original_name = user.full_name

        service = UserService(session)
        updated = await service.update_user(user)

        assert updated.email == original_email
        assert updated.full_name == original_name
