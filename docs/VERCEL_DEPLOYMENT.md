# Vercel Deployment Guide

This guide covers deploying the Past Papers Downloader application to Vercel, including setting up Upstash Redis for job persistence.

## Prerequisites

- GitHub account
- Vercel account (free tier works)
- Upstash Redis account (free tier: 10,000 commands/day)

## Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Deploy to Vercel"
git push
```

### 2. Connect to Vercel

1. Go to [Vercel Dashboard](https://vercel.com)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Root directory: `/` (default)
5. Vercel will auto-detect the configuration from `vercel.json`

### 3. Add Upstash Redis (REQUIRED)

**Why Redis is Required:**
- Vercel serverless functions are stateless
- Each function invocation has an isolated `/tmp` directory
- Jobs created in one request aren't visible in another
- Redis provides persistent storage across function invocations

**Setup Steps:**

1. In your Vercel project dashboard, go to **"Storage"** tab (or **"Integrations"**)
2. Click **"Browse Marketplace"** or **"Add Integration"**
3. Search for **"Upstash for Redis"** (or just "Upstash Redis")
4. Click **"Create"** or **"Add"**
5. Follow the prompts:
   - Create a new database
   - Name it: `pastpapers-jobs` (or any name you prefer)
   - Choose a region (closest to your users)
6. Vercel will automatically configure:
   - `UPSTASH_REDIS_REST_URL` - Redis REST API URL
   - `UPSTASH_REDIS_REST_TOKEN` - Redis authentication token
7. **No code changes needed** - the app detects these env vars automatically!

### 4. Redeploy

After adding Redis:

1. Go to **"Deployments"** tab
2. Click **"Redeploy"** on the latest deployment
3. Or push a new commit to trigger auto-deploy

### 5. Verify Deployment

1. Check Vercel logs for:
   - `"Redis connection established successfully"` (if Redis is working)
   - `"Redis environment variables not set, using file storage"` (if Redis is not configured)
2. Test a download:
   - Select qualification, subjects, and seasons
   - Start a download
   - Check the progress page - should work without "Job not found" errors!

## How It Works

### Storage Strategy

The application uses a **three-tier storage strategy**:

1. **In-Memory** (fast, for local dev)
   - Jobs stored in `download_jobs` dictionary
   - Instant access, but lost on restart

2. **Redis** (for Vercel/serverless)
   - Primary storage when `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` are set
   - Persists across function invocations
   - Jobs expire after 1 hour (configurable)

3. **File Storage** (fallback)
   - Local: `temp_downloads/jobs/`
   - Vercel: `/tmp/pastpapers_jobs/` (ephemeral, not recommended)
   - Used if Redis is unavailable or for local development

### Code Flow

```python
# When creating a job:
1. Store in memory (for fast local access)
2. Try Redis (if env vars are set)
   - Verify write by reading back
   - If successful, skip file storage
3. Fallback to file storage (if Redis unavailable)

# When reading a job:
1. Check memory (fastest)
2. Check Redis (if enabled)
3. Check file system (fallback)
```

## Vercel Limitations

### Function Timeouts

- **Hobby (Free)**: 10 seconds
- **Pro**: 60 seconds
- **Enterprise**: 300 seconds

**Impact:**
- Large downloads may timeout
- Background tasks help, but ZIP creation can still timeout
- Consider upgrading to Pro for larger downloads

### Storage Limits

- `/tmp` directory: 512 MB per function
- Ephemeral: Cleared between invocations
- **Solution**: Use Redis for job storage, `/tmp` only for temporary files

### Cold Starts

- First request after inactivity: ~1-2 seconds
- Subsequent requests: Fast
- **Solution**: Use Vercel Pro for better performance

## Environment Variables

The following environment variables are automatically set by Vercel when you add Upstash Redis:

- `UPSTASH_REDIS_REST_URL` - Redis REST API endpoint
- `UPSTASH_REDIS_REST_TOKEN` - Redis authentication token

**Optional variables** (can be set manually in Vercel dashboard):

- `DEBUG` - Set to `true` for debug mode
- `MAX_CONCURRENT_DOWNLOADS` - Max concurrent downloads (default: 15)
- `DOWNLOAD_TIMEOUT` - Download timeout in seconds (default: 30)

## Troubleshooting

### "Job not found" Error

**Cause:** Redis not configured or connection failed

**Solution:**
1. Verify Redis is added in Vercel Storage tab
2. Check environment variables are set:
   - Go to **Settings** → **Environment Variables**
   - Verify `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` exist
3. Check Vercel logs for Redis connection errors
4. Redeploy after adding Redis

### Redis Connection Failed

**Check logs for:**
- `"Redis connection test failed"`
- `"Failed to save job to Redis"`

**Solutions:**
1. Verify Redis database is active in Upstash dashboard
2. Check environment variables are correct
3. Verify network connectivity (Vercel → Upstash)
4. Check Redis rate limits (free tier: 10,000 commands/day)

### Download Timeout

**Cause:** Function timeout (10s on Hobby plan)

**Solutions:**
1. Upgrade to Vercel Pro (60s timeout)
2. Reduce number of files per download
3. Download in smaller batches

### File Storage Issues

**Symptoms:**
- Jobs work locally but fail on Vercel
- "Permission denied" errors in logs

**Solution:**
- Ensure Redis is configured (file storage on Vercel is unreliable)
- Check that `/tmp` directory exists and is writable

## Cost Considerations

### Vercel

- **Hobby (Free)**: 
  - 100 GB bandwidth/month
  - 10s function timeout
  - Unlimited requests
- **Pro ($20/month)**:
  - 1 TB bandwidth/month
  - 60s function timeout
  - Better performance

### Upstash Redis

- **Free Tier**:
  - 10,000 commands/day
  - 256 MB storage
  - Usually sufficient for small/medium usage
- **Pay-as-you-go**:
  - $0.20 per 100K commands
  - $0.20 per GB storage/month

**Typical Usage:**
- Creating a job: ~2 commands
- Updating progress: ~1 command per update
- Reading job status: ~1 command
- **100 downloads/day ≈ 500 commands/day** (well within free tier)

## Alternative Deployment Options

If Vercel doesn't meet your needs:

### Railway

- Full server control
- No function timeouts
- Persistent storage
- Free tier available

### Render

- Similar to Railway
- Persistent storage
- Free tier available

### DigitalOcean App Platform

- VPS deployment
- Full control
- Persistent storage
- $5/month minimum

## Monitoring

### Vercel Logs

1. Go to **Deployments** → Click deployment → **Logs**
2. Look for:
   - Redis connection messages
   - Job creation/update logs
   - Error messages

### Upstash Dashboard

1. Go to [Upstash Console](https://console.upstash.com)
2. Check:
   - Command usage (daily limit)
   - Storage usage
   - Connection status

## Best Practices

1. **Always use Redis on Vercel** - File storage is unreliable
2. **Monitor Redis usage** - Stay within free tier limits
3. **Handle timeouts gracefully** - Show user-friendly error messages
4. **Clean up old jobs** - Jobs expire after 1 hour automatically
5. **Test locally first** - Use file storage for local development

## Support

If you encounter issues:

1. Check Vercel logs for errors
2. Verify Redis is configured correctly
3. Test locally to isolate Vercel-specific issues
4. Check Upstash dashboard for Redis status
5. Review this guide for common solutions

---

**Last Updated:** 2024
**Version:** 2.0.0
