# QUICK REFERENCE CARD - KeyForAgents AI Platform

## 🚀 72-HOUR LAUNCH TIMELINE

### DAY 1 (Hours 0-24): Foundation
- ✅ Repository initialized
- ✅ Domain ready: keyforagents.com
- ✅ DNS configured
- ✅ Supabase project created
- [ ] Database schema deployed
- [ ] Environment variables configured
- [ ] Backend API structure created

### DAY 2 (Hours 24-48): Build & Integration
- [ ] Frontend components built
- [ ] API endpoints implemented
- [ ] Lead capture form tested
- [ ] Email integration configured
- [ ] Payment gateway tested

### DAY 3 (Hours 48-72): Deploy & Launch
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway
- [ ] DNS records pointed
- [ ] SSL certificates verified
- [ ] Production testing complete
- [ ] LIVE! 🎉

---

## 📊 TECH STACK

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **Hosting**: Vercel
- **Domain**: keyforagents.com

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Hosting**: Railway
- **Auth**: Supabase Auth

### Integrations
- **Payments**: Stripe
- **Email**: SendGrid / Resend
- **Analytics**: Vercel Analytics

---

## 🗄️ DATABASE SCHEMA

### lead_capture table
```sql
CREATE TABLE lead_capture (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(255),
  company VARCHAR(255),
  use_case TEXT,
  source VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  status VARCHAR(50) DEFAULT 'new'
);
```

---

## 🔑 ENVIRONMENT VARIABLES

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=your_stripe_key
```

### Backend (.env)
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_service_role_key
STRIPE_SECRET_KEY=your_stripe_secret
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=hello@keyforagents.com
```

---

## 🛠️ LOCAL DEVELOPMENT

### Start Frontend
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

### Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Runs on http://localhost:8000
```

---

## 📡 API ENDPOINTS

### Core Endpoints
- `POST /api/v1/leads` - Capture new lead
- `GET /api/v1/leads/{id}` - Get lead by ID
- `POST /api/v1/checkout` - Create Stripe checkout
- `POST /api/v1/webhook/stripe` - Stripe webhooks
- `GET /api/v1/health` - Health check

---

## 🚢 DEPLOYMENT COMMANDS

### Deploy Frontend (Vercel)
```bash
vercel --prod
```

### Deploy Backend (Railway)
```bash
railway up
```

### Update DNS
```
A Record: @ → Vercel IP
CNAME: www → cname.vercel-dns.com
A Record: api → Railway IP
```

---

## ✅ PRE-LAUNCH CHECKLIST

### Technical
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] SSL certificates active
- [ ] API health checks passing
- [ ] Forms submitting correctly
- [ ] Email sending working
- [ ] Payment flow tested

### Content
- [ ] Landing page copy finalized
- [ ] CTA buttons clear
- [ ] Social proof added
- [ ] Privacy policy linked
- [ ] Terms of service linked

### Analytics
- [ ] Google Analytics installed
- [ ] Conversion tracking setup
- [ ] Error monitoring active

---

## 📞 QUICK CONTACTS

- **Supabase Project**: svsrkwopqwgtfcmyqnho
- **Domain Registrar**: [Check DNS records]
- **GitHub Repo**: Keyforagents/keyforagents-ai-platform

---

## 🎯 REVENUE MODEL

### Pricing Tiers
1. **Starter**: $97/mo - 1 AI agent
2. **Professional**: $297/mo - 5 AI agents
3. **Enterprise**: $997/mo - Unlimited agents

### Lead Magnet
- Free AI Readiness Assessment
- 30-minute strategy call
- Custom AI implementation roadmap

---

## 🔥 FIRST ACTIONS (NOW!)

1. **Set up database** → Go to Supabase SQL editor
2. **Create lead_capture table** → Run schema script
3. **Build landing page** → Create `frontend/app/page.tsx`
4. **Create API** → Build `backend/main.py`
5. **Test locally** → Verify form → API → database flow
6. **Deploy** → Vercel + Railway
7. **LAUNCH** → Ship it! 🚀

---

**Last Updated**: 2025-11-18  
**Status**: 🟢 READY TO BUILD  
**Next Step**: Set up Supabase schema
