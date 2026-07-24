import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import select


pytestmark = pytest.mark.integration


class TestAuthFlow:
    async def test_register_user(self, async_client, override_get_db, mock_db_session, patch_jwt):
        import uuid
        from datetime import datetime, timezone

        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        async def _refresh(user):
            user.id = uuid.uuid4()
            user.is_verified = False
            user.preferences = {}
            user.created_at = datetime.now(timezone.utc)
            user.updated_at = datetime.now(timezone.utc)
        mock_db_session.refresh = AsyncMock(side_effect=_refresh)

        payload = {
            "full_name": "Nouvel Utilisateur",
            "email": "nouveau@example.com",
            "password": "Password123",
            "phone": "+212612345678",
            "role": "buyer",
        }
        response = await async_client.post("/api/auth/register", json=payload)
        assert response.status_code == 201

    async def test_register_duplicate_email(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = {"id": "existing"}

        payload = {
            "full_name": "Test",
            "email": "existant@example.com",
            "password": "Password123",
            "phone": "+212612345678",
            "role": "buyer",
        }
        response = await async_client.post("/api/auth/register", json=payload)
        assert response.status_code == 409

    async def test_login_success(self, async_client, override_get_db, mock_db_session):
        import uuid
        from datetime import datetime, timezone
        import bcrypt
        from app.models.user import User

        hashed = bcrypt.hashpw(b"Password123", bcrypt.gensalt()).decode()

        fake_user = User(
            id=uuid.uuid4(),
            full_name="Test",
            email="test@example.com",
            hashed_password=hashed,
            role="buyer",
            is_verified=True,
            preferences={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_db_session.execute.return_value.scalar_one_or_none.return_value = fake_user

        payload = {"email": "test@example.com", "password": "Password123"}
        response = await async_client.post("/api/auth/login", json=payload)
        assert response.status_code == 200

    async def test_login_wrong_password(self, async_client, override_get_db, mock_db_session):
        import uuid
        from datetime import datetime, timezone
        import bcrypt

        hashed = bcrypt.hashpw(b"RealPass1", bcrypt.gensalt()).decode()

        from app.models.user import User
        fake_user = User(
            id=uuid.uuid4(),
            full_name="Wrong",
            email="wrong@example.com",
            hashed_password=hashed,
            role="buyer",
            is_verified=False,
            preferences={},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        mock_db_session.execute.return_value.scalar_one_or_none.return_value = fake_user

        payload = {"email": "wrong@example.com", "password": "WrongPass1"}
        response = await async_client.post("/api/auth/login", json=payload)
        assert response.status_code == 401
