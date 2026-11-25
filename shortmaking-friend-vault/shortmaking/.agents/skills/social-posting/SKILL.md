---
name: social-posting
description: |
  Publish a finished video to Instagram Reels, TikTok and YouTube Shorts through the
  official platform APIs. Use when the user says "upload", "post this", "publish this reel",
  "post to TikTok / Instagram / YouTube", "upload a Short", or asks to push a
  rendered vertical video to their socials. ALWAYS uploads to ALL 3 configured platforms
  (YouTube Shorts, TikTok, Instagram Reels) by default unless explicitly restricted.
---

# Social Posting (IG Reels / TikTok / YT Shorts)

Three MCP servers are already wired into Antigravity, all on the official APIs:

| Server   | Package                | Publish tool |
|----------|------------------------|--------------|
| `instagram` | `instagram-mcp-ai`  | `instagram_post_reel` |
| `tiktok`    | `tiktok-studio-mcp` | `post_video` |
| `youtube`   | `yt-studio-mcp`     | `upload_video` |

## CURRENT STATE (22 Nov 2026)

- **youtube**: authorized + published, channel "pixelate past" - WORKS NOW
- **instagram**: authorized + connected via Unified Login (`config_id=1652315386908447`) with a permanent System-User token (`expiresAt=0`) and `IG_ACCOUNT_ID=17841472475162008` (`@pixelatepast`, 100/100 daily Reels quota) - WORKS NOW
- **tiktok**: authorized with `video.publish` (`TIKTOK_MCP_MODE=publish`, Direct Post endpoint `/v2/post/publish/video/init/`, `@pixelatepast`) - WORKS NOW (Sandbox/unaudited Direct Post publishes directly to `@pixelatepast` with `privacy_level="SELF_ONLY"`; after App Review, `PUBLIC_TO_EVERYONE` becomes available)

Full context, exact steps and gotchas: `HANDOVER.md` next to this file.
---

## Post to all three

1. **Master file.** Use a 9:16 vertical MP4, H.264 + AAC, 1080x1920, under 60s
   for Shorts/Reels, under 10 min for TikTok. Render with ffmpeg:
   `ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k out_vertical.mp4`

2. **Public URL (Instagram only).** Instagram ingests Reels by public HTTPS URL
   and cannot pull a local file. Start the tunnel first:
   `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\AFADAZIO\.gemini\config\social-posting\media-host.ps1" start -File "<master.mp4>"`
   It prints `MEDIA_URL=...` and also writes it to
   `C:\Users\AFADAZIO\.gemini\config\social-posting\last-media-url.txt`.
   Keep it running until the Instagram publish finishes, then:
   `... media-host.ps1 stop`

3. **TikTok** — `post_video` with the local file path, `caption`, and `privacy_level="SELF_ONLY"` (or call `creator_info` first), then check `post_status`
   with the returned `publish_id`. `TIKTOK_MCP_MODE=publish` is active with `video.publish` granted, so videos publish directly without landing in inbox/drafts.

4. **YouTube** — `upload_video` with the local file path, `title`,
   `description`, and `visibility` (public/unlisted/private). For a Short,
   keep it vertical and under 60s.

5. **Instagram** — `instagram_post_reel` with `video_url` = the MEDIA_URL and
   the caption. Reels are transcoded by Meta and can take a few minutes; the
   tool waits on the container for you.

## Rules

- Post the same caption idea adapted per platform, not word-for-word identical.
- Never delete a published post to "redo" it. IG deletes need
  `IG_ALLOW_DESTRUCTIVE=true`, which is off by design.
- If one platform fails, report which one and why, and keep the other two live.
- After posting, state the permalink for each platform.

## Credential problems

| Platform | State | If it breaks |
|---|---|---|
| youtube | authorized + published (no token expiry), channel "pixelate past" | re-run `auth-youtube.cmd`, then restart the Antigravity window |
| instagram | authorized + live (`IG_ACCOUNT_ID=17841472475162008`, permanent System-User token from Unified Login `config_id=1652315386908447`) | re-run Unified Login OAuth (`config_id=1652315386908447`) + `ig-exchange.js` and keep `IG_ACCOUNT_ID=17841472475162008` |
| tiktok | authorized + live in `publish` mode (`user.info.basic,video.publish,video.list,video.upload` granted on Sandbox app) | re-run `auth-tiktok.cmd` with `PYTHONUNBUFFERED=1` (`TIKTOK_MCP_SCOPES` is in `tiktok.env`), open the printed URL, approve as `pixelatepast` |

The YouTube OAuth app is published (In production) as of 19 Nov 2026 and was
re-authorized, so its refresh token does not expire weekly.

The Instagram server runs from a locally patched copy of `instagram-mcp-ai` (the packaged `appsecret_time` is signed against a clock that runs ~1 s ahead of Meta's). If `launch-instagram.cmd` is ever changed back to `npx`, re-apply the patch with `node workspace/patch-auth.js` first.

Setup details: `C:\Users\AFADAZIO\.gemini\config\social-posting\setup.md`
