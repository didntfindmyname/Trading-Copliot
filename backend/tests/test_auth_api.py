from __future__ import annotations

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_register_login_and_me(override_session: None) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        register = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "dev@athena.local",
                "password": "StrongPass123!",
                "full_name": "Dev User",
            },
        )
        assert register.status_code == 201

        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "dev@athena.local", "password": "StrongPass123!"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["email"] == "dev@athena.local"
