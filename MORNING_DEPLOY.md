# Deploy CalSync in the Morning — 5 Minutes

## Step 1: Grant DO access to the new repo (2 mins)
1. Go to: https://github.com/settings/installations
2. Click "Configure" next to DigitalOcean
3. Under "Repository access" → add `C0n0r92/calsync-api`
4. Click Save

## Step 2: Deploy to DO (1 min)
Run this:
```bash
cd ~/calsync-api && doctl apps create --spec .do/app.yaml
```

## Step 3: Get the live URL (1 min)
```bash
doctl apps list | grep calsync
```
Copy the URL — it'll look like: `https://calsync-api-xxxxx.ondigitalocean.app`

## Step 4: Update the Bubble plugin JS (1 min)
In `~/calsync-api/bubble-plugin/action1.js` — the URL is already set to 
`https://calsync.playerdatainsights.com` but update to the DO URL until 
you set up the subdomain.

## Step 5: Add subdomain (optional, later)
In your DO DNS settings add:
- Type: CNAME
- Hostname: calsync
- Value: your-app.ondigitalocean.app

That gives you `calsync.playerdatainsights.com`

---

## Everything else is done ✅
- API: fully built and tested (10/10 tests pass)
- Repo: https://github.com/C0n0r92/calsync-api (public)
- Bubble plugin JS: ~/calsync-api/bubble-plugin/action1.js (ready to paste)
- player-predictions: untouched, still live
