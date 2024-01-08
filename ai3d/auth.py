from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from . import schemas, crud, utils
from .database import AsyncSession, get_db

SECRET_KEY = "f894cbd4230cd870a16903c9f7a949e5512b231b54f9c8e8dbcd2e7fb7ba2728"
TOKEN_EXPIRATION = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


def verify_password(plain_password, hashed_password) -> bool:
    return utils.pwd_context.verify(plain_password, hashed_password)


async def get_user(db: AsyncSession, username: str) -> schemas.UserInDB | None:
    user = await crud.get_user(db=db, username=username)
    if user:
        return schemas.UserInDB.model_validate(user)


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> schemas.UserInDB | bool:
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(plain_password=password, hashed_password=user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> schemas.UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
