"""Notification service for sending alerts via multiple channels."""
import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json

import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import (
    Alert,
    User,
    UserSubscription,
    NotificationLog,
    Station,
)

logger = get_logger(__name__)


class NotificationService:
    """Service for sending notifications via multiple channels."""

    def __init__(self):
        """Initialize notification service."""
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user)
        
        # Twilio SMS
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
        
        # Firebase Cloud Messaging
        self.fcm_server_key = os.getenv("FCM_SERVER_KEY")
        
        # OneSignal
        self.onesignal_app_id = os.getenv("ONESIGNAL_APP_ID")
        self.onesignal_api_key = os.getenv("ONESIGNAL_API_KEY")
        
        # Telegram
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Discord
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        # Slack
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    async def send_alert_notifications(
        self,
        alert: Alert,
        station: Station,
        db: AsyncSession
    ) -> Dict[str, int]:
        """
        Send notifications for an alert to all subscribed users.
        
        Args:
            alert: The alert to notify about
            station: The station for the alert
            db: Database session
            
        Returns:
            Dict with counts of notifications sent by type
        """
        logger.info(f"Sending notifications for alert {alert.id} at station {station.code}")
        
        # Get subscribed users for this station
        result = await db.execute(
            select(User, UserSubscription)
            .join(UserSubscription, User.id == UserSubscription.user_id)
            .where(UserSubscription.station_id == station.id)
            .where(UserSubscription.is_active == True)  # noqa: E712
            .where(User.is_active == True)  # noqa: E712
        )
        subscriptions = result.all()
        
        if not subscriptions:
            logger.info(f"No active subscriptions for station {station.code}")
            return {"email": 0, "sms": 0, "push": 0}
        
        # Filter users based on minimum alert level
        alert_level_order = ["info", "warning", "severe", "extreme"]
        alert_level_index = alert_level_order.index(alert.level)
        
        eligible_users = []
        for user, subscription in subscriptions:
            min_level_index = alert_level_order.index(subscription.min_alert_level)
            if alert_level_index >= min_level_index:
                eligible_users.append((user, subscription))
        
        if not eligible_users:
            logger.info(f"No eligible users for alert level {alert.level}")
            return {"email": 0, "sms": 0, "push": 0}
        
        # Send notifications
        counts = {"email": 0, "sms": 0, "push": 0}
        
        tasks = []
        for user, subscription in eligible_users:
            prefs = user.notification_preferences or {}
            
            # Email notification
            if prefs.get("email", True) and user.email:
                tasks.append(self._send_email_notification(alert, station, user, db))
            
            # SMS notification
            if prefs.get("sms", False) and user.phone:
                tasks.append(self._send_sms_notification(alert, station, user, db))
            
            # Push notification
            if prefs.get("push", False) and user.push_tokens:
                tasks.append(self._send_push_notification(alert, station, user, db))
        
        # Send all notifications concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successes
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Notification error: {result}")
            elif result:
                notification_type = result.get("type")
                if notification_type in counts:
                    counts[notification_type] += 1
        
        logger.info(f"Sent {sum(counts.values())} notifications for alert {alert.id}")
        return counts

    async def _send_email_notification(
        self,
        alert: Alert,
        station: Station,
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, str]]:
        """Send email notification."""
        if not self.smtp_host or not self.smtp_user:
            logger.warning("SMTP not configured, skipping email")
            return None
        
        try:
            # Import here to avoid dependency issues if not installed
            import aiosmtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Flood Alert: {alert.level.upper()} - {station.name}"
            msg["From"] = self.smtp_from
            msg["To"] = user.email
            
            # Plain text version
            text = f"""
Flood Alert Notification
========================

Station: {station.name} ({station.code})
Alert Level: {alert.level.upper()}
Probability: {alert.probability * 100:.0f}%
Issued: {alert.issued_at.strftime('%Y-%m-%d %H:%M UTC')}

Message:
{alert.message}

---
FloodSight Alert System
"""
            
            # HTML version
            html = f"""
<html>
  <body style="font-family: Arial, sans-serif;">
    <h2 style="color: {'#d32f2f' if alert.level in ['severe', 'extreme'] else '#f57c00' if alert.level == 'warning' else '#1976d2'};">
      🌊 Flood Alert: {alert.level.upper()}
    </h2>
    <p><strong>Station:</strong> {station.name} ({station.code})</p>
    <p><strong>Alert Level:</strong> {alert.level.upper()}</p>
    <p><strong>Probability:</strong> {alert.probability * 100:.0f}%</p>
    <p><strong>Issued:</strong> {alert.issued_at.strftime('%Y-%m-%d %H:%M UTC')}</p>
    <hr>
    <p>{alert.message}</p>
    <hr>
    <p style="color: #666; font-size: 12px;">FloodSight Alert System</p>
  </body>
</html>
"""
            
            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))
            
            # Send email
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True,
            )
            
            # Log success
            log = NotificationLog(
                alert_id=alert.id,
                user_id=user.id,
                notification_type="email",
                recipient=user.email,
                status="sent",
                provider="smtp",
            )
            db.add(log)
            await db.commit()
            
            logger.info(f"Sent email to {user.email}")
            return {"type": "email", "recipient": user.email}
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")
            
            # Log failure
            log = NotificationLog(
                alert_id=alert.id,
                user_id=user.id,
                notification_type="email",
                recipient=user.email,
                status="failed",
                error_message=str(e),
                provider="smtp",
            )
            db.add(log)
            await db.commit()
            
            return None

    async def _send_sms_notification(
        self,
        alert: Alert,
        station: Station,
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, str]]:
        """Send SMS notification via Twilio."""
        if not self.twilio_account_sid or not self.twilio_auth_token:
            logger.warning("Twilio not configured, skipping SMS")
            return None
        
        try:
            # Create SMS message
            message_body = (
                f"🌊 FLOOD ALERT: {alert.level.upper()}\n"
                f"{station.name}\n"
                f"{alert.message[:100]}..."  # Limit length for SMS
            )
            
            # Send via Twilio API
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.twilio_account_sid, self.twilio_auth_token)
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
                
                data = {
                    "From": self.twilio_from_number,
                    "To": user.phone,
                    "Body": message_body,
                }
                
                async with session.post(url, auth=auth, data=data) as response:
                    if response.status == 201:
                        result = await response.json()
                        message_sid = result.get("sid")
                        
                        # Log success
                        log = NotificationLog(
                            alert_id=alert.id,
                            user_id=user.id,
                            notification_type="sms",
                            recipient=user.phone,
                            status="sent",
                            provider="twilio",
                            provider_message_id=message_sid,
                        )
                        db.add(log)
                        await db.commit()
                        
                        logger.info(f"Sent SMS to {user.phone}")
                        return {"type": "sms", "recipient": user.phone}
                    else:
                        error_text = await response.text()
                        raise Exception(f"Twilio API error: {error_text}")
            
        except Exception as e:
            logger.error(f"Failed to send SMS to {user.phone}: {e}")
            
            # Log failure
            log = NotificationLog(
                alert_id=alert.id,
                user_id=user.id,
                notification_type="sms",
                recipient=user.phone,
                status="failed",
                error_message=str(e),
                provider="twilio",
            )
            db.add(log)
            await db.commit()
            
            return None

    async def _send_push_notification(
        self,
        alert: Alert,
        station: Station,
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, str]]:
        """Send push notification via Firebase or OneSignal."""
        push_tokens = user.push_tokens or {}
        
        # Try Firebase first
        if self.fcm_server_key and push_tokens.get("fcm"):
            return await self._send_fcm_notification(alert, station, user, db)
        
        # Try OneSignal
        if self.onesignal_app_id and push_tokens.get("onesignal"):
            return await self._send_onesignal_notification(alert, station, user, db)
        
        logger.warning(f"No push tokens configured for user {user.email}")
        return None

    async def _send_fcm_notification(
        self,
        alert: Alert,
        station: Station,
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, str]]:
        """Send Firebase Cloud Messaging notification."""
        try:
            push_tokens = user.push_tokens or {}
            fcm_token = push_tokens.get("fcm")
            
            if not fcm_token:
                return None
            
            # Create FCM message
            message = {
                "to": fcm_token,
                "notification": {
                    "title": f"🌊 {alert.level.upper()} Flood Alert",
                    "body": f"{station.name}: {alert.message[:100]}",
                },
                "data": {
                    "alert_id": str(alert.id),
                    "station_code": station.code,
                    "level": alert.level,
                },
            }
            
            # Send to FCM
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"key={self.fcm_server_key}",
                    "Content-Type": "application/json",
                }
                
                async with session.post(
                    "https://fcm.googleapis.com/fcm/send",
                    headers=headers,
                    json=message
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Log success
                        log = NotificationLog(
                            alert_id=alert.id,
                            user_id=user.id,
                            notification_type="push",
                            recipient=fcm_token[:20] + "...",
                            status="sent",
                            provider="firebase",
                            provider_message_id=result.get("message_id"),
                        )
                        db.add(log)
                        await db.commit()
                        
                        logger.info(f"Sent FCM push to user {user.email}")
                        return {"type": "push", "provider": "firebase"}
                    else:
                        error_text = await response.text()
                        raise Exception(f"FCM API error: {error_text}")
            
        except Exception as e:
            logger.error(f"Failed to send FCM push: {e}")
            
            # Log failure
            log = NotificationLog(
                alert_id=alert.id,
                user_id=user.id,
                notification_type="push",
                recipient="fcm_token",
                status="failed",
                error_message=str(e),
                provider="firebase",
            )
            db.add(log)
            await db.commit()
            
            return None

    async def _send_onesignal_notification(
        self,
        alert: Alert,
        station: Station,
        user: User,
        db: AsyncSession
    ) -> Optional[Dict[str, str]]:
        """Send OneSignal push notification."""
        try:
            push_tokens = user.push_tokens or {}
            player_id = push_tokens.get("onesignal")
            
            if not player_id:
                return None
            
            # Create OneSignal message
            message = {
                "app_id": self.onesignal_app_id,
                "include_player_ids": [player_id],
                "headings": {"en": f"🌊 {alert.level.upper()} Flood Alert"},
                "contents": {"en": f"{station.name}: {alert.message[:100]}"},
                "data": {
                    "alert_id": str(alert.id),
                    "station_code": station.code,
                    "level": alert.level,
                },
            }
            
            # Send to OneSignal
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Basic {self.onesignal_api_key}",
                    "Content-Type": "application/json",
                }
                
                async with session.post(
                    "https://onesignal.com/api/v1/notifications",
                    headers=headers,
                    json=message
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        
                        # Log success
                        log = NotificationLog(
                            alert_id=alert.id,
                            user_id=user.id,
                            notification_type="push",
                            recipient=player_id[:20] + "...",
                            status="sent",
                            provider="onesignal",
                            provider_message_id=result.get("id"),
                        )
                        db.add(log)
                        await db.commit()
                        
                        logger.info(f"Sent OneSignal push to user {user.email}")
                        return {"type": "push", "provider": "onesignal"}
                    else:
                        error_text = await response.text()
                        raise Exception(f"OneSignal API error: {error_text}")
            
        except Exception as e:
            logger.error(f"Failed to send OneSignal push: {e}")
            
            # Log failure
            log = NotificationLog(
                alert_id=alert.id,
                user_id=user.id,
                notification_type="push",
                recipient="onesignal_id",
                status="failed",
                error_message=str(e),
                provider="onesignal",
            )
            db.add(log)
            await db.commit()
            
            return None

    async def send_telegram_notification(
        self,
        chat_id: str,
        message: str
    ) -> bool:
        """Send Telegram notification."""
        if not self.telegram_bot_token:
            logger.warning("Telegram bot token not configured")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                }
                
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        logger.info(f"Sent Telegram message to chat {chat_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Telegram API error: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    async def send_discord_notification(
        self,
        webhook_url: str,
        message: str,
        level: str = "info"
    ) -> bool:
        """Send Discord webhook notification."""
        try:
            # Color based on alert level
            colors = {
                "info": 0x2196F3,      # Blue
                "warning": 0xFF9800,   # Orange
                "severe": 0xF44336,    # Red
                "extreme": 0x9C27B0,   # Purple
            }
            
            embed = {
                "embeds": [{
                    "title": f"🌊 {level.upper()} Flood Alert",
                    "description": message,
                    "color": colors.get(level, 0x2196F3),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=embed) as response:
                    if response.status == 204:
                        logger.info("Sent Discord notification")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Discord webhook error: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False

    async def send_slack_notification(
        self,
        webhook_url: str,
        message: str,
        level: str = "info"
    ) -> bool:
        """Send Slack webhook notification."""
        try:
            # Color based on alert level
            colors = {
                "info": "#2196F3",
                "warning": "#FF9800",
                "severe": "#F44336",
                "extreme": "#9C27B0",
            }
            
            payload = {
                "attachments": [{
                    "color": colors.get(level, "#2196F3"),
                    "text": message,
                    "footer": "FloodSight Alert System",
                    "ts": int(datetime.now(timezone.utc).timestamp()),
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Sent Slack notification")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Slack webhook error: {error_text}")
                        return False
        
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


# Global instance
notification_service = NotificationService()



