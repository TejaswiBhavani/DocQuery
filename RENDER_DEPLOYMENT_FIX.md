# Render Deployment Guide for DocQuery

This guide provides step-by-step instructions for deploying DocQuery on Render with the new configuration that fixes the 502 Bad Gateway error.

## 🔧 What Was Fixed

### Root Cause Issues:
1. **Port Binding Issue**: $PORT environment variable wasn't properly handled
2. **Memory Limitations**: Free tier (512MB) insufficient for AI models  
3. **Health Check Missing**: Render requires health monitoring endpoint
4. **Large Deployment Size**: No file exclusions for faster deployments

### Solutions Implemented:
✅ **Health Check Endpoint** (`healthz.py`): FastAPI endpoint at `/healthz` for monitoring  
✅ **Robust Port Configuration**: Enhanced error handling and validation  
✅ **Memory Upgrade**: Changed from Free to Starter plan (1GB RAM)  
✅ **Deployment Optimization**: Added `.renderignore` to exclude large files  
✅ **Dual-Service Startup**: Health endpoint + Streamlit app running together

## 🚀 Deployment Steps

### 1. Update Your Render Service

1. **Go to Render Dashboard** → Your Service → Settings
2. **Update Instance Type**:
   - Change from **Free** to **Starter** 
   - This provides 1GB RAM (required for AI models)
   - Cost: ~$7/month for better performance

### 2. Verify Build Configuration

Your `render.yaml` is already configured with:
```yaml
services:
  - type: web
    name: docquery-app
    env: python
    plan: starter  # 1GB RAM
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn healthz:app --host 0.0.0.0 --port $PORT & streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
    healthCheckPath: /healthz
```

### 3. Environment Variables

Ensure these environment variables are set in Render:
```
PYTHONUNBUFFERED=true
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_ENABLE_CORS=true
RENDER_SERVICE_NAME=docquery-app
```

### 4. Deploy and Monitor

1. **Deploy**: Push your changes or redeploy from Render dashboard
2. **Monitor Logs**: Watch for these success messages:
   ```
   DocQuery: Configured to run on port 10000
   Starting health check server on port 10000
   Starting Streamlit app...
   ```
3. **Test Health Endpoint**: Visit `https://your-app.onrender.com/healthz`
4. **Test Main App**: Visit `https://your-app.onrender.com`

## 🔍 Troubleshooting

### If 502 Bad Gateway Persists:

1. **Check Logs** in Render Dashboard:
   ```bash
   # Look for these success indicators:
   DocQuery: Configured to run on port XXXX
   Health check server starting...
   Streamlit running on port XXXX
   ```

2. **Memory Issues**: 
   ```bash
   # If you see "Killed" or memory errors:
   # Upgrade to Professional plan (2GB RAM)
   ```

3. **Port Issues**:
   ```bash
   # If port binding fails:
   # Check that both services start on the same PORT
   ```

### Test Health Endpoint:

```bash
# Should return 200 OK
curl https://your-app.onrender.com/healthz

# Detailed health info
curl https://your-app.onrender.com/health
```

### Common Log Messages:

✅ **Success**:
```
DocQuery: Starting on port 10000
Health check server starting...
Streamlit app running...
```

❌ **Failure**:
```
Error: Port already in use
Killed (out of memory)
ModuleNotFoundError: streamlit
```

## 📊 Performance Expectations

### Startup Time:
- **First Deploy**: 5-10 minutes (installing dependencies)
- **Subsequent Deploys**: 2-5 minutes (cached dependencies)

### Memory Usage:
- **Base App**: ~300MB
- **With AI Models**: ~800MB-1.2GB
- **Recommended**: Starter plan minimum

### Response Times:
- **Health Check**: <100ms
- **Document Upload**: 5-30 seconds (depending on size)
- **AI Analysis**: 10-60 seconds (depending on complexity)

## 🎯 Key Files Changed

1. **`healthz.py`**: New health check endpoint
2. **`render.yaml`**: Updated configuration with health checks
3. **`requirements.txt`**: Added FastAPI, uvicorn, psutil
4. **`app.py`**: Enhanced port configuration
5. **`.renderignore`**: Deployment optimization
6. **`start.sh`**: Updated startup script

## ✅ Final Checklist

Before deploying, ensure:
- [ ] Instance type is **Starter** or higher (1GB+ RAM)
- [ ] Health check path is set to `/healthz`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command includes both health endpoint AND Streamlit
- [ ] Environment variables are configured
- [ ] Repository changes are pushed to main branch

## 🆘 Getting Help

If deployment still fails:

1. **Check Render Logs** for specific error messages
2. **Verify** all files are properly committed and pushed
3. **Test locally** if possible with the same environment
4. **Check** that your OpenAI API key (if used) is properly set

The configuration is now optimized for Render's infrastructure and should resolve the 502 Bad Gateway error. The health endpoint allows Render to monitor your service properly, while the memory upgrade ensures AI models can load successfully.