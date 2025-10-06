# 🔐 GitHub Actions Secret Setup - Quick Start

Your SSH key has been located! Follow these steps to complete the setup:

## 📋 Step 1: Copy Your SSH Private Key

Your SSH private key is ready to be added to GitHub. 

**⚠️ IMPORTANT:** This key is already displayed above (starting with `-----BEGIN OPENSSH PRIVATE KEY-----`)

## 🔑 Step 2: Add to GitHub Secrets

### Quick Link:
👉 **[Click here to add secret](https://github.com/I-Dacosta/AquatiqTask/settings/secrets/actions/new)**

Or navigate manually:
1. Go to: https://github.com/I-Dacosta/AquatiqTask
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **"New repository secret"**

### Secret Configuration:

**Name:** (copy this exactly)
```
HOSTINGER_SSH_KEY
```

**Secret:** (copy the entire SSH key from terminal output)
```
-----BEGIN OPENSSH PRIVATE KEY-----
...entire key including this line and end line...
-----END OPENSSH PRIVATE KEY-----
```

**Important:** 
- ✅ Include the BEGIN and END lines
- ✅ Copy the entire key (all lines between BEGIN and END)
- ✅ No extra spaces before or after
- ❌ Don't modify or format the key

## ✅ Step 3: Verify Setup

After adding the secret:

1. **Check it's there:**
   - Go to: https://github.com/I-Dacosta/AquatiqTask/settings/secrets/actions
   - You should see: `HOSTINGER_SSH_KEY` (with a green checkmark)

2. **Test the workflow:**
   - Go to: https://github.com/I-Dacosta/AquatiqTask/actions
   - Click on **"Deploy to Hostinger VPS"**
   - Click **"Run workflow"** button (top right)
   - Select branch: `main`
   - Click green **"Run workflow"** button

3. **Watch it deploy:**
   - You'll see a new workflow run appear
   - Click on it to watch progress live
   - Should complete in ~2 minutes

## 🎉 What Happens Next?

Once the secret is added, **every push to main will automatically deploy**:

```bash
# Make any change
echo "Test auto-deploy" >> README.md

# Commit and push
git add README.md
git commit -m "test: Trigger automatic deployment"
git push origin main

# 🚀 Deployment starts automatically!
# Watch at: https://github.com/I-Dacosta/AquatiqTask/actions
```

## 🔍 Verify Deployment Works

After the first deployment runs:

1. **Check n8n:** http://31.97.38.31:5678
2. **Check AI service:** http://31.97.38.31:8000/health
3. **Check logs:** `ssh root@31.97.38.31 'cd /opt/TaskPriority && docker compose -f docker-compose-ip.yml logs -f'`

## 🐛 Troubleshooting

### "Permission denied (publickey)"

**Solution:** The key might not be copied correctly.
- Make sure you copied the ENTIRE key including BEGIN/END lines
- No extra spaces at start or end
- Try removing and re-adding the secret

### "Host key verification failed"

**Solution:** Should auto-fix, but if not:
```bash
# Add VPS to GitHub Actions known_hosts (already in workflow)
ssh-keyscan -H 31.97.38.31 >> ~/.ssh/known_hosts
```

### Workflow doesn't trigger

**Solution:** 
1. Check Actions are enabled: https://github.com/I-Dacosta/AquatiqTask/settings/actions
2. Make sure secret name is exactly: `HOSTINGER_SSH_KEY`
3. Try manual trigger from Actions tab

## 📚 Full Documentation

For more details, see: [`docs/GITHUB_ACTIONS_SETUP.md`](../docs/GITHUB_ACTIONS_SETUP.md)

---

## ✨ Summary

**You're almost done!** Just need to:

1. ✅ Add `HOSTINGER_SSH_KEY` secret to GitHub (link above)
2. ✅ Test manual deployment from Actions tab
3. ✅ Push code to trigger automatic deployment

**Time to complete:** ~2 minutes ⏱️

**Result:** Automated deployments on every push! 🚀
