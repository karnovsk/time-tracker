# מעקב זמן פנאי (Time Tracker)

אפליקציית ווב מלאה למעקב אחר פעילויות פנאי יומיות עם אימות משתמשים, ניתוח סטטיסטי ותצוגת גרפים.

## תכונות

### אימות
- 🔐 התחברות באמצעות OTP (קוד חד-פעמי) באימייל
- 🔄 התחברות אוטומטית (פרסיסטנטית)
- 🛡️ הפרדה מלאה בין משתמשים

### רישום יומי
- 📝 רישום יומי של שעות פנאי בשלוש קטגוריות:
  - **פנאי מזדמן**: טלוויזיה, רשתות חברתיות, וכו'
  - **פנאי רציני**: ספורט, לימוד, תרגול, וכו'
  - **פנאי פרויקט**: פרויקטים אישיים, יזמות, וכו'
- 📋 שדה טקסט לתיאור פעילויות לכל קטגוריה
- 🚫 רישום אחד ליום בלבד (לא ניתן לעריכה)
- 🕐 תמיכה ברישומים רטרואקטיביים (הזנת רישומים עבור ימים קודמים)
- ✅ ולידציה: סה"כ שעות > 0 ו- ≤ 24

### סטטיסטיקות ודוחות
- 📊 סטטיסטיקות מפורטות לפי קטגוריה:
  - סה"כ שעות
  - ממוצע שעות
  - מספר רישומים
- 📈 גרפים אינטראקטיביים:
  - תרשים עוגה
  - תרשים עמודות
- 📤 שיתוף סטטיסטיקות:
  - ייצוא כתמונה (PNG)
  - שיתוף באמצעות Web Share API (מובייל)
- 📜 טבלת היסטוריה מפורטת:
  - תאריך
  - שעות ופעילויות לכל קטגוריה
  - סה"כ שעות
  - פגינציה (10 רישומים לעמוד)
- 🗑️ איפוס נתונים (עם אישור כפול)

### ממשק משתמש
- 🎨 עיצוב מודרני ורספונסיבי
- 🇮🇱 תמיכה מלאה בעברית (RTL)
- 📱 מותאם למובייל
- 🌈 צבעים אטרקטיביים וגרדיאנטים
- ⚡ חווית משתמש חלקה עם אנימציות

## ארכיטקטורה

### Backend
- **FastAPI** - מסגרת API מודרנית ומהירה
- **PostgreSQL** - בסיס נתונים יחסי
- **SQLAlchemy 2.0** - ORM אסינכרוני
- **Supabase Auth** - שירות אימות מנוהל
- **Alembic** - ניהול מיגרציות
- **Docker** - קונטיינריזציה של PostgreSQL

### Frontend
- **Vanilla JavaScript** - ללא תלויות כבדות
- **Chart.js** - ויזואליזציה של נתונים
- **html2canvas** - ייצוא סטטיסטיקות כתמונה
- **CSS3** - עיצוב מודרני עם גרדיאנטים ואנימציות
- **HTML5** - סמנטי ונגיש

### Database Schema
```sql
users (
    id UUID PRIMARY KEY,
    supabase_user_id UUID UNIQUE,
    email VARCHAR(255) UNIQUE,
    last_entry_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

daily_entries (
    id UUID PRIMARY KEY,
    user_id UUID FOREIGN KEY,
    entry_date DATE,
    casual_leisure_hours FLOAT,
    casual_leisure_note TEXT,
    serious_leisure_hours FLOAT,
    serious_leisure_note TEXT,
    project_leisure_hours FLOAT,
    project_leisure_note TEXT,
    total_hours FLOAT (COMPUTED),
    created_at TIMESTAMP,
    UNIQUE(user_id, entry_date)
)
```

## התקנה והפעלה

### דרישות מקדימות
- Python 3.11 or 3.12
- Docker Desktop (for PostgreSQL)
- Supabase account (free tier works)

### 1. הגדרת Supabase
1. גש ל-https://app.supabase.com
2. צור פרויקט חדש
3. עבור אל **Authentication** → **Providers**
4. הפעל **Email OTP**
5. שמור את:
   - SUPABASE_URL
   - SUPABASE_ANON_KEY
   - SUPABASE_SERVICE_KEY

### 2. הגדרת Backend

```bash
# 1. התקן תלויות
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
# או: venv\Scripts\activate  # Windows CMD/PowerShell
pip install -r requirements.txt

# 2. צור קובץ .env
cp .env.example .env
# ערוך .env והוסף את פרטי Supabase שלך

# 3. הפעל PostgreSQL
cd ..
docker compose up -d

# 4. צור טבלאות בבסיס הנתונים
cd backend
python create_tables.py

# 5. הפעל את ה-API
uvicorn app.main:app --reload
```

Backend יהיה זמין ב: **http://localhost:8000**

API Docs: **http://localhost:8000/docs**

### 3. הגדרת Frontend

```bash
# בחלון טרמינל נפרד
cd frontend
python serve.py
```

Frontend יהיה זמין ב: **http://localhost:8080**

### 4. בדיקה

1. פתח **http://localhost:8080** בדפדפן
2. הזן את כתובת האימייל שלך
3. בדוק את האימייל לקוד OTP
4. הזן את הקוד והתחבר
5. הזן רישום יומי
6. לחץ "הצג סטטיסטיקה" לראות ניתוחים

## API Endpoints

### Authentication
- `POST /api/v1/auth/send-otp` - שלח קוד OTP לאימייל
- `POST /api/v1/auth/verify-otp` - אמת OTP וקבל טוקן
- `GET /api/v1/auth/me` - קבל פרטי משתמש נוכחי

### Daily Entries
- `GET /api/v1/entries/can-submit` - בדוק אם ניתן לשלוח רישום היום
- `POST /api/v1/entries/today` - שלח רישום להיום או לתאריך מסוים (רטרואקטיבי)
- `GET /api/v1/entries/today` - קבל רישום של היום
- `GET /api/v1/entries/history` - קבל היסטוריית רישומים (עם פגינציה)

### Statistics
- `GET /api/v1/statistics/overview` - קבל סטטיסטיקות כלליות
- `GET /api/v1/statistics/trends` - קבל נתוני טרנדים לגרפים
- `DELETE /api/v1/statistics/reset` - מחק את כל הנתונים של המשתמש

## מבנה הפרויקט

```
time-tracker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py           # נקודות קצה לאימות
│   │   │   ├── entries.py        # נקודות קצה לרישומים
│   │   │   └── statistics.py    # נקודות קצה לסטטיסטיקות
│   │   ├── models/
│   │   │   ├── user.py           # מודל משתמש
│   │   │   └── daily_entry.py   # מודל רישום יומי
│   │   ├── schemas/
│   │   │   ├── auth.py           # סכמות Pydantic לאימות
│   │   │   ├── entry.py          # סכמות Pydantic לרישומים
│   │   │   └── statistics.py    # סכמות Pydantic לסטטיסטיקות
│   │   ├── services/
│   │   │   └── auth_service.py  # שירות אימות Supabase
│   │   ├── config.py             # הגדרות אפליקציה
│   │   ├── database.py           # הגדרת בסיס נתונים
│   │   ├── dependencies.py       # תלויות FastAPI
│   │   └── main.py               # נקודת כניסה לאפליקציה
│   ├── alembic/                  # מיגרציות בסיס נתונים
│   ├── requirements.txt          # תלויות Python
│   ├── .env.example              # תבנית משתני סביבה
│   └── create_tables.py          # סקריפט ליצירת טבלאות
├── frontend/
│   ├── index.html                # HTML ראשי
│   ├── styles.css                # עיצוב
│   ├── app.js                    # לוגיקת אפליקציה
│   └── serve.py                  # שרת HTTP פשוט
├── docker-compose.yml            # הגדרות PostgreSQL
└── README.md                     # מסמך זה
```

## פיצ'רים מתקדמים

### Security
- Bearer token authentication
- Password-less authentication (OTP)
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)

### Performance
- Async/await throughout the stack
- Connection pooling
- Indexed database queries
- Efficient pagination

### User Experience
- Auto-login with localStorage
- Real-time form validation
- Loading states
- Error handling
- Responsive design
- Hebrew RTL support

## Development

### Running Tests
```bash
cd backend
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Check Database
```bash
cd backend
python check_db.py
```

## Deployment

### Pre-Deployment Checklist

Before deploying to production, ensure:

- [ ] All environment variables configured in production
- [ ] PostgreSQL database provisioned (managed service recommended)
- [ ] Supabase project configured with production domain
- [ ] CORS origins updated for production domain
- [ ] DEBUG=False in production environment
- [ ] HTTPS enabled (required for Supabase)
- [ ] Security review completed
- [ ] Testing completed (authentication, entries, statistics)

### Deployment Options

**Quick Comparison:**
- **Option 1 (Railway)**: Fast, no cold starts - **~$5-10/month**
- **Option 2 (Render + Supabase)**: Free with cold starts - **$0/month** ✨ **Recommended for personal use**
- **Option 3 (Vercel + Supabase)**: Serverless backend - **Free tier available**
- **Option 4 (Docker + VPS)**: Full control - **$5-20/month**

---

#### Option 1: Railway (Best Performance - Paid)

**Backend + Database:**
1. Push code to GitHub repository
2. Go to [railway.app](https://railway.app)
3. Create new project → Deploy from GitHub
4. Select your repository
5. Railway will auto-detect Python and create a PostgreSQL database
6. Add environment variables in Railway dashboard:
   ```
   DATABASE_URL (auto-generated)
   SUPABASE_URL
   SUPABASE_ANON_KEY
   SUPABASE_SERVICE_KEY
   ENVIRONMENT=production
   DEBUG=False
   CORS_ORIGINS=https://your-frontend-domain.com
   ```
7. Deploy command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Frontend:**
- Deploy to Vercel, Netlify, or Cloudflare Pages (see below)
- Update `API_URL` in `frontend/app.js` to your Railway backend URL

#### Option 2: Render + Supabase (100% Free - Recommended)

**Perfect for personal use with zero monthly cost!**

This option uses:
- **Render** for backend (free tier with cold starts) and frontend (free, no cold starts)
- **Supabase** for database (free 500MB, you already have this!)
- **Total cost: $0/month**

**Trade-offs:**
- ⚠️ Backend cold starts after 15 minutes of inactivity (30-60s first load)
- ✅ Frontend loads instantly (no cold starts)
- ✅ Database free forever (500MB is plenty for this app)

---

### Step 1: Set Up Supabase Database

Your Supabase project is already configured for Auth. Now add the application tables:

1. **Go to Supabase Dashboard** → Your project → SQL Editor

2. **Run this SQL** to create the tables:

```sql
-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_user_id UUID UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_entry_date DATE
);

-- Create daily_entries table
CREATE TABLE daily_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    casual_leisure_hours FLOAT NOT NULL CHECK (casual_leisure_hours >= 0),
    casual_leisure_note TEXT,
    serious_leisure_hours FLOAT NOT NULL CHECK (serious_leisure_hours >= 0),
    serious_leisure_note TEXT,
    project_leisure_hours FLOAT NOT NULL CHECK (project_leisure_hours >= 0),
    project_leisure_note TEXT,
    total_hours FLOAT GENERATED ALWAYS AS (
        casual_leisure_hours + serious_leisure_hours + project_leisure_hours
    ) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_date UNIQUE(user_id, entry_date)
);

-- Create indexes for better performance
CREATE INDEX idx_users_supabase_id ON users(supabase_user_id);
CREATE INDEX idx_entries_user_date ON daily_entries(user_id, entry_date DESC);
```

3. **Get your database connection string**:
   - Supabase Dashboard → Project Settings → Database
   - Connection String → Transaction mode
   - Copy the string (looks like: `postgresql://postgres.[PROJECT]:[PASSWORD]@...`)
   - **Important**: Change `postgresql://` to `postgresql+asyncpg://` for SQLAlchemy
   - Example: `postgresql+asyncpg://postgres.abc123:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

---

### Step 2: Deploy Backend to Render

1. **Push your code to GitHub** (if not already done)

2. **Go to [render.com](https://render.com)** and sign up (free account)

3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Repository settings:
     - **Name**: `time-tracker-backend`
     - **Root Directory**: `backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Instance Type**: Free

4. **Add Environment Variables** (before deploying):

   Click "Advanced" → Add Environment Variables:

   ```
   DATABASE_URL = postgresql+asyncpg://postgres.[YOUR-PROJECT]:[PASSWORD]@...
   SUPABASE_URL = https://your-project.supabase.co
   SUPABASE_ANON_KEY = your-anon-key-here
   SUPABASE_SERVICE_KEY = your-service-key-here
   ENVIRONMENT = production
   DEBUG = False
   CORS_ORIGINS = (will update after frontend deployment)
   ```

5. **Click "Create Web Service"** - Render will build and deploy (takes 2-3 minutes)

6. **Copy your backend URL**: Will be something like `https://time-tracker-backend.onrender.com`

---

### Step 3: Deploy Frontend to Render

1. **Update API URL** in your local code:

   Edit `frontend/app.js` line 2:
   ```javascript
   const API_URL = 'https://time-tracker-backend.onrender.com/api/v1';
   ```

2. **Commit and push** this change to GitHub:
   ```bash
   git add frontend/app.js
   git commit -m "Update API URL for production"
   git push
   ```

3. **Create Static Site on Render**:
   - Dashboard → New + → Static Site
   - Connect your GitHub repository
   - Settings:
     - **Name**: `time-tracker-frontend`
     - **Root Directory**: Leave empty
     - **Build Command**: Leave empty (no build needed)
     - **Publish Directory**: `frontend`

4. **Click "Create Static Site"** - Deploys in ~30 seconds

5. **Copy your frontend URL**: Will be something like `https://time-tracker-frontend.onrender.com`

---

### Step 4: Update Backend CORS

1. **Go back to your backend Web Service** on Render

2. **Environment** → Edit `CORS_ORIGINS`:
   ```
   CORS_ORIGINS = https://time-tracker-frontend.onrender.com
   ```

3. **Save** - Render will automatically redeploy the backend

---

### Step 5: Configure Supabase Auth

1. **Supabase Dashboard** → Authentication → URL Configuration

2. **Update URLs**:
   - **Site URL**: `https://time-tracker-frontend.onrender.com`
   - **Redirect URLs**: Add `https://time-tracker-frontend.onrender.com/**`

3. **Authentication → Settings** → Scroll down:
   - Ensure "Enable email confirmations" is OFF (for OTP to work)

---

### Step 6: Test Your Deployment

1. Visit your frontend URL: `https://time-tracker-frontend.onrender.com`
2. Enter your email → Receive OTP
3. Login → Submit an entry
4. View statistics → Share statistics
5. Success! 🎉

**Note on Cold Starts**: First request after 15 minutes of inactivity will take 30-60 seconds as the backend wakes up. Subsequent requests are instant.

---

### Optional: Keep Backend Awake (Free Method)

Use a free uptime monitor to ping your backend every 14 minutes:

1. **Sign up at [UptimeRobot](https://uptimerobot.com)** (free)
2. **Add New Monitor**:
   - Type: HTTP(s)
   - URL: `https://time-tracker-backend.onrender.com/docs`
   - Interval: 14 minutes
3. This keeps your backend awake = no cold starts!

---

**Total Monthly Cost: $0** ✨

#### Option 3: Vercel (Frontend) + Supabase (Backend Alternative)

If you want to leverage Supabase fully:

1. **Database**: Use Supabase's built-in PostgreSQL
   - Go to Supabase project → Database
   - Run SQL to create tables (from `backend/app/models/`)

2. **Backend**: Deploy FastAPI to Vercel as a Serverless Function
   - Create `api/index.py` with Vercel adapter
   - Or deploy backend separately (Railway/Render)

3. **Frontend**: Deploy to Vercel
   - `cd frontend`
   - `vercel deploy`
   - Update `API_URL` in `app.js`

#### Option 4: Docker + VPS (DigitalOcean, Linode, AWS EC2)

**For advanced users who want full control:**

1. **Create Dockerfile for backend:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Update docker-compose.yml for production:**
```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/timetracker
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=timetracker
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=securepassword
    volumes:
      - postgres_data:/var/lib/postgresql/data

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html

volumes:
  postgres_data:
```

3. **Deploy:**
```bash
# On VPS
docker-compose up -d
```

4. **Set up Nginx reverse proxy** for HTTPS (with Let's Encrypt)

### Frontend Deployment Details

**Update API URL for Production:**

In `frontend/app.js`, change:
```javascript
const API_URL = 'http://localhost:8000/api/v1';
```

To:
```javascript
const API_URL = 'https://your-backend-domain.com/api/v1';
```

**Deploy to Vercel:**
```bash
cd frontend
npm init -y  # If no package.json
vercel deploy --prod
```

**Deploy to Netlify:**
```bash
cd frontend
netlify deploy --prod --dir .
```

**Deploy to Cloudflare Pages:**
1. Go to Cloudflare Pages dashboard
2. Connect GitHub repository
3. Build settings:
   - Build command: (none - static files)
   - Build output directory: `frontend`
4. Deploy

### Post-Deployment

1. **Test the full flow:**
   - Login with OTP
   - Submit entry
   - View statistics
   - Share statistics
   - Reset data

2. **Update Supabase settings:**
   - Go to Authentication → URL Configuration
   - Add your production domain to allowed redirect URLs
   - Add production domain to CORS allowed origins

3. **Monitor:**
   - Set up error tracking (Sentry, LogRocket)
   - Monitor database performance
   - Set up uptime monitoring (UptimeRobot, Pingdom)

4. **Backup:**
   - Enable automated database backups
   - Railway/Render: Built-in backups
   - Self-hosted: Set up `pg_dump` cronjob

### Environment Variables Reference

**Required for Production:**
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJxxx...
SUPABASE_SERVICE_KEY=eyJxxx...

# FastAPI
ENVIRONMENT=production
DEBUG=False

# CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Server (auto-set by most platforms)
HOST=0.0.0.0
PORT=8000
```

### Security Checklist for Production

- [ ] Use HTTPS everywhere (frontend + backend)
- [ ] Update CORS origins to only your frontend domain
- [ ] Enable rate limiting (consider adding slowapi middleware)
- [ ] Review Supabase security rules
- [ ] Set up database connection pooling limits
- [ ] Enable database SSL connection
- [ ] Keep dependencies updated (`pip list --outdated`)
- [ ] Set up logging and monitoring
- [ ] Configure Supabase email templates (branding)

## Troubleshooting

### Backend Issues
- **Port 8000 in use**: Kill the process or use `uvicorn app.main:app --port 8001`
- **Database connection error**: Make sure Docker is running (`docker ps`)
- **Timezone error**: Already fixed in config (see docker-compose.yml and database.py)
- **Missing email-validator**: `pip install email-validator`

### Frontend Issues
- **CORS errors**: Make sure backend is running with correct CORS settings
- **API URL wrong**: Check `API_URL` in app.js (should be `http://localhost:8000/api/v1`)
- **Token expired**: Logout and login again

### Supabase Issues
- **Not receiving OTP**: Check spam folder, verify email provider settings in Supabase
- **Magic link instead of OTP**: Enable "Email OTP" in Supabase Auth settings

## Future Enhancements

Possible future features:
- [ ] Export data to CSV/JSON
- [ ] Weekly/monthly email reports
- [ ] Goals and achievements
- [ ] Data visualization improvements (line charts, trends)
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Social features (compare with friends)

## License

This project is open source and available under the MIT License.

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Supabase](https://supabase.com/)
- [Chart.js](https://www.chartjs.org/)
- [html2canvas](https://html2canvas.hertzen.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/)

---

**Enjoy tracking your leisure time! 🎉**
