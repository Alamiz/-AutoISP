# Auto-Update Guide (Windows / NSIS)

How AutoISP Desktop checks for, downloads, and installs updates via GitHub Releases.

---

## How It Works

1. **On launch** (5 s after the main window opens) and **every 6 hours**, the app silently checks GitHub Releases for a newer version.
2. If an update is available, a **badge** and **"Download update"** button appear in the sidebar footer; a toast is shown.
3. The user clicks **Download** → a progress bar appears in the sidebar.
4. Once downloaded, **"Install update"** is shown. Clicking it opens a confirmation dialog warning that the app will close and automations will stop.
5. On confirm, the backend process is terminated, and the NSIS installer runs.

> **Key settings**: `autoDownload = false`, `autoInstallOnAppQuit = false` — the user is always in control.

---

## Tagging a Release

```bash
# 1. Bump version in package.json (must match the tag!)
npm version patch          # or minor / major

# 2. Push the commit and tag
git push origin main --tags
```

The CI workflow (below) triggers on `v*` tags and publishes the NSIS installer as a GitHub Release.

---

## GitHub Configuration Checklist

### 1. Personal Access Token

| Step | Detail |
|------|--------|
| Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)** | |
| Click **Generate new token (classic)** | |
| Name: `autoisp-release` | |
| Scope: **`repo`** (full control of private repos) | |
| Copy the token — you'll need it next | |

### 2. Repository Secret

1. Go to your repo **Settings → Secrets and variables → Actions**.
2. Click **New repository secret**.
3. Name: `GH_TOKEN`
4. Value: paste the PAT from step 1.

### 3. GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

jobs:
  build:
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # ── Backend ──────────────────────────────────
      - name: Install backend dependencies
        working-directory: light-engine
        run: |
          python -m venv venv
          venv\Scripts\pip install -r requirements.txt
          venv\Scripts\pip install pyinstaller

      - name: Build backend
        working-directory: light-engine
        run: venv\Scripts\pyinstaller --clean api.spec

      # ── Frontend + Electron ──────────────────────
      - name: Install frontend dependencies
        working-directory: frontend-client
        run: npm ci

      - name: Build & Publish
        working-directory: frontend-client
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
        run: |
          npm run build
          npm run build-electron
          npx electron-builder --publish always
```

### 4. Ensure Releases Are Published (Not Draft)

`electron-updater` looks for the **latest published release** by default. If your releases end up as drafts, the updater won't find them.

In `electron-builder` config, do **not** set `"releaseType": "draft"`. The default (`"release"`) is correct.

### 5. Version Must Be Bumped

Each release **must** have a higher semver version than the previous one. The version is read from `frontend-client/package.json` → `"version"`.

---

## Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| "No published versions" / 406 error | The release has a grey **Draft** badge → click ✏️ Edit on the release and click **Publish release** |
| "HttpError: 401" in logs | `GH_TOKEN` is missing, expired, or lacks `repo` scope |
| Update check never fires | In dev mode, `electron-updater` can't find artifacts. Build with `npm run dist` and test the installed app |
| Download hangs at 0% | Firewall/proxy blocking `github.com` or `objects.githubusercontent.com` |
| "Cannot find latest.yml" | The artifact wasn't published. Re-run CI or manually upload `latest.yml` alongside the `.exe` |
| Wrong version detected | `package.json` version wasn't bumped before building |
| Backend not killed before update | Check `electron-log` file (default: `%APPDATA%/frontend/logs/main.log`) for kill errors |

---

## Log Files

Electron-updater logs go through `electron-log`:

```
%APPDATA%\frontend\logs\main.log
```

Open this file to debug update issues.
