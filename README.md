# GitHub Trending Scout 🔥

Automated GitHub Trending report, delivered to Discord every day at **09:00 WIB**.

## Features
- Scrapes GitHub Trending (daily + weekly)
- Sends formatted Discord embeds with stars, descriptions, links
- Saves JSON report as GitHub Actions artifact (30-day retention)
- Manual trigger via `workflow_dispatch`

## Setup

### 1. Fork/Clone this repo

### 2. Add Discord Webhook Secret
Go to repo → Settings → Secrets → Actions → New:
- Name: `DISCORD_WEBHOOK_URL`
- Value: Your Discord webhook URL

### 3. Enable GitHub Actions
Go to repo → Actions → Enable workflows

### 4. Test
Actions → GitHub Trending Scout → Run workflow

## Schedule
| Time | Timezone | Cron |
|------|----------|------|
| 09:00 | WIB (UTC+7) | `0 2 * * *` |

## Manual Run
```
gh workflow run trending.yml
```

## Output
Discord embed with:
- 🔥 Top 15 daily trending repos
- 📈 Top 15 weekly trending repos
- Stars, descriptions, direct links
