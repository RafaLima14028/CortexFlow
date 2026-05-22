from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
    Cookie
)
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse
)
from src.core.database import get_db
from src.services.database.auth_db import (
    add_new_user,
    get_user_by_email,
    user_exists_by_id
)
from src.models.auth import (
    UserResponse,
    UserRegister
)
from src.core.security import (
    hash_password,
    verify_hashed_password,
    create_jwt_token,
    decode_jwt_token
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED
)
async def post_register_user(
    data: RegisterRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user: UserResponse | None = await get_user_by_email(data.email, db)

    if isinstance(user, UserResponse):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user is already registered"
        )

    await add_new_user(
        UserRegister(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(
                data.password
            )
        ),
        db
    )

    return Response(
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse
)
async def post_login_user(
    data: LoginRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    user: UserResponse | None = await get_user_by_email(data.email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_hashed_password(
        user.hashed_password,
        data.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_jwt_token(user.id, False, "access")
    refresh_token = create_jwt_token(user.id, True, "refresh")

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800
    )

    return LoginResponse(
        access_token=access_token
    )


@router.post(
    "/refresh",
    response_model=LoginResponse
)
async def post_refresh_token_user(
    response: Response,
    refresh_token: str | None = Cookie(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    payload = decode_jwt_token(refresh_token)

    user_exists = await user_exists_by_id(user_id, db)

    if not user_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not exists"
        )

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")

    access_token = create_jwt_token(user_id, False, "access")
    refresh_token = create_jwt_token(user_id, True, "refresh")

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800
    )

    return LoginResponse(
        access_token=access_token
    )
