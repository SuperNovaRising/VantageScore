from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST
import pytest
from unittest.mock import patch
from auth.auth import app, User, get_user, write_to_userdb, create_access_token, get_current_user, get_current_active_admin, get_current_active_user

client = TestClient(app)

def mock_get_user(username):
    if username == "test_user":
        return ("test_user", "hashedpassword123")
    elif username == "admin":
        return ("admin", "hashedpassword")
    elif username == "user":  # Make sure to add this case
        return ("user", "userpassword")
    else:
        return None

def mock_write_to_userdb(user):
    return None

def mock_create_access_token(data, expires_delta):
    return "fake-jwt-token"

# TODO: Strangely, adding auth at front solved the path resolution problem.
@patch("auth.auth.get_user", side_effect=mock_get_user)
@patch("auth.auth.write_to_userdb", side_effect=mock_write_to_userdb)
@patch("auth.auth.create_access_token", side_effect=mock_create_access_token)
# The @patch decorators are applied from the bottom up, contrary to how they are listed in the code.
def test_signup(mock_create_access_token, mock_write_to_userdb, mock_get_user):
    # Test signup with a new user
    response = client.post("/signup/", json={"username": "new_user", "hashed_password": "newpassword123"})
    assert response.status_code == 200
    assert response.json() == {"username": "new_user", "access_token": "fake-jwt-token"}

    # Test signup with an existing user
    response = client.post("/signup/", json={"username": "test_user", "hashed_password": "hashedpassword123"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

@patch("auth.auth.get_user", side_effect=mock_get_user)
@patch("auth.auth.write_to_userdb", side_effect=mock_write_to_userdb)
@patch("auth.auth.create_access_token", side_effect=mock_create_access_token)
def test_login(mock_create_access_token, mock_write_to_userdb, mock_get_user):
    response = client.post("/login/", data={"username": "test_user", "password": "hashedpassword123"})
    assert response.status_code == 200
    assert response.json() == {"access_token": "fake-jwt-token", "token_type": "bearer"}

    response = client.post("/login/", data={"username": "wrong_user", "password": "wrong_password"})
    assert response.status_code == 401
    assert "detail" in response.json()

def mock_decode_token(token, secret_key, **kwargs):
    if token == "valid_admin_token":
        return {"sub": "admin"}
    elif token == "valid_user_token":
        return {"sub": "user"}    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@pytest.mark.asyncio
@patch("auth.auth.jwt.decode", side_effect=mock_decode_token)
@patch("auth.auth.get_user", side_effect=mock_get_user)
async def test_get_current_user(mock_get_user, mock_decode):
    # Test valid case
    user = await get_current_user("valid_admin_token")
    assert user.username == "admin"

    user = await get_current_user("valid_user_token")
    assert user.username == "user"

    # Test invalid token case
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token")
    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
@patch("auth.auth.get_current_user", side_effect=mock_get_user)
async def test_get_current_active_admin(mock_get_current_user):
    # Test admin case
    admin_user = await get_current_active_admin(User(username="admin", hashed_password="hashedpassword"))
    assert admin_user.username == "admin"

    # Test non-admin case
    with pytest.raises(HTTPException) as excinfo:
        await get_current_active_admin(User(username="unregistered", hashed_password="hashedpassword"))
    assert excinfo.value.status_code == HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
@patch("auth.auth.get_current_user", side_effect=mock_get_user)
async def test_get_current_active_user(mock_get_current_user):
    # Test admin case
    admin_user = await get_current_active_user(User(username="admin", hashed_password="hashedpassword"))
    assert admin_user.username == "admin"

    # Test general user case
    other_user = await get_current_active_user(User(username="user", hashed_password="hashedpassword123"))
    assert other_user.username == "user"

    # Test non-admin case
    with pytest.raises(HTTPException) as excinfo:
        await get_current_active_admin(User(username="unregistered", hashed_password="hashedpassword"))
    assert excinfo.value.status_code == HTTP_400_BAD_REQUEST