# AWS DevOps Deployment & Handoff Guide

This repository contains an enterprise AI Governance-as-Code system configured for automated deployment to **AWS (Amazon Web Services)** using Docker containers, AWS ECR (Elastic Container Registry), AWS ECS (Elastic Container Service / Fargate), and GitHub Actions.

---

## 1. Prerequisites & Required AWS Resources

Before deploying, ensure the following AWS resources are created:

1. **AWS ECR Repositories**:
   - `aivar-backend`
   - `aivar-frontend`
2. **AWS IAM Roles**:
   - `ecsTaskExecutionRole` (with `AmazonECSTaskExecutionRolePolicy` attached, plus `SecretsManagerReadWrite` for reading API keys).
   - `ecsTaskRole` (optional, for accessing S3/DynamoDB if Supabase/Cloud storage is configured).
3. **AWS ECS Cluster**:
   - Cluster Name: `aivar-governance-cluster` (Fargate or EC2 launch type).
4. **AWS ECS Services**:
   - `aivar-backend-service` (target port `8000`)
   - `aivar-frontend-service` (target port `80`)
5. **AWS Secrets Manager**:
   - Store API keys securely: `aivar/groq_key`, `aivar/openai_key`, etc.

---

## 2. GitHub Secrets Configuration

Set the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions**):

| Secret Name | Description | Example / Note |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM User Key with ECR & ECS permissions | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | Target AWS Region | `us-east-1` |
| `AWS_ACCOUNT_ID` | 12-digit AWS Account ID | `123456789012` |

---

## 3. GitHub Environments & Promotion Pipeline Setup

In GitHub (**Settings > Environments**), create 3 environments:

1. `dev`:
   - Auto-deploys from pushes on `dev` or `develop` branches.
2. `staging`:
   - Deploys on merge to `staging` or `main` branches.
3. `production`:
   - **Environment Protection Rules**: Enable **Required reviewers**.
   - Add authorized Lead Engineers / DevOps Engineers as reviewers.
   - Requires explicit manual approval in GitHub Actions before deploying to production!

---

## 4. Manual AWS Deployment Commands (CLI Handoff)

If deploying manually from a local terminal or EC2 jumpbox:

```bash
# 1. Login to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# 2. Build Production Images
docker build -t aivar-backend ./backend
docker build -t aivar-frontend ./frontend

# 3. Tag Images for ECR
docker tag aivar-backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aivar-backend:latest
docker tag aivar-frontend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aivar-frontend:latest

# 4. Push to ECR
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aivar-backend:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aivar-frontend:latest

# 5. Update ECS Service
aws ecs update-service --cluster aivar-governance-cluster --service aivar-backend-service --force-new-deployment
aws ecs update-service --cluster aivar-governance-cluster --service aivar-frontend-service --force-new-deployment
```

---

## 5. Docker Compose Production Deployment (EC2 / Single Instance)

For single-instance AWS EC2 deployment using Docker Compose:

```bash
# Set environment secrets
export GROQ_API_KEY="your-groq-key"
export OPENAI_API_KEY="your-openai-key"

# Run production stack
docker-compose -f docker-compose.prod.yml up -d --build
```
