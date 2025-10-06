# GitHub Actions Workflows

## Hostinger Deployment

The `hostinger-deploy.yml` workflow automatically deploys the PrioritiAI stack to your Hostinger VPS when changes are pushed to the `main` branch.

### Setup Instructions

#### 1. Generate SSH Key for Deployment

On your local machine or CI environment:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/hostinger_deploy_key -N ""
```

This creates two files:
- `~/.ssh/hostinger_deploy_key` (private key - add to GitHub Secrets)
- `~/.ssh/hostinger_deploy_key.pub` (public key - add to Hostinger VPS)

#### 2. Configure Hostinger VPS

SSH into your Hostinger VPS and add the public key:

```bash
ssh root@your-vps-ip

# Add the public key to authorized_keys
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### 3. Configure GitHub Repository Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add the following **Repository Secrets**:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `HOSTINGER_HOST` | `your-vps-ip` or `vps.yourdomain.com` | VPS hostname or IP |
| `HOSTINGER_USER` | `root` or deployment user | SSH user for VPS |
| `HOSTINGER_SSH_KEY` | Contents of `~/.ssh/hostinger_deploy_key` | Private SSH key (entire file content) |

Add the following **Repository Variables** (optional overrides):

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `HOSTINGER_REPO_DIR` | `/opt/TaskPriority` | Directory on VPS where repo is cloned |
| `HOSTINGER_ENV_FILE` | `/opt/TaskPriority/.env.production` | Path to production env file on VPS |

#### 4. Prepare VPS Environment File

Before first deployment, SSH into your VPS and create the `.env.production` file:

```bash
ssh root@your-vps-ip
cd /opt
git clone https://github.com/I-Dacosta/AquatiqTask.git TaskPriority
cd TaskPriority

# Create environment file from example
cp .env.production.example .env.production
nano .env.production
```

Fill in all required values:
```bash
POSTGRES_PASSWORD=YourStrongPasswordHere123!
SSL_EMAIL=your-email@example.com
DOMAIN_NAME=yourdomain.com
OPENAI_API_KEY=sk-proj-your-actual-key
```

#### 5. Test Deployment

Push to main branch or manually trigger:

```bash
git push origin main
```

Or manually trigger from GitHub:
- Go to Actions → Deploy to Hostinger → Run workflow

### Workflow Behavior

- **Automatic**: Runs on every push to `main` branch
- **Manual**: Can be triggered via GitHub Actions UI with custom branch selection
- **Process**:
  1. Checks out code
  2. Uploads deployment script to VPS
  3. Executes script on VPS (pulls latest code, rebuilds containers)
  4. Waits 30s and runs health check
  5. Reports success or failure

### Troubleshooting

#### SSH Connection Issues

```bash
# Test SSH connection locally
ssh -i ~/.ssh/hostinger_deploy_key root@your-vps-ip

# View GitHub Actions logs for detailed error messages
```

#### Deployment Script Errors

SSH into VPS and check Docker logs:

```bash
cd /opt/TaskPriority
docker compose -f docker-compose-prod.yml logs --tail=50
```

#### Health Check Failures

Check if services are running:

```bash
docker compose -f docker-compose-prod.yml ps
docker compose -f docker-compose-prod.yml logs ai-prioritization
```

### Security Notes

- Never commit the private SSH key to the repository
- Use separate deployment keys (not your personal SSH key)
- Consider creating a dedicated deployment user on VPS with limited sudo access
- Rotate SSH keys periodically
- Store sensitive values in GitHub Secrets, not in the workflow file
