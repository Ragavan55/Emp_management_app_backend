from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import create_access_token, verify_password
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticates a user with email and password and returns a JWT access token.",
    status_code=status.HTTP_200_OK,
)
async def login(payload: LoginRequest) -> TokenResponse:
    user = await User.find_one(User.email == payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get(
    "/me",
    response_model=dict,
    summary="Current user",
    description="Returns information for the authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)) -> dict:
    return {"email": current_user.email, "username": current_user.username}
