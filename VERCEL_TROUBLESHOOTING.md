# Vercel Deployment Troubleshooting Guide

This comprehensive guide covers all common Vercel deployment failure scenarios and their solutions.

## Quick Diagnosis Steps

1. **Check Deployment Logs**: Go to Vercel dashboard → Project → Deployment → "View Logs"
2. **Identify Error Type**: Look for specific error patterns listed below
3. **Apply Targeted Fix**: Use the appropriate solution from this guide
4. **Test Locally**: Always test fixes locally before deploying
5. **Monitor Redeploy**: Watch new deployment logs for success

## Common Error Patterns & Solutions

### 1. Build Failed Errors

#### Module Not Found / Dependency Issues
```
Error: Module not found: Can't resolve 'package-name'
npm ERR! code ENOTFOUND
```

**Solutions:**
```bash
# Add missing packages
npm install <package> --save-exact
yarn add <package>
pip install <package>

# For Python projects
pip install -r requirements.txt

# Verify package.json or requirements.txt
```

**For Python/Streamlit projects:**
```bash
# Ensure requirements.txt contains all dependencies
streamlit>=1.47.0
PyPDF2>=3.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

#### Missing Build Script
```
Error: No build script found
```

**Solution - Add to package.json:**
```json
{
  "scripts": {
    "build": "next build",
    "start": "next start"
  }
}
```

**For Python/Streamlit projects:**
- No build script needed, handled by `@vercel/python`

#### Framework Configuration Errors

**Next.js Issues:**
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  eslint: { 
    ignoreDuringBuilds: true 
  },
  experimental: {
    esmExternals: false
  }
}
```

**React/Vite Issues:**
```javascript
// vite.config.js
export default {
  build: {
    sourcemap: false,
    outDir: 'dist'
  },
  base: './'
}
```

**Streamlit Issues:**
```python
# Already handled in app.py setup_environment() function
# No additional config needed
```

### 2. Environment Variable Issues

#### Missing Environment Variables
```
Error: process.env.MISSING_VAR is undefined
ReferenceError: OPENAI_API_KEY is not defined
```

**Solutions:**

1. **Add to Vercel Dashboard:**
   - Go to Project Settings → Environment Variables
   - Add required variables for each environment (Development, Preview, Production)

2. **Common Variables for DocQuery:**
   ```
   OPENAI_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:pass@host:port/db
   PORT=8501
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

3. **Create .env.local for testing:**
   ```bash
   # .env.local (add to .gitignore)
   OPENAI_API_KEY=your_test_key
   DATABASE_URL=sqlite:///test.db
   ```

### 3. Path & Routing Issues

#### 404 File Not Found
```
Error: 404 - File or directory not found
```

**Solution - Create/update vercel.json:**
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "functions": {
    "app.py": {
      "maxDuration": 30
    }
  }
}
```

#### Incorrect Root Directory
- Set root directory in Vercel project settings if app is not in repository root
- Update build output directory if needed

### 4. Timeout Issues

#### Function Timeout
```
Error: Function execution timed out
```

**Solution - Update vercel.json:**
```json
{
  "functions": {
    "app.py": {
      "maxDuration": 30
    },
    "api/**/*.py": {
      "maxDuration": 60
    }
  }
}
```

#### Build Timeout
- Optimize dependencies using `.vercelignore`
- Remove unnecessary files from build

### 5. Memory Issues

#### Out of Memory
```
Error: Process out of memory
```

**Solutions:**
1. **Create .vercelignore:**
   ```
   # Large files to exclude
   *.pdf
   *.mp4
   *.zip
   __pycache__/
   .git/
   node_modules/
   ```

2. **Optimize dependencies:**
   ```bash
   # Use lighter alternatives
   pip install Pillow-SIMD  # instead of Pillow
   pip install numpy-slim   # if available
   ```

### 6. Python-Specific Issues

#### Python Version Mismatch
```
Error: Python version not supported
```

**Solution - Add runtime.txt:**
```
python-3.11
```

#### Package Installation Failures
```
Error: Failed building wheel for package
```

**Solutions:**
```bash
# Use binary packages when possible
pip install psycopg2-binary  # instead of psycopg2
pip install Pillow           # pre-compiled wheels
```

## Framework-Specific Quick Fixes

### Streamlit (Current Project)
```python
# app.py - Already implemented
def setup_environment():
    port = int(os.getenv('PORT', '8501'))
    os.environ.setdefault('STREAMLIT_SERVER_PORT', str(port))
    os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
    os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
    return port
```

### Next.js
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
  experimental: { esmExternals: false },
  eslint: { ignoreDuringBuilds: true }
}
```

### React/Create React App
```json
{
  "scripts": {
    "build": "react-scripts build",
    "start": "serve -s build"
  }
}
```

### Vue.js/Nuxt
```javascript
// nuxt.config.js
export default {
  ssr: false,
  target: 'static',
  generate: { fallback: true }
}
```

## Verification Checklist

Before deploying, ensure:

- [ ] **Local Build Success**: `npm run build` or `pip install -r requirements.txt`
- [ ] **Environment Variables**: All required variables set in Vercel dashboard
- [ ] **Framework Config**: Appropriate config files created
- [ ] **Dependencies**: All packages listed in package.json/requirements.txt
- [ ] **Ignore Files**: .vercelignore created to exclude unnecessary files
- [ ] **Routes**: vercel.json routes configuration correct
- [ ] **Function Timeouts**: Adequate timeouts set for long-running operations

## Advanced Debugging

### Enable Debug Logging
```json
{
  "env": {
    "DEBUG": "1",
    "VERCEL_DEBUG": "1"
  }
}
```

### Test Deployment Locally
```bash
# Install Vercel CLI
npm i -g vercel

# Test locally
vercel dev

# Deploy to preview
vercel --prebuilt
```

### Common Log Patterns to Look For

1. **Import Errors**: `ModuleNotFoundError`, `ImportError`
2. **Path Issues**: `ENOENT`, `404`
3. **Memory Issues**: `out of memory`, `killed`
4. **Timeout Issues**: `Function execution timed out`
5. **Build Issues**: `Command failed`, `Exit code 1`

## Emergency Fixes

### Quick Rollback
```bash
# Via Vercel CLI
vercel rollback [deployment-url]

# Via Dashboard
# Go to Deployments → Select working deployment → Promote to Production
```

### Minimal Working Configuration

**vercel.json** (minimal):
```json
{
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "app.py" }]
}
```

**requirements.txt** (minimal):
```
streamlit>=1.47.0
```

## Success Indicators

Deployment successful when you see:
- ✅ Build completed successfully
- ✅ Functions deployed
- ✅ Domain assigned
- ✅ Logs show no errors
- ✅ App accessible via assigned URL

## Getting Help

1. **Check Vercel Status**: https://vercel-status.com/
2. **Vercel Documentation**: https://vercel.com/docs
3. **Community Support**: https://github.com/vercel/vercel/discussions
4. **Framework-specific docs**: Next.js, React, Vue, etc.

## Additional Resources

- [Vercel Python Runtime](https://vercel.com/docs/runtimes/python)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy)
- [Environment Variables](https://vercel.com/docs/environment-variables)
- [Function Configuration](https://vercel.com/docs/functions/configuration)