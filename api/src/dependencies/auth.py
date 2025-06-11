from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from src.core.config import settings
from src.schemas.integrations.github import TokenData

security = HTTPBearer()


async def get_current_user(credentials: Annotated[HTTPBearer, Depends(security)]) -> TokenData:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if (user_id := payload.get("sub")) is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token") from None
