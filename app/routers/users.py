from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_permission
from app.core.security import hash_password
from app.models import User, Role
from app.schemas import UserCreate, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("users:create")),
):
    # 1. Verify username and email are not in use
    existing_query = select(User).where(
        (User.username == data.username) | (User.email == data.email)
    )
    result = await db.execute(existing_query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The username or email is already registered.",
        )

    # 2. Search for the requested roles by name
    if data.roles:
        roles_query = select(Role).where(Role.name.in_(data.roles))
        roles_result = await db.execute(roles_query)
        db_roles = list(roles_result.scalars().all())
        if len(db_roles) != len(data.roles):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more roles do not exist.",
            )
    else:
        db_roles = []

    # 3. Hash the password and create the user
    new_user = User(
        username=data.username,
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        is_active=data.is_active,
        roles=db_roles,
    )

    db.add(new_user)
    await db.commit()

    # 4. Re-query with roles loaded for the response
    complete_query = (
        select(User)
        .where(User.id == new_user.id)
        .options(selectinload(User.roles))
    )
    final_result = await db.execute(complete_query)
    complete_user = final_result.scalar_one()

    return complete_user