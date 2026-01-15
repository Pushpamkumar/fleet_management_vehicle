# 🌐 Deployment Guide - Host Your Fleet Management API Online

This guide shows you how to deploy your Fleet Management API to make it accessible to others online.

---

## 🚀 Option 1: Railway.app (Easiest - FREE TIER)

**Railway** is the easiest option with free tier and automatic deployments.

### Step 1: Prepare Your Project
```bash
# Make sure you have these files:
# - requirements.txt (already exists)
# - Procfile (create below)
# - .env (for production config)
# - runtime.txt (Python version)
```

### Step 2: Create `Procfile` in project root
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Create `runtime.txt` in project root
```
python-3.9.12
```

### Step 4: Deploy to Railway

1. Go to **https://railway.app**
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Connect your GitHub repo
5. Railway auto-deploys on push
6. Your URL: `https://your-app-name.railway.app`

### Step 5: Set Environment Variables on Railway
In Railway dashboard:
- `DATABASE_URL`: Your PostgreSQL URI (Railway provides free PostgreSQL)
- `SECRET_KEY`: Generate random key: `openssl rand -hex 32`
- `CORS_ORIGINS`: Add your frontend URL

---

## 🚀 Option 2: Render.com (Simple & Free)

### Step 1: Prepare `requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
PyJWT==2.8.1
python-dotenv==1.0.0
email-validator==2.1.0
redis==5.0.1
```

### Step 2: Deploy to Render

1. Go to **https://render.com**
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Fill in details:
   - **Name**: fleet-management-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

5. Add Environment Variables:
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=your-generated-key
   CORS_ORIGINS=*
   ```

6. Deploy!

---

## 🚀 Option 3: Heroku (Paid, but simple)

### Step 1: Install Heroku CLI
```bash
# Windows: Download installer from https://devcenter.heroku.com/articles/heroku-cli

# Or with npm:
npm install -g heroku
```

### Step 2: Login
```bash
heroku login
```

### Step 3: Create Heroku App
```bash
heroku create your-fleet-app
```

### Step 4: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:mini
```

### Step 5: Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-generated-key"
heroku config:set ALGORITHM="HS256"
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES="30"
```

### Step 6: Deploy
```bash
git push heroku main
```

### Step 7: Check Logs
```bash
heroku logs --tail
```

Your app will be at: `https://your-fleet-app.herokuapp.com`

---

## 🚀 Option 4: Docker + AWS/Google Cloud/Azure

### Step 1: Build Docker Image
```bash
docker build -t fleet-management-api .
```

### Step 2: Run Locally to Test
```bash
docker run -p 8000:8000 fleet-management-api
```

### Step 3: Push to Docker Hub
```bash
# Login to Docker Hub
docker login

# Tag image
docker tag fleet-management-api yourusername/fleet-management-api:latest

# Push
docker push yourusername/fleet-management-api:latest
```

### Step 4: Deploy to AWS/GCP/Azure
- **AWS**: Use ECS or App Runner
- **Google Cloud**: Use Cloud Run
- **Azure**: Use Container Instances or App Service

---

## 📋 Pre-Deployment Checklist

- [ ] Update `.env` for production:
  ```
  DATABASE_URL=postgresql://user:pass@host:5432/fleet_management
  SECRET_KEY=<generate-random-32-char-key>
  CORS_ORIGINS=https://yourdomain.com
  RELOAD=False
  LOG_LEVEL=INFO
  ```

- [ ] Generate secure SECRET_KEY:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] Set up PostgreSQL database
  - Production: Don't use SQLite
  - Use managed PostgreSQL from Railway, Render, or AWS RDS

- [ ] Test all endpoints locally
  - Run `curl http://localhost:8000/health`

- [ ] Update README with your deployed URL

---

## 🔗 Share Your Live API

Once deployed, share the link:

```
📌 Live API: https://your-app-name.railway.app
📖 API Docs: https://your-app-name.railway.app/api/docs
🔍 ReDoc: https://your-app-name.railway.app/api/redoc
📊 Health: https://your-app-name.railway.app/health
```

### Example Response from Live API:
```bash
curl https://your-app-name.railway.app/health

# Response:
{
  "status": "healthy",
  "service": "Fleet Management API",
  "version": "1.0.0"
}
```

---

## 🚨 Common Issues & Solutions

### ❌ "ModuleNotFoundError: No module named..."
**Solution**: Make sure `requirements.txt` has all dependencies
```bash
pip freeze > requirements.txt
```

### ❌ "DATABASE_URL environment variable not set"
**Solution**: Set it in your hosting platform's environment variables
```bash
DATABASE_URL=postgresql://user:pass@host/dbname
```

### ❌ "Port already in use"
**Solution**: Change port or kill process using port 8000
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### ❌ "CORS errors from frontend"
**Solution**: Update CORS_ORIGINS in .env
```
CORS_ORIGINS=https://yourdomain.com,http://localhost:3000
```

---

## 📊 Monitoring Your Live API

### Check Health Status
```bash
curl https://your-deployed-url/health
```

### View API Docs Live
```
https://your-deployed-url/api/docs
```

### Monitor Logs
- **Railway**: Dashboard → Deployments → Logs
- **Render**: Dashboard → Logs
- **Heroku**: `heroku logs --tail`

---

## 💰 Estimated Costs

| Platform | Cost | Bandwidth | Database |
|----------|------|-----------|----------|
| Railway | $5/month | $0.10/GB out | Free tier |
| Render | Free tier (limited) | Unlimited | Free tier |
| Heroku | $7/month | Unlimited | $9/month |
| AWS | Pay-as-you-go | $0.12/GB out | $15+/month |

**Recommendation**: Start with **Railway.app** (easiest, good free tier)

---

## ✅ After Deployment

1. **Test all endpoints** at your live URL
2. **Share API URL** with team
3. **Monitor performance** and logs
4. **Update frontend** to use live API URL
5. **Set up SSL certificate** (most platforms auto-enable)

---

## 🎉 Success!

Once deployed, your Fleet Management API is live and accessible globally!

**Share with others:**
- 📱 Send them the API docs link
- 🔐 They can register and get a JWT token
- 📅 They can book vehicles
- 📊 They can view analytics

---

**Need Help?**
- Railway Support: https://railway.app/support
- Render Support: https://render.com/support
- FastAPI Docs: https://fastapi.tiangolo.com
