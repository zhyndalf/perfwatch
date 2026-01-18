# T004: Auth Backend

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 1 - Foundation |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T003 (Database Setup) |
| **Status** | ⬜ NOT_STARTED |

---

## Objective

Implement JWT-based authentication with FastAPI including login, logout, and protected route middleware.

---

## Context

Authentication requirements:
- Single admin user (initially)
- JWT tokens for API access
- 24-hour token expiration
- Password hashing with bcrypt

Keep it simple - this is for local use only.

---

## Specifications

Reference documents:
- [API Spec - Authentication](../../02-specification/api-spec.md#authentication)
- [Data Model - Users](../../02-specification/data-model.md#table-users)

---

## Acceptance Criteria

### Auth Service
- [ ] Password hashing with bcrypt
- [ ] Password verification
- [ ] JWT token generation
- [ ] JWT token validation
- [ ] Token expiration handling

### Endpoints
- [ ] `POST /api/auth/login` - Returns JWT token
- [ ] `POST /api/auth/logout` - Invalidates session (optional)
- [ ] `GET /api/auth/me` - Returns current user
- [ ] `PUT /api/auth/password` - Change password

### Middleware
- [ ] Auth dependency for protected routes
- [ ] Extract user from token
- [ ] Return 401 for invalid/missing token

### Security
- [ ] Passwords never stored in plain text
- [ ] Tokens are cryptographically signed
- [ ] Sensitive data not in token payload

---

## Implementation Details

### Auth Service

```python
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
```

### Auth Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### Login Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_username(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    # Create token
    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_EXPIRE_HOURS * 3600
    }
```

### Pydantic Schemas

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
```

---

## Files to Create

| File | Description |
|------|-------------|
| `backend/app/services/auth.py` | Auth service functions |
| `backend/app/api/auth.py` | Auth API endpoints |
| `backend/app/api/deps.py` | Dependencies (get_current_user) |
| `backend/app/schemas/user.py` | User-related schemas |
| `backend/app/schemas/auth.py` | Auth-related schemas |

---

## Verification Steps

```bash
# Start services
docker-compose up -d

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Save token
TOKEN="<token from response>"

# Test protected endpoint
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Test invalid token
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer invalid"
# Should return 401

# Test password change
curl -X PUT http://localhost:8000/api/auth/password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"current_password":"admin123","new_password":"newpass123"}'
```

---

## Implementation Notes

*To be filled during implementation*

---

## Files Created/Modified

*To be filled during implementation*
