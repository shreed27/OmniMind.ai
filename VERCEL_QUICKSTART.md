# Vercel Deployment Quick Reference

## Your Project Configuration

Your OmniMind.ai frontend is configured for Vercel with the following files:

- `vercel.json` - Main Vercel configuration
- `frontend/.env.production` - Production environment variables
- `DEPLOYMENT.md` - Full deployment guide

## Quick Deploy Commands

### First Time Deployment
```bash
# 1. Login to Vercel (opens browser)
vercel login

# 2. Deploy to production
cd /Users/shreedshrivastava/Projects/OmniMind.ai
vercel --prod
```

### Subsequent Deployments
```bash
# From project root
vercel --prod
```

### Preview Deployments (for testing)
```bash
vercel
# This creates a preview URL without affecting production
```

## Post-Deployment Tasks

After your first deployment:

1. **Get your deployment URL** - Vercel will display it, something like:
   ```
   https://omnimind-ai.vercel.app
   ```

2. **Update environment variables** (when backend is ready):
   - Go to [vercel.com](https://vercel.com)
   - Navigate to your project → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_BASE_URL` to your Cloud Run backend URL

3. **Redeploy after env var changes**:
   ```bash
   vercel --prod --force
   ```

## Useful Vercel CLI Commands

```bash
# Check deployment status
vercel ls

# View project details
vercel inspect [deployment-url]

# View logs
vercel logs [deployment-url]

# Remove a deployment
vercel remove [deployment-id]

# Link local project to Vercel project
vercel link

# Pull environment variables locally
vercel env pull
```

## Automatic Deployments via Git

To enable automatic deployments:

1. Push your code to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your repository
4. Every push to `main` = Production deployment
5. Every PR = Preview deployment with unique URL

## Troubleshooting

### Build Fails
- Check build logs: `vercel logs [url]`
- Verify `frontend/package.json` dependencies
- Ensure Node.js version compatibility

### Environment Variables Not Working
- Make sure they start with `NEXT_PUBLIC_` for client-side access
- Redeploy after adding new env vars
- Check in Project Settings → Environment Variables

### API Connection Issues
- Verify `NEXT_PUBLIC_API_BASE_URL` is correct
- Check CORS settings in your backend
- Test API endpoint directly with curl

## Team and Project Info

- **Team**: iamshreedshrivastava's projects
- **Team ID**: team_wUh2nCx47KGrYHm20vtXCoTq
- **Project Name**: omnimind-ai
- **Framework**: Next.js 14.2.4

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ⬜ Deploy backend to Google Cloud Run
3. ⬜ Update `NEXT_PUBLIC_API_BASE_URL` with backend URL
4. ⬜ Configure databases (PostgreSQL, Neo4j, Redis, Qdrant)
5. ⬜ Set up custom domain (optional)
6. ⬜ Enable Vercel Analytics (optional)

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js on Vercel](https://vercel.com/docs/frameworks/nextjs)
- [Environment Variables Guide](https://vercel.com/docs/projects/environment-variables)
- [Custom Domains](https://vercel.com/docs/custom-domains)

---

**Questions or Issues?**

Run `vercel help` or visit the [Vercel Support](https://vercel.com/support)
