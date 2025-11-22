# 🚀 FloodSight Quick Start Guide

## ✅ Setup Complete!

Your FloodSight alert system is now fully deployed with all 6 advanced features.

---

## 📊 Access Your Dashboards

### 1. **Live Dashboard** (Main)
**URL**: http://localhost:5173/dashboard-figma.html

Features:
- Real-time flood monitoring
- Interactive map with station markers
- Forecast visualization
- Alert indicators

### 2. **Analytics Dashboard** (NEW! 📊)
**URL**: http://localhost:5173/analytics-dashboard.html

Features:
- Alert statistics & trends
- Notification performance metrics
- Station risk ranking
- Interactive charts
- Configurable time periods (7, 30, 90, 365 days)

### 3. **Admin Dashboard** (NEW! ⚙️)
**URL**: http://localhost:5173/admin-dashboard.html

Features:
- User management (create, view, delete)
- Subscription management
- Webhook configuration
- Alert rule management
- Acknowledgment tracking

---

## 🔧 Quick Actions

### Test the API
```bash
# Health check
curl http://localhost:8080/v1/health

# View current alerts
curl http://localhost:8080/v1/alerts?active_only=true | jq

# Trigger alert computation
curl -X POST http://localhost:8080/v1/alerts/compute
```

### Create Your First User
```bash
curl -X POST http://localhost:8080/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@floodsight.com",
    "name": "Admin User",
    "phone": "+1234567890"
  }'
```

### Add a Subscription
```bash
curl -X POST http://localhost:8080/v1/subscriptions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "station_id": 1,
    "min_alert_level": "warning"
  }'
```

### Create a Webhook (Slack Example)
```bash
curl -X POST http://localhost:8080/v1/webhooks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Slack Alerts",
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "webhook_type": "slack",
    "min_alert_level": "severe"
  }'
```

---

## 🔔 Enable Notifications (Optional)

To enable email/SMS/push notifications, configure environment variables in `backend/.env`:

### Minimal Setup (Email Only)
```bash
# Gmail with app password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM="FloodSight <your-email@gmail.com>"
```

**Get Gmail App Password**: https://myaccount.google.com/apppasswords

### Full Configuration
See `ALERT_SYSTEM_SETUP.md` for:
- SMS (Twilio)
- Push notifications (Firebase, OneSignal)
- Telegram bot
- Discord/Slack webhooks

After updating `.env`:
```bash
cd backend
docker compose restart api scheduler
```

---

## 📚 Documentation

- **Complete Setup Guide**: `ALERT_SYSTEM_SETUP.md`
- **Feature Summary**: `ALERT_SYSTEM_COMPLETE.md`
- **API Documentation**: http://localhost:8080/docs

---

## 🎯 What's Working

✅ Real-time flood monitoring (GloFAS data)  
✅ Alert computation with custom rules  
✅ Multi-channel notifications (6 types)  
✅ Alert webhooks with retry logic  
✅ User subscription management  
✅ Alert acknowledgment tracking  
✅ Analytics dashboard  
✅ Admin configuration panel  
✅ Interactive dashboards

---

## 🚨 Current Alerts

Check active alerts:
```bash
curl -s http://localhost:8080/v1/alerts?active_only=true | jq '.[] | {level, station_code, probability}'
```

---

## 🔄 System Management

### View Logs
```bash
cd backend
docker compose logs -f api scheduler
```

### Restart Services
```bash
cd backend
docker compose restart api scheduler
```

### Check Database
```bash
docker compose exec db psql -U postgres -d floodsight -c "SELECT COUNT(*) as total_forecasts FROM forecasts;"
docker compose exec db psql -U postgres -d floodsight -c "SELECT level, COUNT(*) FROM alerts WHERE is_active = true GROUP BY level;"
```

### Monitor System
```bash
./backend/monitor.sh
```

---

## 🆘 Troubleshooting

### API Not Responding
```bash
# Wait 30 seconds after rebuild
sleep 30
curl http://localhost:8080/v1/health

# Check logs
docker compose logs api
```

### No Notifications Sending
1. Check environment variables are set
2. Verify SMTP/Twilio credentials
3. Check notification logs:
```bash
docker compose exec db psql -U postgres -d floodsight -c "SELECT * FROM notification_logs ORDER BY created_at DESC LIMIT 10;"
```

### Database Migration Needed
```bash
cd backend
docker compose exec api alembic upgrade head
```

---

## 🎉 Next Steps

1. ✅ Explore the dashboards
2. ⏳ Configure notifications (optional)
3. ⏳ Create users and subscriptions
4. ⏳ Set up webhooks for your team
5. ⏳ Create custom alert rules
6. ⏳ Monitor analytics

---

## 📞 Support

- API Documentation: http://localhost:8080/docs
- Setup Guide: `ALERT_SYSTEM_SETUP.md`
- Feature Summary: `ALERT_SYSTEM_COMPLETE.md`

---

**Status**: ✅ **FULLY OPERATIONAL**

All 6 advanced alert features are ready to use!  
Navigate between dashboards using the top navigation menu.

🌊 **Happy Flood Monitoring!**



