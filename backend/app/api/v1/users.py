"""User and subscription management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
)
from app.core.logging import get_logger
from app.db.models import User, UserSubscription, Station
from app.db.session import get_db

logger = get_logger(__name__)

router = APIRouter()


# User endpoints
@router.get("/users", response_model=List[UserResponse], tags=["Users"])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[User]:
    """List all users."""
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    return list(users)


@router.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get a specific user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    
    return user


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user.email} already exists",
        )
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    logger.info(f"Created user {user.email}")
    return db_user


@router.patch("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    
    # Update fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"Updated user {user.email}")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    
    await db.delete(user)
    await db.commit()
    
    logger.info(f"Deleted user {user.email}")


# Subscription endpoints
@router.get(
    "/users/{user_id}/subscriptions",
    response_model=List[SubscriptionResponse],
    tags=["Subscriptions"],
)
async def list_user_subscriptions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> List[UserSubscription]:
    """List subscriptions for a user."""
    # Verify user exists
    result = await db.execute(select(User).where(User.id == user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    
    # Get subscriptions
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == user_id)
        .where(UserSubscription.is_active == True)  # noqa: E712
    )
    subscriptions = result.scalars().all()
    return list(subscriptions)


@router.post(
    "/subscriptions",
    response_model=SubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Subscriptions"],
)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
) -> UserSubscription:
    """Create a new subscription."""
    # Verify user exists
    result = await db.execute(select(User).where(User.id == subscription.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {subscription.user_id} not found",
        )
    
    # Verify station exists
    result = await db.execute(select(Station).where(Station.id == subscription.station_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id {subscription.station_id} not found",
        )
    
    # Check if subscription already exists
    result = await db.execute(
        select(UserSubscription)
        .where(UserSubscription.user_id == subscription.user_id)
        .where(UserSubscription.station_id == subscription.station_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        if not existing.is_active:
            # Reactivate
            existing.is_active = True
            await db.commit()
            await db.refresh(existing)
            logger.info(f"Reactivated subscription for user {subscription.user_id}")
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription already exists",
            )
    
    db_subscription = UserSubscription(**subscription.model_dump())
    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)
    
    logger.info(f"Created subscription for user {subscription.user_id} to station {subscription.station_id}")
    return db_subscription


@router.patch(
    "/subscriptions/{subscription_id}",
    response_model=SubscriptionResponse,
    tags=["Subscriptions"],
)
async def update_subscription(
    subscription_id: int,
    subscription_update: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserSubscription:
    """Update a subscription."""
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with id {subscription_id} not found",
        )
    
    # Update fields
    update_data = subscription_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    await db.commit()
    await db.refresh(subscription)
    
    logger.info(f"Updated subscription {subscription_id}")
    return subscription


@router.delete(
    "/subscriptions/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Subscriptions"],
)
async def delete_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a subscription."""
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with id {subscription_id} not found",
        )
    
    await db.delete(subscription)
    await db.commit()
    
    logger.info(f"Deleted subscription {subscription_id}")



