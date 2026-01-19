"""Tests for authentication functionality."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    get_token_expiry_seconds,
)


# =============================================================================
# Auth Service Tests
# =============================================================================


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_string(self):
        """Hash password returns a bcrypt hash string."""
        result = hash_password("testpassword")
        assert isinstance(result, str)
        assert result.startswith("$2")  # bcrypt hash prefix

    def test_hash_password_different_each_time(self):
        """Same password produces different hashes (salt)."""
        hash1 = hash_password("testpassword")
        hash2 = hash_password("testpassword")
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Correct password verifies successfully."""
        password = "mysecretpassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password fails verification."""
        hashed = hash_password("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_empty_fails(self):
        """Empty password fails verification."""
        hashed = hash_password("somepassword")
        assert verify_password("", hashed) is False


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_access_token_returns_string(self):
        """Create access token returns a JWT string."""
        token = create_access_token({"sub": "123"})
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long

    def test_decode_token_valid(self):
        """Valid token decodes successfully."""
        token = create_access_token({"sub": "456", "extra": "data"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "456"
        assert payload["extra"] == "data"
        assert "exp" in payload

    def test_decode_token_invalid(self):
        """Invalid token returns None."""
        payload = decode_token("invalid.token.here")
        assert payload is None

    def test_decode_token_tampered(self):
        """Tampered token returns None."""
        token = create_access_token({"sub": "123"})
        # Modify the token
        tampered = token[:-5] + "xxxxx"
        payload = decode_token(tampered)
        assert payload is None

    def test_get_token_expiry_seconds(self):
        """Token expiry is returned in seconds."""
        seconds = get_token_expiry_seconds()
        assert isinstance(seconds, int)
        assert seconds > 0
        # Default is 24 hours = 86400 seconds
        assert seconds == 24 * 3600


# =============================================================================
# Auth API Tests
# =============================================================================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user for authentication tests."""
    user = User(
        username="testuser",
        password_hash=hash_password("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Get an auth token for the test user."""
    return create_access_token({"sub": str(test_user.id)})


class TestLoginEndpoint:
    """Tests for POST /api/auth/login."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Successful login returns token."""
        response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Wrong password returns 401."""
        response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Nonexistent user returns 401."""
        response = await client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "anypassword"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_updates_last_login(
        self, client: AsyncClient, test_user: User, db_session: AsyncSession
    ):
        """Successful login updates last_login timestamp."""
        assert test_user.last_login is None

        await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )

        # Refresh user from database
        await db_session.refresh(test_user)
        assert test_user.last_login is not None

    @pytest.mark.asyncio
    async def test_login_empty_username(self, client: AsyncClient):
        """Empty username returns validation error."""
        response = await client.post(
            "/api/auth/login",
            json={"username": "", "password": "somepassword"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient):
        """Missing fields return validation error."""
        response = await client.post("/api/auth/login", json={})
        assert response.status_code == 422


class TestMeEndpoint:
    """Tests for GET /api/auth/me."""

    @pytest.mark.asyncio
    async def test_me_authenticated(
        self, client: AsyncClient, test_user: User, auth_token: str
    ):
        """Authenticated request returns user info."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == "testuser"
        assert "created_at" in data
        assert "password_hash" not in data  # Should not expose password

    @pytest.mark.asyncio
    async def test_me_no_token(self, client: AsyncClient):
        """Request without token returns 401."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_invalid_token(self, client: AsyncClient):
        """Invalid token returns 401."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_me_token_with_nonexistent_user(self, client: AsyncClient):
        """Token for deleted user returns 401."""
        # Create token for non-existent user ID
        token = create_access_token({"sub": "99999"})
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401


class TestPasswordChangeEndpoint:
    """Tests for PUT /api/auth/password."""

    @pytest.mark.asyncio
    async def test_change_password_success(
        self, client: AsyncClient, test_user: User, auth_token: str, db_session: AsyncSession
    ):
        """Successful password change."""
        response = await client.put(
            "/api/auth/password",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "current_password": "testpass123",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

        # Verify new password works
        await db_session.refresh(test_user)
        assert verify_password("newpassword123", test_user.password_hash)

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, client: AsyncClient, auth_token: str
    ):
        """Wrong current password returns 400."""
        response = await client.put(
            "/api/auth/password",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_change_password_too_short(
        self, client: AsyncClient, auth_token: str
    ):
        """New password too short returns validation error."""
        response = await client.put(
            "/api/auth/password",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "current_password": "testpass123",
                "new_password": "short",  # Less than 6 chars
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_change_password_no_auth(self, client: AsyncClient):
        """Request without auth returns 401."""
        response = await client.put(
            "/api/auth/password",
            json={
                "current_password": "testpass123",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 401


# =============================================================================
# Integration Tests
# =============================================================================


class TestAuthIntegration:
    """Integration tests for complete auth flow."""

    @pytest.mark.asyncio
    async def test_full_auth_flow(self, client: AsyncClient, test_user: User):
        """Test complete authentication flow."""
        # 1. Login
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 2. Access protected endpoint
        me_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "testuser"

        # 3. Change password
        password_response = await client.put(
            "/api/auth/password",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "current_password": "testpass123",
                "new_password": "newpassword456",
            },
        )
        assert password_response.status_code == 200

        # 4. Login with new password
        new_login_response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "newpassword456"},
        )
        assert new_login_response.status_code == 200

        # 5. Old password no longer works
        old_login_response = await client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert old_login_response.status_code == 401
