"""Webhook service for delivering alerts to external systems."""
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import (
    Alert,
    Station,
    Webhook,
    WebhookDelivery,
)

logger = get_logger(__name__)


class WebhookService:
    """Service for delivering alerts via webhooks."""

    async def deliver_alert_to_webhooks(
        self,
        alert: Alert,
        station: Station,
        db: AsyncSession
    ) -> int:
        """
        Deliver an alert to all configured webhooks.
        
        Args:
            alert: The alert to deliver
            station: The station for the alert
            db: Database session
            
        Returns:
            Number of webhooks triggered
        """
        logger.info(f"Delivering alert {alert.id} to webhooks")
        
        # Get active webhooks
        result = await db.execute(
            select(Webhook)
            .where(Webhook.is_active == True)  # noqa: E712
        )
        webhooks = result.scalars().all()
        
        if not webhooks:
            logger.info("No active webhooks configured")
            return 0
        
        # Filter webhooks based on alert level and station filter
        alert_level_order = ["info", "warning", "severe", "extreme"]
        alert_level_index = alert_level_order.index(alert.level)
        
        eligible_webhooks = []
        for webhook in webhooks:
            # Check minimum alert level
            min_level_index = alert_level_order.index(webhook.min_alert_level)
            if alert_level_index < min_level_index:
                continue
            
            # Check station filter
            if webhook.station_filter:
                if station.id not in webhook.station_filter:
                    continue
            
            eligible_webhooks.append(webhook)
        
        if not eligible_webhooks:
            logger.info(f"No eligible webhooks for alert level {alert.level}")
            return 0
        
        # Deliver to all eligible webhooks
        tasks = []
        for webhook in eligible_webhooks:
            tasks.append(self._deliver_to_webhook(webhook, alert, station, db))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        success_count = sum(1 for r in results if r and not isinstance(r, Exception))
        
        logger.info(f"Delivered alert {alert.id} to {success_count}/{len(eligible_webhooks)} webhooks")
        return success_count

    async def _deliver_to_webhook(
        self,
        webhook: Webhook,
        alert: Alert,
        station: Station,
        db: AsyncSession
    ) -> bool:
        """
        Deliver an alert to a specific webhook.
        
        Args:
            webhook: The webhook configuration
            alert: The alert to deliver
            station: The station for the alert
            db: Database session
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        logger.info(f"Delivering alert {alert.id} to webhook {webhook.name}")
        
        # Create delivery record
        delivery = WebhookDelivery(
            webhook_id=webhook.id,
            alert_id=alert.id,
            status="pending",
            attempt_number=1,
        )
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)
        
        # Prepare payload based on webhook type
        payload = self._prepare_payload(webhook, alert, station)
        
        # Attempt delivery
        success = await self._attempt_delivery(webhook, payload, delivery, db)
        
        if not success and webhook.max_retries > 0:
            # Schedule retry
            next_retry = datetime.now(timezone.utc) + timedelta(
                seconds=webhook.retry_delay_seconds
            )
            delivery.status = "retrying"
            delivery.next_retry_at = next_retry
            await db.commit()
            
            logger.info(
                f"Webhook {webhook.name} delivery failed, "
                f"will retry at {next_retry}"
            )
        
        return success

    def _prepare_payload(
        self,
        webhook: Webhook,
        alert: Alert,
        station: Station
    ) -> Dict:
        """
        Prepare webhook payload based on webhook type.
        
        Args:
            webhook: The webhook configuration
            alert: The alert
            station: The station
            
        Returns:
            Payload dictionary
        """
        # Base payload for generic webhooks
        base_payload = {
            "alert_id": alert.id,
            "station": {
                "id": station.id,
                "code": station.code,
                "name": station.name,
                "lat": station.lat,
                "lon": station.lon,
                "river_basin": station.river_basin,
            },
            "level": alert.level,
            "probability": alert.probability,
            "message": alert.message,
            "issued_at": alert.issued_at.isoformat(),
            "is_active": alert.is_active,
        }
        
        # Format for specific webhook types
        if webhook.webhook_type == "slack":
            return self._format_slack_payload(base_payload, alert)
        elif webhook.webhook_type == "discord":
            return self._format_discord_payload(base_payload, alert)
        elif webhook.webhook_type == "telegram":
            return self._format_telegram_payload(base_payload, alert)
        elif webhook.webhook_type == "teams":
            return self._format_teams_payload(base_payload, alert)
        else:
            # Generic webhook
            return base_payload

    def _format_slack_payload(self, data: Dict, alert: Alert) -> Dict:
        """Format payload for Slack."""
        colors = {
            "info": "#2196F3",
            "warning": "#FF9800",
            "severe": "#F44336",
            "extreme": "#9C27B0",
        }
        
        return {
            "attachments": [{
                "color": colors.get(alert.level, "#2196F3"),
                "title": f"🌊 {alert.level.upper()} Flood Alert",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Station",
                        "value": f"{data['station']['name']} ({data['station']['code']})",
                        "short": True
                    },
                    {
                        "title": "Probability",
                        "value": f"{alert.probability * 100:.0f}%",
                        "short": True
                    },
                ],
                "footer": "FloodSight Alert System",
                "ts": int(alert.issued_at.timestamp()),
            }]
        }

    def _format_discord_payload(self, data: Dict, alert: Alert) -> Dict:
        """Format payload for Discord."""
        colors = {
            "info": 0x2196F3,
            "warning": 0xFF9800,
            "severe": 0xF44336,
            "extreme": 0x9C27B0,
        }
        
        return {
            "embeds": [{
                "title": f"🌊 {alert.level.upper()} Flood Alert",
                "description": alert.message,
                "color": colors.get(alert.level, 0x2196F3),
                "fields": [
                    {
                        "name": "Station",
                        "value": f"{data['station']['name']} ({data['station']['code']})",
                        "inline": True
                    },
                    {
                        "name": "Probability",
                        "value": f"{alert.probability * 100:.0f}%",
                        "inline": True
                    },
                ],
                "timestamp": alert.issued_at.isoformat(),
                "footer": {
                    "text": "FloodSight Alert System"
                }
            }]
        }

    def _format_telegram_payload(self, data: Dict, alert: Alert) -> Dict:
        """Format payload for Telegram."""
        emoji = {"info": "ℹ️", "warning": "⚠️", "severe": "🚨", "extreme": "🔴"}
        
        message = f"""
{emoji.get(alert.level, '🌊')} <b>{alert.level.upper()} Flood Alert</b>

<b>Station:</b> {data['station']['name']} ({data['station']['code']})
<b>Probability:</b> {alert.probability * 100:.0f}%
<b>Issued:</b> {alert.issued_at.strftime('%Y-%m-%d %H:%M UTC')}

{alert.message}
"""
        
        return {
            "text": message,
            "parse_mode": "HTML"
        }

    def _format_teams_payload(self, data: Dict, alert: Alert) -> Dict:
        """Format payload for Microsoft Teams."""
        colors = {
            "info": "0078D4",
            "warning": "FFA500",
            "severe": "DC143C",
            "extreme": "8B008B",
        }
        
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": f"{alert.level.upper()} Flood Alert",
            "themeColor": colors.get(alert.level, "0078D4"),
            "title": f"🌊 {alert.level.upper()} Flood Alert",
            "sections": [{
                "activityTitle": f"{data['station']['name']} ({data['station']['code']})",
                "facts": [
                    {"name": "Alert Level", "value": alert.level.upper()},
                    {"name": "Probability", "value": f"{alert.probability * 100:.0f}%"},
                    {"name": "Issued", "value": alert.issued_at.strftime('%Y-%m-%d %H:%M UTC')},
                ],
                "text": alert.message
            }]
        }

    async def _attempt_delivery(
        self,
        webhook: Webhook,
        payload: Dict,
        delivery: WebhookDelivery,
        db: AsyncSession
    ) -> bool:
        """
        Attempt to deliver payload to webhook.
        
        Args:
            webhook: The webhook configuration
            payload: The payload to send
            delivery: The delivery record
            db: Database session
            
        Returns:
            True if delivery succeeded, False otherwise
        """
        try:
            headers = webhook.headers or {}
            headers.setdefault("Content-Type", "application/json")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    delivery.status_code = response.status
                    
                    if response.status in [200, 201, 202, 204]:
                        # Success
                        delivery.status = "success"
                        delivery.completed_at = datetime.now(timezone.utc)
                        response_body = await response.text()
                        delivery.response_body = response_body[:1000]  # Limit size
                        
                        await db.commit()
                        
                        logger.info(
                            f"Successfully delivered to webhook {webhook.name} "
                            f"(status: {response.status})"
                        )
                        return True
                    else:
                        # Failure
                        error_body = await response.text()
                        delivery.status = "failed"
                        delivery.error_message = f"HTTP {response.status}: {error_body[:500]}"
                        delivery.completed_at = datetime.now(timezone.utc)
                        
                        await db.commit()
                        
                        logger.error(
                            f"Webhook {webhook.name} returned status {response.status}: "
                            f"{error_body[:200]}"
                        )
                        return False
        
        except Exception as e:
            delivery.status = "failed"
            delivery.error_message = str(e)[:500]
            delivery.completed_at = datetime.now(timezone.utc)
            
            await db.commit()
            
            logger.error(f"Failed to deliver to webhook {webhook.name}: {e}")
            return False

    async def retry_failed_deliveries(self, db: AsyncSession) -> int:
        """
        Retry failed webhook deliveries that are due for retry.
        
        Args:
            db: Database session
            
        Returns:
            Number of deliveries retried
        """
        now = datetime.now(timezone.utc)
        
        # Get deliveries ready for retry
        result = await db.execute(
            select(WebhookDelivery, Webhook, Alert, Station)
            .join(Webhook, WebhookDelivery.webhook_id == Webhook.id)
            .join(Alert, WebhookDelivery.alert_id == Alert.id)
            .join(Station, Alert.station_id == Station.id)
            .where(WebhookDelivery.status == "retrying")
            .where(WebhookDelivery.next_retry_at <= now)
        )
        pending = result.all()
        
        if not pending:
            return 0
        
        logger.info(f"Retrying {len(pending)} failed webhook deliveries")
        
        retry_count = 0
        for delivery, webhook, alert, station in pending:
            if delivery.attempt_number >= webhook.max_retries:
                # Max retries reached
                delivery.status = "failed"
                delivery.error_message = (
                    f"{delivery.error_message or ''}\n"
                    f"Max retries ({webhook.max_retries}) reached"
                )
                delivery.completed_at = now
                await db.commit()
                
                logger.warning(
                    f"Webhook {webhook.name} delivery {delivery.id} "
                    f"failed after {delivery.attempt_number} attempts"
                )
                continue
            
            # Increment attempt number
            delivery.attempt_number += 1
            await db.commit()
            
            # Prepare payload and attempt delivery
            payload = self._prepare_payload(webhook, alert, station)
            success = await self._attempt_delivery(webhook, payload, delivery, db)
            
            if not success and delivery.attempt_number < webhook.max_retries:
                # Schedule next retry
                next_retry = now + timedelta(seconds=webhook.retry_delay_seconds)
                delivery.next_retry_at = next_retry
                await db.commit()
            
            retry_count += 1
        
        logger.info(f"Completed {retry_count} webhook delivery retries")
        return retry_count


# Global instance
webhook_service = WebhookService()



