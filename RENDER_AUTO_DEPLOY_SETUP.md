# Render Auto-Deployment Setup Guide

## ✅ COMPLETED STEPS

### 1. Requirements.txt ✅
- Updated with specific versions for stability
- Includes all necessary dependencies: Flask, requests, numpy, scipy, schedule, etc.
- Added version pinning to prevent deployment issues

### 2. Render.yaml Configuration ✅
- Added `repo: https://github.com/mostgood1/MLB-Betting.git`
- Added `branch: main` 
- Added `autoDeploy: true`
- This enables automatic deployments from your GitHub repository

## 🔧 RENDER DASHBOARD SETUP STEPS

### Step 3: Connect GitHub to Render (REQUIRED)

1. **Log into Render Dashboard**
   - Go to: https://dashboard.render.com/
   - Sign in with your account

2. **Access Your Web Service**
   - Find your `mlb-betting-predictions` service
   - Click on it to open the service details

3. **Connect Repository**
   - Look for "Settings" or "Repository" section
   - Click "Connect Repository" or "Link Repository"
   - Select GitHub as your Git provider
   - Authorize Render to access your GitHub account if prompted

4. **Configure Repository Connection**
   - Select Repository: `mostgood1/MLB-Betting`
   - Set Branch: `main`
   - Enable "Auto-Deploy": Toggle this ON
   - Confirm the settings

5. **Environment Variables (if needed)**
   - Go to "Environment" tab in your service
   - Add any API keys or sensitive data:
     - Add variables from your `api_keys.json` if needed for production
     - Example: `ODDS_API_KEY`, `MLB_API_KEY`, etc.

### Step 4: Test Auto-Deployment

1. **Make a Small Change**
   - Edit a file (like adding a comment to app.py)
   - Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Test auto-deployment"
   git push origin main
   ```

2. **Verify Deployment**
   - Go to your Render dashboard
   - You should see a new deployment starting automatically
   - Wait for it to complete (usually 2-5 minutes)

## 📋 VERIFICATION CHECKLIST

- [ ] GitHub repository connected to Render
- [ ] Auto-deploy enabled in Render dashboard
- [ ] Environment variables configured (if needed)
- [ ] Test deployment successful
- [ ] Live site reflects your latest changes

## 🚨 TROUBLESHOOTING

### If Auto-Deploy Doesn't Work:
1. Check that your GitHub repo is public or Render has access
2. Verify the branch name is exactly "main" (not "master")
3. Ensure render.yaml is in the root directory
4. Check Render deployment logs for errors

### If Build Fails:
1. Check requirements.txt is in root directory
2. Verify all import dependencies are listed
3. Check Python version compatibility (using 3.11)
4. Review Render build logs for specific errors

## 📝 NEXT STEPS AFTER SETUP

Once auto-deployment is working:
- Every `git push origin main` will trigger automatic deployment
- Changes will be live within 2-5 minutes
- You can monitor deployments in the Render dashboard
- No manual deployment actions needed

## 🔗 USEFUL LINKS

- Render Dashboard: https://dashboard.render.com/
- Your Repository: https://github.com/mostgood1/MLB-Betting
- Render Documentation: https://render.com/docs

---
**Status**: Ready for Render dashboard configuration
**Next Action**: Connect GitHub repository in Render dashboard
