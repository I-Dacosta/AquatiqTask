# GitHub Actions Setup Guide

This guide will help you set up automated deployments to your Hostinger VPS using GitHub Actions.

## 🎯 What This Does

Every time you push code to the `main` branch, GitHub Actions will automatically:
1. 📥 Pull the latest code to your VPS
2. 🏗️  Build the AI service Docker image
3. 🔄 Restart all services
4. 🏥 Run health checks to verify deployment
5. ✅ Report success/failure

---

## 📋 Prerequisites

- ✅ VPS deployed and running (31.97.38.31)
- ✅ Git repository on GitHub (I-Dacosta/AquatiqTask)
- ✅ SSH access to VPS configured
- ⚠️  GitHub repository secrets (we'll set these up)

---

## 🔐 Step 1: Get Your SSH Private Key

Your SSH private key is needed so GitHub Actions can connect to your VPS.

### Option A: Use Existing Key (Recommended)

```bash
# Display your private key (the one you're already using)
cat ~/.ssh/id_rsa

# Or if you used a different key:
cat ~/.ssh/id_ed25519
```

**Copy the entire output**, including:
```
-----BEGIN OPENSSH PRIVATE KEY-----
...entire key content...
-----END OPENSSH PRIVATE KEY-----
```

### Option B: Create New Deployment Key

If you want a separate key just for GitHub Actions:

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy -N ""

# Display the private key
cat ~/.ssh/github_actions_deploy

# Add public key to VPS
ssh-copy-id -i ~/.ssh/github_actions_deploy.pub root@31.97.38.31

# Test the new key
ssh -i ~/.ssh/github_actions_deploy root@31.97.38.31 "echo 'Connection successful!'"
```

---

## 🔑 Step 2: Add GitHub Secret

1. **Go to your GitHub repository:**
   ```
   https://github.com/I-Dacosta/AquatiqTask/settings/secrets/actions
   ```

2. **Click "New repository secret"**

3. **Add the SSH key:**
   - **Name:** `HOSTINGER_SSH_KEY`
   - **Value:** Paste your entire SSH private key (from Step 1)
   - Click **"Add secret"**

---

## ✅ Step 3: Verify Setup

### Enable Actions (if not already enabled)

1. Go to: https://github.com/I-Dacosta/AquatiqTask/settings/actions
2. Under "Actions permissions", select:
   - ✅ **"Allow all actions and reusable workflows"**
3. Click **"Save"**

### Test the Workflow

You can trigger a deployment manually to test:

1. Go to: https://github.com/I-Dacosta/AquatiqTask/actions
2. Click on **"Deploy to Hostinger VPS"** workflow
3. Click **"Run workflow"** button
4. Select branch: `main`
5. Click **"Run workflow"**

**Watch the deployment progress live!** ⏱️

---

## 🔄 Step 4: Automatic Deployments

Now, every time you push to main, it will auto-deploy:

```bash
# Make a change
echo "# Test deployment" >> README.md

# Commit and push
git add .
git commit -m "Test GitHub Actions deployment"
git push origin main

# Watch it deploy automatically!
# Visit: https://github.com/I-Dacosta/AquatiqTask/actions
```

---

## 🎛️ Workflow Configuration

### Trigger Conditions

The workflow runs when:
- ✅ You push to `main` branch
- ✅ You manually trigger via GitHub UI
- ❌ **Skip deployment** when only these change:
  - Markdown files (`*.md`)
  - GitHub Actions files (`.github/**`)
  - Documentation (`docs/**`)

### Deployment Steps

```mermaid
graph TD
    A[Push to main] --> B[Setup SSH]
    B --> C[Pull latest code on VPS]
    C --> D[Build AI service]
    D --> E[Restart services]
    E --> F[Wait 15s]
    F --> G[Health checks]
    G --> H{All healthy?}
    H -->|Yes| I[✅ Success]
    H -->|No| J[❌ Show logs]
```

---

## 🏥 Health Checks

The workflow verifies:

1. **Docker Services Status**
   ```bash
   docker compose -f docker-compose-ip.yml ps
   ```

2. **AI Service Health**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status":"healthy"}
   ```

3. **n8n Availability**
   ```bash
   curl http://localhost:5678
   # Expected: HTTP 200
   ```

4. **PostgreSQL Connection**
   ```bash
   pg_isready -U prioai
   # Expected: accepting connections
   ```

---

## 🐛 Troubleshooting

### "Permission denied (publickey)"

**Problem:** GitHub Actions can't connect to VPS.

**Solution:**
```bash
# 1. Verify your SSH key works locally
ssh root@31.97.38.31 "echo 'Test successful'"

# 2. Make sure you copied the PRIVATE key (not public)
cat ~/.ssh/id_rsa  # Should start with -----BEGIN

# 3. Verify the secret in GitHub:
# Go to: https://github.com/I-Dacosta/AquatiqTask/settings/secrets/actions
# Check that HOSTINGER_SSH_KEY exists
```

### "Host key verification failed"

**Problem:** VPS host key not recognized.

**Solution:** The workflow automatically handles this with `ssh-keyscan`, but if it fails:
```bash
# Add to workflow (already included):
ssh-keyscan -H 31.97.38.31 >> ~/.ssh/known_hosts
```

### Deployment succeeds but services fail

**Problem:** Code deployed but containers won't start.

**Solution:**
```bash
# SSH to VPS and check logs
ssh root@31.97.38.31
cd /opt/TaskPriority
docker compose -f docker-compose-ip.yml logs --tail 100

# Check for:
# - Missing environment variables
# - Port conflicts
# - Database connection issues
```

### Workflow doesn't trigger

**Problem:** Push to main but workflow doesn't run.

**Solution:**
1. Check Actions are enabled: https://github.com/I-Dacosta/AquatiqTask/settings/actions
2. Verify workflow file is in `.github/workflows/` folder
3. Check if path is in ignore list (`.md`, `.github/`, `docs/`)

---

## 🔒 Security Best Practices

### ✅ DO

- ✅ Use SSH keys (not passwords)
- ✅ Use separate deployment key (not your personal key)
- ✅ Rotate SSH keys periodically
- ✅ Use GitHub Environments for protection rules
- ✅ Review deployment logs regularly

### ❌ DON'T

- ❌ Commit SSH keys to repository
- ❌ Share SSH keys between environments
- ❌ Use root user without key authentication
- ❌ Disable host key verification
- ❌ Commit API keys or secrets to `.env` files

---

## 📊 Monitoring Deployments

### GitHub Actions Dashboard

**Live deployments:**
```
https://github.com/I-Dacosta/AquatiqTask/actions
```

**Recent runs:**
- ✅ Green checkmark = successful
- ❌ Red X = failed
- 🟡 Yellow dot = in progress

### Email Notifications

GitHub sends emails for:
- ❌ Failed deployments
- ✅ First successful deployment after failures

**Configure:**
1. Go to: https://github.com/settings/notifications
2. Enable "Actions" notifications

### Slack/Discord Notifications (Optional)

Add to workflow for team notifications:
```yaml
- name: 📢 Notify team
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🎯 Advanced Configuration

### Environment Protection Rules

Add manual approval for production:

1. Go to: https://github.com/I-Dacosta/AquatiqTask/settings/environments
2. Click **"New environment"** → Name: `production`
3. Enable **"Required reviewers"** → Add yourself
4. Click **"Save protection rules"**

Now deployments will wait for manual approval! 🛡️

### Deploy Specific Branch

Modify workflow to deploy other branches:

```yaml
on:
  push:
    branches:
      - main
      - staging  # Add staging branch
```

### Rollback on Failure

Add automatic rollback:

```yaml
- name: 🔙 Rollback on failure
  if: failure()
  run: |
    ssh root@31.97.38.31 << 'EOF'
      cd /opt/TaskPriority
      git reset --hard HEAD~1
      docker compose -f docker-compose-ip.yml up -d
    EOF
```

---

## 📝 Summary Checklist

Before pushing your first automated deployment:

- [ ] SSH private key copied
- [ ] `HOSTINGER_SSH_KEY` secret added to GitHub
- [ ] GitHub Actions enabled in repository settings
- [ ] Test manual workflow run successful
- [ ] Health checks passing
- [ ] Email notifications configured

---

## 🆘 Getting Help

**Workflow failed?**
1. Check: https://github.com/I-Dacosta/AquatiqTask/actions
2. Click on the failed run
3. Expand the failing step
4. Look for error message

**Still stuck?**
1. SSH to VPS: `ssh root@31.97.38.31`
2. Check logs: `cd /opt/TaskPriority && docker compose -f docker-compose-ip.yml logs`
3. Verify services: `docker compose -f docker-compose-ip.yml ps`

---

## 🎉 Success!

Once set up, you'll have:
- ✅ Automated deployments on every push
- ✅ Health checks ensuring stability
- ✅ Rollback capability if needed
- ✅ Deployment history and logs
- ✅ Zero-downtime updates

**Happy deploying!** 🚀
