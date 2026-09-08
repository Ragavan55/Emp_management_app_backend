from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core.security import create_access_token, hash_password, verify_password
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, summary="Create user")
async def signup(payload: SignupRequest) -> dict[str, str]:
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    existing = await User.find_one(User.email == payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists")

    username = (payload.name or "").strip() or payload.email.split("@", 1)[0]
    if len(username) < 3:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Name or email username must be at least 3 characters")

    now = datetime.utcnow()
    user = User(
        username=username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        created_at=now,
        updated_at=now,
    )
    await user.insert()
    return {"message": "User created successfully", "email": str(user.email)}


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticates a user with email and password and returns a JWT access token.",
    status_code=status.HTTP_200_OK,
)
async def login(payload: LoginRequest, response: Response) -> TokenResponse:
    user = await User.find_one(User.email == payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(user.email)
    # set a cookie so Next.js middleware can detect authenticated requests
    # HttpOnly cookie is used for security; client keeps localStorage copy too
    response.set_cookie("token", token, httponly=True, secure=True, samesite="none")
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Logout")
async def logout(response: Response) -> None:
    response.delete_cookie("token")


@router.get(
    "/me",
    response_model=dict,
    summary="Current user",
    description="Returns information for the authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> dict:
    return {"email": current_user.email, "username": current_user.username}
