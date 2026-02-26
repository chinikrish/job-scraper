# 🚀 Job Scraper & Government Schemes Tool

## 📋 Features
- Scrapes government job openings
- Scrapes private sector jobs
- Tracks government schemes and welfare programs
- Monitors exam notifications and deadlines
- Posts automatically to WhatsApp status
- Runs twice daily (9 AM and 6 PM)

## 🚀 Deploy to Railway

### One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/job-scraper)

### Manual Deploy
1. **Clone/Download** this repository
2. **Create a Railway account** at [railway.app](https://railway.app)
3. **Create New Project** → **Deploy from GitHub**
4. **Add Environment Variables**:
   - `MORNING_POST_TIME`: 09:00
   - `EVENING_POST_TIME`: 18:00
5. **Add PostgreSQL** (optional)
6. **Add Volume** mounted at `/tmp/whatsapp-session`

## 📱 WhatsApp Setup

1. After first deploy, you need to authenticate WhatsApp:
   ```bash
   railway run /bin/bash
   python main.py --first-run