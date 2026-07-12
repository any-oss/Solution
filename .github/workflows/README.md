# GitHub Actions Secrets Setup

This workflow requires Docker Hub credentials to be stored as GitHub Secrets.

## Required Secrets

Navigate to your repository settings: **Settings > Secrets and variables > Actions**

Add the following secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DOCKER_USER` | `docker_user` | Your Docker Hub username |
| `DOCKER_PASS` | `docker_pass` | Your Docker Hub password or access token |

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Enter the secret name and value
6. Click **Add secret**

## Workflow Triggers

The workflow will automatically run when:
- Code is pushed to the `main` branch
- A pull request is opened/updated against the `main` branch

## Docker Image Tags

The workflow automatically tags images with:
- Branch name (e.g., `main`, `feature-branch`)
- PR number (e.g., `pr-123`)
- Commit SHA
- `latest` tag (only for default branch)

## Manual Trigger (Optional)

To manually trigger the workflow:

1. Go to **Actions** tab in your repository
2. Select "Build and Push Docker Image" workflow
3. Click **Run workflow**
4. Select branch and click **Run workflow**
