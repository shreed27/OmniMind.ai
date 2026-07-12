# OmniMind.ai Deployment Guide

## Architecture Overview

OmniMind.ai follows a decoupled architecture:
- **Frontend**: Next.js application → Deploy to **Vercel**
- **Backend**: FastAPI (Python) → Deploy to **Google Cloud Run**
- **Databases**: PostgreSQL, Neo4j, Redis, Qdrant → Cloud infrastructure

---

## Frontend Deployment to Vercel

### Prerequisites
1. A [Vercel account](https://vercel.com/signup)
2. Vercel CLI installed (optional): `npm i -g vercel`

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Connect Repository**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub/GitLab/Bitbucket repository
   - Vercel will auto-detect the Next.js framework

2. **Configure Project**:
   - **Root Directory**: Leave as default (Vercel will use the config in `vercel.json`)
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/.next`
   - **Install Command**: `cd frontend && npm install`

3. **Set Environment Variables**:
   Navigate to **Project Settings → Environment Variables** and add:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-backend-url.run.app/api/v1
   ```
   *Note: Update this URL after deploying your backend to Google Cloud Run*

4. **Deploy**:
   - Click **Deploy**
   - Vercel will build and deploy your application
   - You'll receive a production URL (e.g., `omnimind-ai.vercel.app`)

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd /path/to/OmniMind.ai
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? [Select your team/personal account]
# - Link to existing project? No
# - What's your project's name? omnimind-ai
# - In which directory is your code located? ./

# For production deployment
vercel --prod
```

### Option 3: Deploy via GitHub Integration (CI/CD)

1. **Connect GitHub Repository**:
   - Push your code to GitHub
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your repository

2. **Configure Auto-Deployments**:
   - Every push to `main` → Production deployment
   - Every pull request → Preview deployment
   - Vercel automatically detects changes in the `frontend/` directory

---

## Backend Deployment to Google Cloud Run

### Prerequisites
1. [Google Cloud Account](https://cloud.google.com/)
2. [gcloud CLI](https://cloud.google.com/sdk/docs/install) installed
3. Project created in Google Cloud Console

### Steps

1. **Authenticate and Set Project**:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

2. **Build and Push Container**:
```bash
# Navigate to backend directory
cd backend

# Build container image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/omnimind-backend

# Or use Cloud Build
gcloud run deploy omnimind-backend \
  --image gcr.io/YOUR_PROJECT_ID/omnimind-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Set Environment Variables**:
```bash
gcloud run services update omnimind-backend \
  --set-env-vars="GOOGLE_API_KEY=your_gemini_key" \
  --set-env-vars="DATABASE_URL=your_postgres_url" \
  --set-env-vars="NEO4J_URI=your_neo4j_url" \
  --set-env-vars="REDIS_URL=your_redis_url"
```

4. **Get Backend URL**:
```bash
gcloud run services describe omnimind-backend --format='value(status.url)'
```

5. **Update Frontend Environment**:
   - Copy the Cloud Run URL from step 4
   - Update Vercel environment variable `NEXT_PUBLIC_API_BASE_URL` with this URL

---

## Environment Variables Reference

### Frontend (Vercel)
| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API endpoint | `https://omnimind-backend-xyz.run.app/api/v1` |

### Backend (Cloud Run)
| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Gemini API key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `NEO4J_URI` | Neo4j graph database URI | Yes |
| `NEO4J_USER` | Neo4j username | Yes |
| `NEO4J_PASSWORD` | Neo4j password | Yes |
| `REDIS_URL` | Redis cache URL | Yes |
| `QDRANT_URL` | Qdrant vector DB URL | Yes |
| `QDRANT_API_KEY` | Qdrant API key | Optional |

---

## Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Google Cloud Run
- [ ] Database services configured (PostgreSQL, Neo4j, Redis, Qdrant)
- [ ] Environment variables set in both Vercel and Cloud Run
- [ ] Frontend can successfully call backend API
- [ ] Executive board debates working
- [ ] Git copilot features functional
- [ ] Social campaign creator operational
- [ ] Edge runtime (Gemma) configured for offline continuity

---

## Continuous Deployment

### Vercel (Frontend)
- **Automatic**: Every push to `main` deploys to production
- **Preview**: Every PR gets a preview deployment
- **Rollback**: Use Vercel dashboard to rollback to previous deployments

### Cloud Run (Backend)
Set up Cloud Build triggers:
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/omnimind-backend', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/omnimind-backend']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'omnimind-backend'
      - '--image'
      - 'gcr.io/$PROJECT_ID/omnimind-backend'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

---

## Monitoring & Logs

### Vercel
- **Analytics**: `https://vercel.com/[team]/[project]/analytics`
- **Logs**: `https://vercel.com/[team]/[project]/logs`
- **Speed Insights**: Enable in project settings

### Google Cloud Run
```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=omnimind-backend" --limit 50

# Monitor metrics
gcloud run services list
gcloud run services describe omnimind-backend
```

---

## Troubleshooting

### Frontend Issues
- **Build Fails**: Check build logs in Vercel dashboard
- **API Connection**: Verify `NEXT_PUBLIC_API_BASE_URL` is correct
- **Runtime Errors**: Check Vercel function logs

### Backend Issues
- **Container Won't Start**: Check Cloud Run logs with `gcloud logging read`
- **Memory Issues**: Increase memory in Cloud Run settings
- **Slow Responses**: Check if database connections are properly pooled

---

## Security Considerations

1. **API Keys**: Never commit API keys to git. Use environment variables.
2. **CORS**: Configure CORS in FastAPI backend to allow only your Vercel domain
3. **Authentication**: Implement proper JWT/OAuth in production
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **HTTPS**: Both Vercel and Cloud Run provide HTTPS by default

---

**Deployment Status**: 🚀 Ready to Deploy

For questions or issues, refer to:
- [Vercel Documentation](https://vercel.com/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
