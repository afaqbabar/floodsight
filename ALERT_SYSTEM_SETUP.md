# 🚨 FloodSight Advanced Alert System Setup Guide

Complete guide for setting up the enhanced alert system with all 6 features.

## 📋 Table of Contents

1. [Overview](#overview)
2. [New Features](#new-features)
3. [Database Migration](#database-migration)
4. [Environment Configuration](#environment-configuration)
5. [Quick Start](#quick-start)
6. [Feature Guides](#feature-guides)
7. [API Reference](#api-reference)

---

## 🎯 Overview

The FloodSight alert system now includes:

- ✅ **Multi-Channel Notifications** (Email, SMS, Push, Telegram, Discord, Slack)
- ✅ **Alert Webhooks** with retry logic
- ✅ **Alert Acknowledgment** tracking
- ✅ **User Subscriptions** for personalized alerts
- ✅ **Custom Alert Rules** (station-specific thresholds, rate-of-rise, time windows)
- ✅ **Analytics Dashboard** for insights and reporting

---

## 🆕 New Features

### 1. Notification System
Send alerts via multiple channels:
- **Email** (SMTP-based: Gmail, SendGrid, Mailgun, etc.)
- **SMS** (Twilio)
- **Push Notifications** (Firebase, OneSignal)
- **Telegram Bot**
- **Discord Webhooks**
- **Slack Webhooks**

### 2. Alert Webhooks
- POST alerts to external systems
- Automatic retry with configurable delays
- Support for Slack, Discord, Telegram, Teams, and generic webhooks
- Delivery tracking and logging

### 3. Alert Acknowledgment
- Users can acknowledge/dismiss/resolve alerts
- Track who acknowledged and when
- Add notes to acknowledgments
- Reduce alert fatigue

### 4. User Subscriptions
- Users subscribe to specific stations
- Set minimum alert level per subscription
- Notification preferences per user
- Support for email, SMS, and push tokens

### 5. Custom Alert Rules
- **Threshold Rules**: Station-specific discharge thresholds
- **Rate of Rise**: Trigger on rapid discharge increases
- **Time Window**: Boost alert levels during critical hours (e.g., nighttime)
- **Multi-Station**: Correlate alerts across related stations

### 6. Alert Analytics
- Alert frequency and trends
- Station risk ranking
- Acknowledgment rates
- Notification delivery statistics
- Interactive dashboards

---

## 🗄️ Database Migration

### Option 1: Automatic Migration (Alembic)

```bash
cd /home/lenovo/scrimba/floodsight/backend

# Create migration
alembic revision --autogenerate -m "Add alert system tables"

# Apply migration
alembic upgrade head
```

### Option 2: Manual SQL Migration

Create the following tables manually:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(20),
    notification_preferences JSONB,
    push_tokens JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Subscriptions
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    station_id INTEGER REFERENCES stations(id) ON DELETE CASCADE,
    min_alert_level VARCHAR(20) DEFAULT 'warning',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert Rules
CREATE TABLE alert_rules (
    id SERIAL PRIMARY KEY,
    station_id INTEGER REFERENCES stations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_type VARCHAR(50) NOT NULL,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Webhooks
CREATE TABLE webhooks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) NOT NULL,
    webhook_type VARCHAR(50) DEFAULT 'generic',
    min_alert_level VARCHAR(20) DEFAULT 'warning',
    station_filter JSONB,
    headers JSONB,
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Webhook Deliveries
CREATE TABLE webhook_deliveries (
    id SERIAL PRIMARY KEY,
    webhook_id INTEGER REFERENCES webhooks(id) ON DELETE CASCADE,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    status_code INTEGER,
    response_body TEXT,
    error_message TEXT,
    attempt_number INTEGER DEFAULT 1,
    next_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Alert Acknowledgments
CREATE TABLE alert_acknowledgments (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT,
    action VARCHAR(50) DEFAULT 'acknowledged'
);

-- Notification Logs
CREATE TABLE notification_logs (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    notification_type VARCHAR(20) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    provider VARCHAR(50),
    provider_message_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_user_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_station ON user_subscriptions(station_id);
CREATE INDEX idx_alert_rules_station ON alert_rules(station_id);
CREATE INDEX idx_webhook_deliveries_webhook ON webhook_deliveries(webhook_id);
CREATE INDEX idx_webhook_deliveries_alert ON webhook_deliveries(alert_id);
CREATE INDEX idx_alert_acknowledgments_alert ON alert_acknowledgments(alert_id);
CREATE INDEX idx_notification_logs_alert ON notification_logs(alert_id);
```

---

## ⚙️ Environment Configuration

### Required Services Setup

#### 1. Email (SMTP)

**Gmail Setup:**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Generate at: https://myaccount.google.com/apppasswords
SMTP_FROM="FloodSight Alerts <your-email@gmail.com>"
```

**SendGrid Setup:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM="FloodSight <noreply@yourdomain.com>"
```

#### 2. SMS (Twilio)

1. Sign up at https://www.twilio.com
2. Get credentials from Console
3. Buy a phone number

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890
```

#### 3. Push Notifications (Firebase)

1. Go to Firebase Console
2. Project Settings > Cloud Messaging
3. Copy Server Key

```bash
FCM_SERVER_KEY=your-fcm-server-key
```

#### 4. Push Notifications (OneSignal)

1. Sign up at https://onesignal.com
2. Create new app
3. Get App ID and API Key

```bash
ONESIGNAL_APP_ID=your-app-id
ONESIGNAL_API_KEY=your-api-key
```

#### 5. Telegram Bot

1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Copy token

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 6. Discord Webhook

1. Server Settings > Integrations > Webhooks
2. Create webhook and copy URL

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

#### 7. Slack Webhook

1. Create Slack App at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook to workspace

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

---

## 🚀 Quick Start

### 1. Update Docker Compose

The `docker-compose.yml` already includes all environment variable placeholders.

Create a `.env` file in the backend directory:

```bash
cd /home/lenovo/scrimba/floodsight/backend
nano .env
```

Add your credentials (see Environment Configuration above).

### 2. Rebuild Containers

```bash
cd /home/lenovo/scrimba/floodsight/backend
docker compose down
docker compose build
docker compose up -d
```

### 3. Run Database Migration

```bash
docker compose exec api alembic upgrade head
```

### 4. Access Dashboards

- **Live Dashboard**: http://localhost:5173/dashboard-figma.html
- **Analytics**: http://localhost:5173/analytics-dashboard.html
- **Admin Panel**: http://localhost:5173/admin-dashboard.html

---

## 📚 Feature Guides

### Creating a User

```bash
curl -X POST http://localhost:8080/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+1234567890",
    "notification_preferences": {
      "email": true,
      "sms": true,
      "push": false,
      "min_level": "warning"
    }
  }'
```

### Creating a Subscription

```bash
curl -X POST http://localhost:8080/v1/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "station_id": 1,
    "min_alert_level": "warning"
  }'
```

### Creating a Webhook

```bash
curl -X POST http://localhost:8080/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Slack Production Alerts",
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "webhook_type": "slack",
    "min_alert_level": "severe",
    "station_filter": [1, 2, 3]
  }'
```

### Creating Custom Alert Rules

**Threshold Rule:**
```bash
curl -X POST http://localhost:8080/v1/alert-rules \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": 1,
    "name": "Rhine Custom Thresholds",
    "rule_type": "threshold",
    "priority": 200,
    "config": {
      "thresholds": {
        "info": 500,
        "warning": 800,
        "severe": 1200,
        "extreme": 1500
      }
    }
  }'
```

**Rate of Rise Rule:**
```bash
curl -X POST http://localhost:8080/v1/alert-rules \
  -H "Content-Type: application/json" \
  -d '{
    "station_id": 1,
    "name": "Rapid Rise Detection",
    "rule_type": "rate_of_rise",
    "priority": 150,
    "config": {
      "threshold_m3s_per_hour": 50,
      "min_hours": 6,
      "alert_level": "warning"
    }
  }'
```

**Time Window Rule:**
```bash
curl -X POST http://localhost:8080/v1/alert-rules \
  -H "Content-Type": "application/json" \
  -d '{
    "station_id": 1,
    "name": "Nighttime Priority",
    "rule_type": "time_window",
    "priority": 100,
    "config": {
      "start_hour": 22,
      "end_hour": 6,
      "level_boost": 1,
      "probability_boost": 0.1
    }
  }'
```

### Acknowledging an Alert

```bash
curl -X POST http://localhost:8080/v1/alert-acknowledgments \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": 72,
    "user_id": 1,
    "action": "acknowledged",
    "notes": "Monitoring situation, no immediate action needed"
  }'
```

---

## 📊 API Reference

### User Management

- `GET /v1/users` - List all users
- `GET /v1/users/{id}` - Get user details
- `POST /v1/users` - Create user
- `PATCH /v1/users/{id}` - Update user
- `DELETE /v1/users/{id}` - Delete user

### Subscriptions

- `GET /v1/users/{id}/subscriptions` - List user subscriptions
- `POST /v1/subscriptions` - Create subscription
- `PATCH /v1/subscriptions/{id}` - Update subscription
- `DELETE /v1/subscriptions/{id}` - Delete subscription

### Webhooks

- `GET /v1/webhooks` - List webhooks
- `GET /v1/webhooks/{id}` - Get webhook
- `POST /v1/webhooks` - Create webhook
- `PATCH /v1/webhooks/{id}` - Update webhook
- `DELETE /v1/webhooks/{id}` - Delete webhook
- `GET /v1/webhooks/{id}/deliveries` - List deliveries
- `POST /v1/webhooks/retry` - Retry failed deliveries

### Alert Rules

- `GET /v1/alert-rules` - List rules
- `GET /v1/alert-rules/{id}` - Get rule
- `POST /v1/alert-rules` - Create rule
- `PATCH /v1/alert-rules/{id}` - Update rule
- `DELETE /v1/alert-rules/{id}` - Delete rule

### Acknowledgments

- `GET /v1/alert-acknowledgments` - List acknowledgments
- `POST /v1/alert-acknowledgments` - Acknowledge alert

### Analytics

- `GET /v1/analytics/alerts?days=30` - Alert analytics
- `GET /v1/analytics/notifications?days=30` - Notification analytics
- `GET /v1/analytics/alerts/timeline?days=30` - Alert timeline
- `GET /v1/analytics/stations/risk-ranking?days=30` - Station risk ranking

---

## 🎨 Dashboard Access

### Analytics Dashboard
- URL: http://localhost:5173/analytics-dashboard.html
- Features:
  - Alert statistics
  - Notification performance
  - Alert timeline charts
  - Station risk ranking

### Admin Dashboard
- URL: http://localhost:5173/admin-dashboard.html
- Features:
  - User management
  - Subscription management
  - Webhook configuration
  - Alert rule management
  - Acknowledgment tracking

---

## 🔧 Troubleshooting

### Notifications Not Sending

1. Check environment variables are set correctly
2. Check logs: `docker compose logs api scheduler`
3. Verify notification service credentials
4. Test individual providers

### Webhooks Failing

1. Check webhook URL is accessible
2. Review delivery logs: `GET /v1/webhooks/{id}/deliveries`
3. Manually retry: `POST /v1/webhooks/retry`
4. Check webhook service is accepting requests

### Database Migration Issues

```bash
# Reset and rerun migration
docker compose exec api alembic downgrade base
docker compose exec api alembic upgrade head
```

---

## 📝 Next Steps

1. **Configure Notifications**: Set up at least one notification channel
2. **Create Users**: Add users who should receive alerts
3. **Set Up Subscriptions**: Subscribe users to relevant stations
4. **Add Webhooks**: Connect to Slack/Discord/Teams
5. **Create Custom Rules**: Fine-tune alerting for specific stations
6. **Monitor Analytics**: Use dashboards to track system performance

---

## 🆘 Support

For issues or questions:
- Check logs: `docker compose logs -f api scheduler`
- Review API docs: http://localhost:8080/docs
- Check database: `docker compose exec db psql -U postgres -d floodsight`

---

**System Status**: ✅ All 6 Features Implemented & Ready

Enjoy your comprehensive flood alert system! 🌊



