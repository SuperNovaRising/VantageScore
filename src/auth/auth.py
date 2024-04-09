from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import psycopg2
from datetime import datetime, timedelta
from jwt import decode, encode, PyJWTError
import os
from typing import Optional

SECRET_KEY = "VantageScore"
ALGORITHM = "HS256"

app = FastAPI()

# Define a simple user model for demonstration
class User(BaseModel):
    username: str
    hashed_password: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user(username)
        if user is None:
            raise credentials_exception
        return User(username=user[0], hashed_password=user[1])
    except PyJWTError:
        raise credentials_exception

async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.username == "admin":
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return current_user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=400, detail="The user is not a registered user")
    return current_user

# This method is multi-tasked to check if a user already exists and fetch the hashed_password
def get_user(username):
    connection = None
    try:
        # Establish a connection to the database
        connection = psycopg2.connect(
            database="users",  
            user="root",
            password="password", # TODO: Move this to kubernetes secrets
            #   running on kubernetes, uvicorn locally
            # Unfortunately, I have trouble having Docker container to resolve the localhost correctly
            host=os.getenv("DB_HOST", "localhost"),
            port="5432"
        )
        cursor = connection.cursor()
        
        # Execute a query
        cursor.execute("SELECT * FROM account WHERE username = %s", (username,))
        
        # Fetch and print the result of the query
        user = cursor.fetchone()

        return user
    except Exception as e:
        print("Error while connecting to PostgreSQL", e)
    finally: 
        if connection:
            cursor.close()
            connection.close()

def write_to_userdb(user: User):
    connection = None
    try:
        # Establish a connection to the database
        connection = psycopg2.connect(
            database="users",
            user="root",
            password="password",
            #   running on kubernetes, docker container
            host=os.getenv("DB_HOST", "localhost"),
            port="5432"
        )
        cursor = connection.cursor()
        
        # Execute an insertion
        cursor.execute("INSERT INTO account (username, hashed_password) VALUES (%s, %s)", (user.username, user.hashed_password))
        connection.commit()
    except Exception as e:
        print("Error while connecting to PostgreSQL", e)
        raise e
    finally: 
        if connection:
            cursor.close()
            connection.close()
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/signup/")
def signup(user: User):
    if get_user(user.username) is not None:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Assume the front end application hashes the password using bcrypt
    write_to_userdb(user)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"username": user.username, "access_token": access_token}

def authenticate_user(username, hashed_password):
    user = get_user(username)
    if user is not None and user[1] == hashed_password:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user[0]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
