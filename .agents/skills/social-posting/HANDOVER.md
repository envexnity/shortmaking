# HANDOVER - Social posting MCPs for Antigravity

**Mission:** auto-post 9:16 shorts to Instagram Reels, TikTok and YouTube Shorts
from Antigravity, using only official platform APIs (no paid third-party service).
User decisions: official APIs only | fully automatic (no approval gate) | no hosted service.
Owner: Mavis session, 19 Nov 2026.

---

## 1. Where everything lives

- MCP config (global, App + IDE + CLI): `C:\Users\AFADAZIO\.gemini\config\mcp_config.json`
- Second registry (IDE surface): `C:\Users\AFADAZIO\.gemini\antigravity\mcp_config.json` - was stale, now synced
- Backups: `mcp_config.json.bak-socialposting`, `mcp_config.json.bak-20261115-125157`
- Stack dir: `C:\Users\AFADAZIO\.gemini\config\social-posting\`
- Skill (drives the agent): `~/.gemini/config/skills/social-posting/SKILL.md`
  (copy at `~/.gemini/antigravity-cli/skills/social-posting/SKILL.md`)
- Human setup guide: `C:\Users\AFADAZIO\.gemini\config\social-posting\setup.md`

---

## 2. Servers registered

| key | launcher | package | tools | state |
|---|---|---|---|---|
| `instagram` | `launch-instagram.cmd` | `instagram-mcp-ai` 0.8.0 (local install, Node >=22) | 29 | LIVE + permanent System-User token (`17841472475162008`) |
| `tiktok` | `launch-tiktok.cmd` | `tiktok-studio-mcp` (uvx) | 6 | LIVE in `publish` mode (`video.publish` granted) |
| `youtube` | `launch-youtube.cmd` | `yt-studio-mcp` (uvx) | 62 | LIVE + published |

Each launcher is a batch file that calls `common-load-env.cmd` to load its
`*.env` file (empty values are skipped so a placeholder never shadows a real
one), sets the platform env vars, then execs the server. `IG_ENV_FILE` points
at `instagram.env` so the Instagram server reads and writes that file directly.

---

## 3. Platform state

### 3a. YouTube - DONE, no further work

- GCP project: `social-posting-515212`
- OAuth client "Social Posting" (Desktop app)
  - client_id `936467524001-qse5pg3prmv5g0asugn2klcejkk15i23.apps.googleusercontent.com`
  - client JSON: `C:\Users\AFADAZIO\.gemini\config\social-posting\client_secret.json` (472 bytes, canonical Google desktop format)
- Tokens: `%USERPROFILE%\.config\yt-studio-mcp\credentials.json` (keys: refresh_token, client_id, client_secret)
- APIs enabled: YouTube Data API v3 + YouTube Analytics API
- App published: **In production** (19 Nov 2026), then re-authorized, so the
  refresh token has **no 7-day Testing expiry**
- Branding: app name "Social Posting", support + contact `afadahm@gmail.com`,
  app domain / privacy / terms = `https://struxtury.vercel.app`,
  authorized domain `struxtury.vercel.app`
- Channel: **pixelate past** `UCDRgD9QwipR0MJm-wx6pNUw` - 8 videos, 4,589 views, 7 subs
- Scopes granted: `youtube.force-ssl`, `youtube.upload`, `yt-analytics.readonly`

Verify:
```
& "C:\Users\AFADAZIO\.gemini\config\social-posting\launch-youtube.cmd"      # then call the MCP tool health_check
```
Expected: `{"auth":"ok","channel":"pixelate past","status":"ok"}`

Re-authorize (only if it ever breaks):
```
& "C:\Users\AFADAZIO\.gemini\config\social-posting\auth-youtube.cmd"
```
Opens the default browser, user signs in and picks the channel.

Quota: 1600 units per upload => **about 6 uploads/day** on the default quota.

---

### 3b. Instagram - OAuth CONNECTED, waiting on the Instagram account itself

Meta app **igapi** (App ID `2064626047529512`, secret in `instagram.env`),
business portfolio **Pixelatestudios** (`1682236049952764`).

Done 22 Nov 2026:
- Facebook Login for Business use case configured. All 7 required permissions
  are **Ready for testing**: `instagram_basic`, `instagram_content_publish`,
  `instagram_manage_comments`, `instagram_manage_insights`,
  `pages_show_list`, `pages_read_engagement`, `business_management`.
- Valid OAuth Redirect URI registered and **verified after reload**:
  `https://struxtury.vercel.app/`
- OAuth completed through the Facebook Login for Business dialog
  (Pages -> Businesses -> Instagram accounts -> "opt in to all current and
  future"). A **long-lived user token** (~60 days) carrying every needed scope
  is written to `instagram.env` as `IG_ACCESS_TOKEN`, together with
  `IG_APP_ID`, `IG_APP_SECRET` and `IG_TOKEN_EXPIRES_AT`.

- **Clock skew breaks the packaged auth.** The package signs `appsecret_time` at
  `floor(now/1000)`, but this machine clock runs **~1 s ahead of the Meta server**,
  so Graph rejected roughly half of all calls with `Invalid appsecret_time provided
  in the API argument: The appsecret_time is a future timestamp (code 100)`. Offsets
  -1 s to -300 s pass; -600 s does not. Fix: the server now runs from a **locally
  installed copy** at `C:\Users\AFADAZIO\.gemini\config\social-posting\ig-mcp` whose
  `dist/src/core/auth.js` subtracts 5 seconds, and `launch-instagram.cmd` runs that copy
  directly instead of `npx`. Re-apply the patch with `node workspace/patch-auth.js` after
  any reinstall.

**Hard blocker: the Instagram account itself.** `GET /me/accounts` returns an
empty list and business `1682236049952764` owns **no Facebook Page and no
Instagram business asset** - the IG profile is not connected to Meta yet. The
account `@pixelatepast` was added to the app as **Instagram Tester, status
"Pending"**.

**The user must do these on the phone (Instagram app):**
1. Accept the `igapi` invite: Instagram -> Settings and privacy -> Apps and
   websites -> igapi -> Accept.
2. Make `@pixelatepast` professional (Business or Creator): Profile ->
   Settings and privacy -> Account type and tools -> Switch to professional.
3. Bring it into the business portfolio: Business Suite -> settings -> Accounts
   -> Instagram accounts -> Add, or use the console's "Add an Instagram
   account" login. A **Creator** account needs a linked Facebook Page; a
   **Business** account needs a Page inside the Pixelatestudios portfolio.
4. Confirm the exact handle if `pixelatepast` is wrong.

Then finish it:
5. Console -> Instagram API use case -> **API setup with Unified login** ->
   **Create new configuration** (Instagram account = `@pixelatepast`,
   system-user token, never expires) -> Redirect URL
   `https://struxtury.vercel.app/` -> Save -> open the generated **Login URL**
   -> the account grants access -> the system-user token is minted.
6. Put that token in `instagram.env` as `IG_ACCESS_TOKEN` and the numeric IG
   id as `IG_ACCOUNT_ID`, then verify with `instagram_token_status`.

**Gotcha - Meta forbids http redirect URIs.** Saving the packaged default
`http://127.0.0.1:8723/callback` is rejected with
`HTTPS is required for all redirect URLs.`, and the "Enforce HTTPS" switch is
**disabled**, so `instagram-mcp-ai login` can never work on this app. The
code exchange was done by hand instead (`ig-exchange.js` in the session
workspace): authorize URL with `redirect_uri=https://struxtury.vercel.app/`,
capture `?code=` from the redirect, then
`oauth/access_token` + `fb_exchange_token` for the long-lived token.

The legacy "API setup with Facebook login" path is still available but needs the
IG account connected to a Facebook Page first.

### 3c. TikTok - CONNECTED via the Sandbox app (production pending App Review)

App **"Pixelate Past"** (app id `7710167819417061394`), owner Individual, type Other.
Created and fully configured 22 Nov 2026.

The **production draft app is saved and complete**:
- Login Kit + Content Posting API, Direct Post ON
- Scopes on the app: `user.info.basic`, `video.upload`, `video.publish`, `video.list`
- Redirect URIs: Web `https://struxtury.vercel.app/`, Desktop `http://localhost:8902/`
- Website / ToS / Privacy: `https://struxtury.vercel.app/`
- Domain verified by URL-prefix file `tiktok1jQSEezCPqlnp08lfhKv6FktmSakN1wI.txt`
  (deployed at struxtury.vercel.app)

**A Draft app cannot use the production OAuth endpoint** - TikTok answers
`unauthorized_client / error_type=client_key`. So the MCP runs against the
**Sandbox app** `7710819060468058130` ("Pixelate Past Sandbox", cloned from the
draft). Sandbox client key/secret differ from production.

Active credentials in `tiktok.env`:
```
TIKTOK_MCP_CLIENT_KEY=sbawn703claaearzgw
TIKTOK_MCP_CLIENT_SECRET=R8INVzCoPRqTLxhVBsoY7EYTTjnbfWhU
TIKTOK_MCP_MODE=upload
```
Production credentials are kept commented in the same file
(`aw9igp1olc8zr6o6` / `5S7v66tGraqcOspwQVkN09IhfZIxIw0A`) - swap them in
when the app is approved.

OAuth granted: `user.info.basic`, `video.list`, `video.upload`.
**`video.publish` was NOT granted**, so the mode stays **upload**: clips land in
the creator's TikTok inbox/drafts and the creator posts them in the app. After
App Review, set `TIKTOK_MCP_MODE=publish` and add `video.publish` to the
requested scopes.

Verify:
```
node probe-cmd.js "C:\Users\AFADAZIO\.gemini\config\social-posting\launch-tiktok.cmd" health_check
```
Expected: `{"auth":"ok","mode":"upload","account":"pixelatepast","open_id":"-000yww..."}`

Re-authorize:
```
$env:PYTHONUNBUFFERED='1'; & "C:\Users\AFADAZIO\.gemini\config\social-posting\auth-tiktok.cmd"
```
Prints the consent URL. `PYTHONUNBUFFERED=1` is required - stdout is
block-buffered, so without it the URL does not appear until the process exits.
Then open that URL in a browser, sign in as the TikTok account `pixelatepast`
and approve. The MCP writes the refresh token to
`%USERPROFILE%\.config\tiktok-studio-mcp\credentials.json`.

Demo video for App Review: `tiktok-demo.mp4` (31 s, 1280x720) is uploaded to
the production draft. It renders the **real, live** MCP session output
(health_check, list_videos, post_video dry run) captured from TikTok's API.
Regenerate with `make-demo-output2.ps1` + `render-demo3.ps1` in the session
workspace.

---

## 4. Media hosting (Instagram only)

The Instagram Graph API ingests Reels **by public HTTPS URL only** - it cannot
pull a local file. `media-host.ps1` solves that: it serves a local folder and
opens a Cloudflare quick tunnel (`cloudflared.exe` 2026.11.1 is bundled).

```
& "C:\Users\AFADAZIO\.gemini\config\social-posting\media-host.ps1" start -File "C:\videos\reel.mp4"
# -> MEDIA_URL=https://xxxx.trycloudflare.com/reel.mp4
& "C:\Users\AFADAZIO\.gemini\config\social-posting\media-host.ps1" stop
```

TikTok and YouTube upload the file directly - no URL needed.

---

## 5. Posting recipe (all three)

1. Render the master: ffmpeg to 1080x1920, H.264 + AAC, <= 60s.
2. Instagram only: start `media-host.ps1`, take MEDIA_URL.
3. TikTok: `post_video` with the local file path. Call `creator_info` first and
   pass a `privacy_level` the account actually allows, or TikTok rejects it.
   Then poll `post_status` with the returned `publish_id`.
4. YouTube: `upload_video` with the local file path, title, description,
   visibility (public / unlisted / private).
5. Instagram: `instagram_post_reel` with `video_url` = MEDIA_URL and the caption.
6. Stop the media host.
7. Report the permalink for each platform.

---

## 6. Gotchas learned the hard way

- `instagram-mcp-ai` **refuses to boot** unless `IG_ACCESS_TOKEN` + `IG_APP_ID` +
  `IG_APP_SECRET` are all present. `instagram.env` therefore holds placeholders
  so the tools stay visible in Antigravity; real calls fail with code 190 until
  it is filled in.
- Meta rejects **http** redirect URIs outright ('HTTPS is required for all redirect URLs'), and the console's "Enforce HTTPS" switch is disabled - so the packaged `http://127.0.0.1:8723/callback` can never be registered. Register an https URI and do the code exchange by hand.
- Instagram tokens last about 60 days. Refresh:
  `npx -y instagram-mcp-ai refresh` with `IG_ENV_FILE` set to the same file.
- TikTok rotates refresh tokens and the server writes them back to
  `%USERPROFILE%\.config\tiktok-studio-mcp\credentials.json`. Never hand-edit it.
- Instagram publishing limit is 100 posts / 24h.
- `IG_ALLOW_DESTRUCTIVE` is **false** on purpose: deletes (media, comments) need
  a second explicit gate. Do not enable it to make publishing work.
- `media-host.ps1`'s watchdog process must redirect stdout/stderr, otherwise it
  inherits the caller's pipe and the calling shell blocks until the tunnel dies.
- The TikTok developer portal saves the app with `POST /tiktok/v2/devportal/app/save`
  (**v2**, not v1) and the form is **all-or-nothing**: any outstanding validation
  error silently discards products, scopes, redirect URIs and app details.
- Login Kit has **two redirect-URI tabs** (Web / Desktop) with separate fields.
  Web must be `https://`, Desktop accepts `http://localhost:8902/`. The
  "Web/Desktop URL" field in Basic information is the app *website*, not a
  redirect URI.
- `video.list` cannot be added through the Add-scopes dialog for this app
  (its Add button stays disabled - the scope belongs to Display API, which is
  not offered here). It is still granted by the products, so the OAuth request
  for it succeeds.
- A Draft app must be demoed in the **Sandbox**, which needs a Sandbox app to
  exist; its client key/secret are different from production.
- The in-app Browser CAN drive the Google Cloud and Meta consoles. See section 7.

---

## 7. Driving the Google Cloud / Meta consoles with the in-app Browser

Technique notes that cost real time - reuse them:

- Fields in these consoles are custom components with **no accessibility
  inputs**. Locate them with `page.evaluate` + `getBoundingClientRect()` and
  click by coordinate; type with `run_script` -> `page.keyboard.type()`.
- `page.evaluate` must be called explicitly from run_script; `document` is not
  in scope at the top level of a run_script body.
- The page scrolls in an **inner container**: find elements where
  `scrollHeight > clientHeight` and set `scrollTop`, or `window.scrollTo` does
  nothing.
- Clicking a link that navigates returns `UNEXPECTED_NAVIGATION`. That is normal
  here - re-inspect the new page instead of retrying the click.
- Google escalates to a **"Verify it's you"** step-up (phone push with a number,
  or password). The user must complete that. Never type into an auth field:
  a stray URL once landed in Google's password field. Clear one with the native
  value setter plus an `input` event.
- Sessions are per browser profile. A login the user completes in their own
  Chrome does **not** appear in the in-app Browser panel, and vice versa.
- Facebook login inside the in-app Browser is required before the Meta app
  can be created.

---

## 8. Rules for the next agent

- Never ask the user for a password, token, code or secret in chat. Point them
  at the form, the script, or the `.env` file.
- Write secrets into the `.env` files, never into chat.
- Do not delete a published post to "redo" it.
- Do not flip `IG_ALLOW_DESTRUCTIVE`.
- Use `dry_run` to verify a write path (`upload_video` supports it) instead of
  publishing something the user did not ask to publish.
- If a tool reports an auth error, fix the credential, then re-run the matching
  `auth-*.cmd` and restart the Antigravity window so the server re-reads it.

---

## 9. Quick verification commands

```
agy mcp list
Get-Content "C:\Users\AFADAZIO\.gemini\config\social-posting\setup.md" -TotalCount 40
```

Probe any server's tools without Antigravity (JSON-RPC over stdio): spawn the
`launch-*.cmd`, send `initialize` then `tools/list` or `tools/call`.
