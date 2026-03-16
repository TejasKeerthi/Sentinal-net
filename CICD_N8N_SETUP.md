# CI/CD + n8n Automation Setup

This project now includes:
- GitHub CI pipeline for frontend and backend checks.
- GitHub Pages deploy pipeline with optional n8n notification.
- Importable n8n workflow for deployment success/failure automation.

## Files Added/Updated
- .github/workflows/ci.yml
- .github/workflows/deploy.yml
- automation/n8n/sentinel-cicd-automation.json

## 1) Configure GitHub Secret
Set this repository secret in GitHub:
- Name: N8N_WEBHOOK_URL
- Value: your n8n production webhook URL

GitHub path:
- Settings -> Secrets and variables -> Actions -> New repository secret

## 2) Import n8n Workflow
In n8n:
1. Open Workflows.
2. Click Import from file.
3. Select automation/n8n/sentinel-cicd-automation.json.
4. Save workflow.
5. Set workflow to Active.
6. Copy the Production webhook URL from the GitHub Deploy Webhook node.

The webhook path in the template is:
- sentinel-cicd

## 3) Connect GitHub to n8n
Paste the n8n production webhook URL into GitHub secret N8N_WEBHOOK_URL.

The deploy workflow sends payload fields:
- event
- status
- buildStatus
- deployStatus
- repository
- branch
- commitSha
- actor
- pageUrl
- runId
- runNumber
- runAttempt
- runUrl

## 4) Optional Next Automation Steps in n8n
After the Deployment Success? node, you can add:
- Slack node for notifications
- Email node for alerts
- Jira node for incident ticket creation on failures
- HTTP Request node to trigger downstream systems

## 5) Trigger
On push to main:
1. CI workflow runs lint/build/syntax checks.
2. Deploy workflow publishes to GitHub Pages.
3. deploy.yml sends deployment result to n8n webhook when secret is set.
