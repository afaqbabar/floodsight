"""Webhook and alert rule management endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    WebhookCreate,
    WebhookUpdate,
    WebhookResponse,
    WebhookDeliveryResponse,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertRuleResponse,
    AlertAcknowledgmentCreate,
    AlertAcknowledgmentResponse,
)
from app.core.logging import get_logger
from app.db.models import (
    Webhook,
    WebhookDelivery,
    AlertRule,
    Station,
    AlertAcknowledgment,
    Alert,
    User,
)
from app.db.session import get_db
from app.services.webhooks import webhook_service

logger = get_logger(__name__)

router = APIRouter()


# Webhook endpoints
@router.get("/webhooks", response_model=List[WebhookResponse], tags=["Webhooks"])
async def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> List[Webhook]:
    """List all webhooks."""
    query = select(Webhook)
    
    if active_only:
        query = query.where(Webhook.is_active == True)  # noqa: E712
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    webhooks = result.scalars().all()
    return list(webhooks)


@router.get("/webhooks/{webhook_id}", response_model=WebhookResponse, tags=["Webhooks"])
async def get_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
) -> Webhook:
    """Get a specific webhook."""
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with id {webhook_id} not found",
        )
    
    return webhook


@router.post(
    "/webhooks",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Webhooks"],
)
async def create_webhook(
    webhook: WebhookCreate,
    db: AsyncSession = Depends(get_db),
) -> Webhook:
    """Create a new webhook."""
    db_webhook = Webhook(**webhook.model_dump())
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)
    
    logger.info(f"Created webhook {webhook.name}")
    return db_webhook


@router.patch("/webhooks/{webhook_id}", response_model=WebhookResponse, tags=["Webhooks"])
async def update_webhook(
    webhook_id: int,
    webhook_update: WebhookUpdate,
    db: AsyncSession = Depends(get_db),
) -> Webhook:
    """Update a webhook."""
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with id {webhook_id} not found",
        )
    
    # Update fields
    update_data = webhook_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    await db.commit()
    await db.refresh(webhook)
    
    logger.info(f"Updated webhook {webhook.name}")
    return webhook


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Webhooks"])
async def delete_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a webhook."""
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with id {webhook_id} not found",
        )
    
    await db.delete(webhook)
    await db.commit()
    
    logger.info(f"Deleted webhook {webhook.name}")


@router.get(
    "/webhooks/{webhook_id}/deliveries",
    response_model=List[WebhookDeliveryResponse],
    tags=["Webhooks"],
)
async def list_webhook_deliveries(
    webhook_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[WebhookDelivery]:
    """List delivery logs for a webhook."""
    # Verify webhook exists
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webhook with id {webhook_id} not found",
        )
    
    # Get deliveries
    result = await db.execute(
        select(WebhookDelivery)
        .where(WebhookDelivery.webhook_id == webhook_id)
        .order_by(WebhookDelivery.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    deliveries = result.scalars().all()
    return list(deliveries)


@router.post(
    "/webhooks/retry",
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Webhooks"],
)
async def retry_failed_webhooks(
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Manually trigger retry of failed webhook deliveries."""
    count = await webhook_service.retry_failed_deliveries(db)
    
    return {
        "message": f"Retried {count} failed webhook deliveries",
        "count": count
    }


# Alert Rule endpoints
@router.get("/alert-rules", response_model=List[AlertRuleResponse], tags=["Alert Rules"])
async def list_alert_rules(
    station_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> List[AlertRule]:
    """List all alert rules."""
    query = select(AlertRule)
    
    if station_id:
        query = query.where(AlertRule.station_id == station_id)
    
    if active_only:
        query = query.where(AlertRule.is_active == True)  # noqa: E712
    
    query = query.order_by(AlertRule.priority.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    rules = result.scalars().all()
    return list(rules)


@router.get("/alert-rules/{rule_id}", response_model=AlertRuleResponse, tags=["Alert Rules"])
async def get_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
) -> AlertRule:
    """Get a specific alert rule."""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id {rule_id} not found",
        )
    
    return rule


@router.post(
    "/alert-rules",
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Alert Rules"],
)
async def create_alert_rule(
    rule: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
) -> AlertRule:
    """Create a new alert rule."""
    # Verify station exists
    result = await db.execute(select(Station).where(Station.id == rule.station_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with id {rule.station_id} not found",
        )
    
    db_rule = AlertRule(**rule.model_dump())
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    
    logger.info(f"Created alert rule {rule.name} for station {rule.station_id}")
    return db_rule


@router.patch("/alert-rules/{rule_id}", response_model=AlertRuleResponse, tags=["Alert Rules"])
async def update_alert_rule(
    rule_id: int,
    rule_update: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
) -> AlertRule:
    """Update an alert rule."""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id {rule_id} not found",
        )
    
    # Update fields
    update_data = rule_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    
    await db.commit()
    await db.refresh(rule)
    
    logger.info(f"Updated alert rule {rule.name}")
    return rule


@router.delete("/alert-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Alert Rules"])
async def delete_alert_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an alert rule."""
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with id {rule_id} not found",
        )
    
    await db.delete(rule)
    await db.commit()
    
    logger.info(f"Deleted alert rule {rule.name}")


# Alert Acknowledgment endpoints
@router.get(
    "/alert-acknowledgments",
    response_model=List[AlertAcknowledgmentResponse],
    tags=["Alert Acknowledgments"],
)
async def list_acknowledgments(
    alert_id: int | None = None,
    user_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> List[AlertAcknowledgment]:
    """List alert acknowledgments."""
    query = select(AlertAcknowledgment).order_by(AlertAcknowledgment.acknowledged_at.desc())
    
    if alert_id:
        query = query.where(AlertAcknowledgment.alert_id == alert_id)
    
    if user_id:
        query = query.where(AlertAcknowledgment.user_id == user_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    acknowledgments = result.scalars().all()
    return list(acknowledgments)


@router.post(
    "/alert-acknowledgments",
    response_model=AlertAcknowledgmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Alert Acknowledgments"],
)
async def acknowledge_alert(
    acknowledgment: AlertAcknowledgmentCreate,
    db: AsyncSession = Depends(get_db),
) -> AlertAcknowledgment:
    """Acknowledge an alert."""
    # Verify alert exists
    result = await db.execute(select(Alert).where(Alert.id == acknowledgment.alert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with id {acknowledgment.alert_id} not found",
        )
    
    # Verify user exists if provided
    if acknowledgment.user_id:
        result = await db.execute(select(User).where(User.id == acknowledgment.user_id))
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {acknowledgment.user_id} not found",
            )
    
    db_acknowledgment = AlertAcknowledgment(**acknowledgment.model_dump())
    db.add(db_acknowledgment)
    await db.commit()
    await db.refresh(db_acknowledgment)
    
    logger.info(f"Alert {acknowledgment.alert_id} acknowledged (action: {acknowledgment.action})")
    return db_acknowledgment



