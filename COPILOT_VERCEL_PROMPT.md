# GitHub Copilot: Vercel Deployment Fix Prompt

Use this comprehensive prompt with GitHub Copilot to diagnose and fix any Vercel deployment failures.

## 🤖 Copilot Prompt Template

```markdown
**Context:**  
My GitHub pull request has a Vercel deployment failure. I need you to:
1. Diagnose the error from deployment logs
2. Provide specific fixes for all possible failure scenarios
3. Generate necessary code/config changes
4. Guide me through verification steps

**Required Information from Vercel Logs:**  
[PASTE FULL ERROR LOGS HERE]

**If logs show "Build Failed":**
1. **Dependency Issues:**
   - If `Module not found` or `npm ERR!`:  
     - Add missing packages: `npm install <package> --save-exact`  
     - Update `package.json` dependencies section  
     - Generate patch for `package-lock.json`/`yarn.lock`

2. **Build Script Errors:**
   - If `Error: No build script found`:  
     - Add build command to `package.json`:  
       ```json
       "scripts": {
         "build": "next build" // or "react-scripts build"/"vite build"
       }
       ```
   - If framework-specific error (Next.js/Nuxt/etc):  
     - Create framework config file (`next.config.js`/`nuxt.config.js`) with:  
       ```js
       module.exports = {
         /* Framework-specific settings */
         output: 'standalone' // Example for Next.js
       }
       ```

3. **Environment Variables:**
   - If `process.env.MISSING_VAR is undefined`:  
     - Add to Vercel:  
       1. Go to project Settings → Environment Variables  
       2. Add key-value pairs  
     - Create `.env.local` for local testing:  
       ```
       MISSING_VAR=your_value
       ```

4. **Path Configuration:**
   - If `404 File not found`:  
     - Create `vercel.json` with correct routes:  
       ```json
       {
         "routes": [
           { "src": "/(.*)", "dest": "/public/$1" },
           { "src": "/api/(.*)", "dest": "/api/$1" }
         ]
       }
       ```
   - Set root directory in Vercel settings if not repository root

**If logs show "Deployment Timed Out":**
1. Increase timeout in `vercel.json`:  
   ```json
   {
     "functions": {
       "api/**/*.js": {
         "maxDuration": 30 // seconds
       }
     }
   }
   ```
2. Optimize large dependencies (add `.vercelignore` for unused files)

**Framework-Specific Fixes:**
- **Next.js:**  
  ```js
  // next.config.js
  module.exports = {
    output: 'standalone', // For Docker deployments
    eslint: { ignoreDuringBuilds: true } // If ESLint fails
  }
  ```

- **React/Vite:**  
  ```js
  // vite.config.js
  export default {
    build: {
      sourcemap: false // Reduce build size
    }
  }
  ```

- **Python/Streamlit:**  
  ```python
  # app.py - Vercel handler
  def handler(event, context):
      return {
          'statusCode': 200,
          'headers': {'Content-Type': 'application/json'},
          'body': json.dumps({'message': 'Streamlit App'})
      }
  ```

**Verification Steps:**
1. Run locally: `npm run build && npm start`
2. Test API routes with `curl`
3. Check browser console for client-side errors
4. Push changes to trigger new deployment

**Final Checklist:**
- [ ] Fixed build errors in logs
- [ ] Updated environment variables in Vercel
- [ ] Added/updated framework config files
- [ ] Verified build succeeds locally
- [ ] Pushed changes to GitHub branch
- [ ] Confirmed new Vercel deployment started

**Additional Requests:**
1. Generate exact code changes needed as patch files
2. Provide Vercel dashboard navigation guide
3. Suggest optimizations to prevent future failures
```

## 🚀 How to Use This Prompt

### Step 1: Get Error Details
1. Go to your GitHub PR
2. Find the Vercel deployment check (usually shows ❌ or ⚠️)
3. Click "Details" → "View logs"
4. Copy the full error message (last 50 lines if too long)

### Step 2: Execute with Copilot
1. Open GitHub Copilot Chat in VS Code or GitHub
2. Paste the prompt above
3. Replace `[PASTE FULL ERROR LOGS HERE]` with your actual error logs
4. Add any specific context about your project (framework, language, etc.)

### Step 3: Implement Suggested Fixes
Apply the code changes that Copilot provides, prioritizing:
1. Critical errors (build failures, missing dependencies)
2. Configuration issues (vercel.json, environment variables)
3. Optimization improvements (.vercelignore, timeouts)

### Step 4: Test and Deploy
1. Test fixes locally
2. Push changes to your branch
3. Monitor the new Vercel deployment
4. Check deployment logs for success

## 📋 Common Error Patterns & Quick Fixes

### Build Errors
| Error Pattern | Quick Fix |
|---------------|-----------|
| `Module not found` | Add to requirements.txt or package.json |
| `Command not found` | Add build script to package.json |
| `Python version not supported` | Add runtime.txt with `python-3.11` |
| `Function timeout` | Increase maxDuration in vercel.json |

### Configuration Errors
| Error Pattern | Quick Fix |
|---------------|-----------|
| `404 Not Found` | Fix routes in vercel.json |
| `Environment variable undefined` | Add to Vercel dashboard |
| `Build output not found` | Set correct output directory |
| `Permission denied` | Make start scripts executable |

### Framework-Specific Issues
| Framework | Common Issue | Solution |
|-----------|--------------|----------|
| Next.js | Build optimization | Add `output: 'standalone'` |
| React | Large bundle size | Enable tree shaking, add .vercelignore |
| Python/Streamlit | Port configuration | Handle PORT env var in app.py |
| Vue/Nuxt | SSR issues | Set `target: 'static'` |

## 🛠️ Advanced Troubleshooting

### Debug Mode
Enable debug logging by adding to vercel.json:
```json
{
  "env": {
    "DEBUG": "1",
    "VERCEL_DEBUG": "1"
  }
}
```

### Local Testing
```bash
# Install Vercel CLI
npm i -g vercel

# Test deployment locally
vercel dev

# Preview deployment
vercel --prebuilt
```

### Emergency Rollback
```bash
# Quick rollback via CLI
vercel rollback [deployment-url]

# Or via Vercel Dashboard:
# Deployments → Select working deployment → Promote
```

## ✨ Pro Tips for Copilot

1. **Be Specific**: Include exact error messages and line numbers
2. **Provide Context**: Mention your framework, version, and deployment target
3. **Ask for Alternatives**: Request multiple solution approaches
4. **Request Explanations**: Ask Copilot to explain why certain fixes work
5. **Iterative Fixing**: Fix one error type at a time for best results

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Deployment Troubleshooting Guide](./VERCEL_TROUBLESHOOTING.md)
- [Validation Tool](./vercel_validator.py)
- [Framework-specific guides](https://vercel.com/docs/frameworks)

---

💡 **Remember**: This prompt is designed to be comprehensive. Feel free to modify it based on your specific project needs and share sections with Copilot as needed.