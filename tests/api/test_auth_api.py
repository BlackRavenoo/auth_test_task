from uuid import uuid4

import pytest

@pytest.fixture
def payload() -> dict[str, str]:
    token = uuid4().hex
    return {
        "name": f"User {token[:6]}",
        "email": f"{token}@example.com",
        "password": "strong-password-123",
        "password_repeat": "strong-password-123",
    }

@pytest.mark.asyncio
async def test_register_success(client, payload):
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_register_duplicate_email(client, payload):
    first = await client.post("/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/auth/register", json=payload)
    assert second.status_code == 409

@pytest.mark.asyncio
async def test_login_success(client, payload):
    await client.post("/auth/register", json=payload)

    response = await client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_invalid_password(client, payload):
    await client.post("/auth/register", json=payload)

    response = await client.post(
        "/auth/login",
        json={"email": payload["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_refresh_success_and_old_token_revoked(client, payload):
    await client.post("/auth/register", json=payload)

    login = await client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    login_data = login.json()

    refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert refresh.status_code == 200

    old_refresh = await client.post(
        "/auth/refresh",
        json={"refresh_token": login_data["refresh_token"]},
    )
    assert old_refresh.status_code == 401

@pytest.mark.asyncio
async def test_logout_requires_authorization_header(client):
    response = await client.post(
        "/auth/logout",
        json={"refresh_token": "something"},
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout_success(client, payload):
    await client.post("/auth/register", json=payload)

    login = await client.post(
        "/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    login_data = login.json()

    response = await client.post(
        "/auth/logout",
        json={"refresh_token": login_data["refresh_token"]},
        headers={"Authorization": f"Bearer {login_data['access_token']}"},
    )
    assert response.status_code == 200
