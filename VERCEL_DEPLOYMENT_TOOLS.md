# Vercel Deployment Tools - Quick Reference

This document provides quick access to the comprehensive Vercel deployment troubleshooting tools added to the DocQuery repository.

## 🚀 Quick Start

### Pre-Deployment Validation
```bash
# Validate your deployment configuration
python vercel_validator.py
```

### Post-Deployment Health Check
```bash
# Check if your deployed app is healthy
python health_check.py https://your-app.vercel.app
```

## 📚 Documentation Files

| File | Purpose | When to Use |
|------|---------|-------------|
| [`VERCEL_TROUBLESHOOTING.md`](./VERCEL_TROUBLESHOOTING.md) | Comprehensive troubleshooting guide | When you have deployment failures |
| [`COPILOT_VERCEL_PROMPT.md`](./COPILOT_VERCEL_PROMPT.md) | GitHub Copilot prompt template | When working with AI to fix issues |
| [`vercel_validator.py`](./vercel_validator.py) | Pre-deployment validation script | Before every deployment |
| [`health_check.py`](./health_check.py) | Post-deployment health checker | After successful deployment |

## 🛠️ Tools Overview

### Validation Tool (`vercel_validator.py`)
- ✅ Checks vercel.json configuration
- ✅ Validates requirements.txt
- ✅ Verifies app.py setup
- ✅ Tests environment variables
- ✅ Checks optimization files
- ✅ Tests dependency installation

### Health Check Tool (`health_check.py`)
- 🏥 Tests main endpoint response
- 🏥 Checks Vercel handler function
- 🏥 Validates static assets
- 🏥 Inspects response headers
- 🏥 Measures performance metrics

## 🎯 Common Scenarios

### Before Deploying
```bash
# 1. Run validation
python vercel_validator.py

# 2. Test locally
streamlit run app.py

# 3. Deploy
vercel --prod
```

### Deployment Failed
1. Check logs in Vercel dashboard
2. Use the troubleshooting guide: [`VERCEL_TROUBLESHOOTING.md`](./VERCEL_TROUBLESHOOTING.md)
3. Or use the Copilot prompt: [`COPILOT_VERCEL_PROMPT.md`](./COPILOT_VERCEL_PROMPT.md)

### After Successful Deployment
```bash
# Verify everything is working
python health_check.py https://your-app.vercel.app
```

## 📝 Configuration Files

### Enhanced `vercel.json`
- ✅ Optimized function memory (1024MB)
- ✅ Proper timeout configuration (30s)
- ✅ Environment variables for Streamlit
- ✅ Regional deployment (iad1)

### `.vercelignore`
- 🚫 Excludes PDF files (large assets)
- 🚫 Excludes Python cache files
- 🚫 Excludes development files
- 🚫 Excludes test files

### `.gitignore`
- 🚫 Standard Python gitignore patterns
- 🚫 Environment variable files
- 🚫 IDE and OS files
- 🚫 Cache and temporary files

## 🔧 Troubleshooting Workflow

1. **Issue Occurs** → Check Vercel deployment logs
2. **Identify Pattern** → Use troubleshooting guide for specific error
3. **Apply Fix** → Implement suggested solution
4. **Validate** → Run `python vercel_validator.py`
5. **Deploy** → Push changes and monitor logs
6. **Verify** → Run `python health_check.py <url>`

## 🤖 AI-Assisted Debugging

The [`COPILOT_VERCEL_PROMPT.md`](./COPILOT_VERCEL_PROMPT.md) contains a comprehensive prompt you can use with:
- GitHub Copilot
- ChatGPT
- Claude
- Any AI coding assistant

Just paste your error logs and get targeted solutions!

## ✅ Validation Checklist

Before deploying, ensure:
- [ ] `python vercel_validator.py` passes all checks
- [ ] Local testing works: `streamlit run app.py`
- [ ] All environment variables set in Vercel dashboard
- [ ] No sensitive data in repository
- [ ] `.vercelignore` excludes unnecessary files

## 🚨 Emergency Procedures

### Quick Rollback
```bash
# If deployment fails, rollback immediately
vercel rollback <previous-deployment-url>
```

### Minimal Working State
If all else fails, revert to the minimal configuration in `vercel.json`:
```json
{
  "builds": [{"src": "app.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
```

## 📞 Getting Help

1. **Documentation**: Start with [`VERCEL_TROUBLESHOOTING.md`](./VERCEL_TROUBLESHOOTING.md)
2. **AI Assistant**: Use [`COPILOT_VERCEL_PROMPT.md`](./COPILOT_VERCEL_PROMPT.md)
3. **Validation**: Run `python vercel_validator.py`
4. **Community**: [Vercel GitHub Discussions](https://github.com/vercel/vercel/discussions)

---

💡 **Pro Tip**: Bookmark this page and run validation before every deployment to catch issues early!