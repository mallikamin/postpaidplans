# postpaidplans.com — Index

The wikipedia of this project. Read me first.

## What this project is

`postpaidplans.com` — a tool-led Etisalat postpaid-plan site for the UAE. Core differentiator: an **interactive Plan Finder** (recommends a plan from budget + primary need) + a filterable comparison table of all 11 current Etisalat plans. Authorized Etisalat Dealer positioning, Etisalat-only. Conversion via WhatsApp + the reused `/choose-number/` picker.

Created 2026-05-25 as the third site in the family, deliberately **distinct in angle** from `uaepremiumnumbers.com` (catalog) and `goldennummbers.com` (numbers) to avoid duplicate-content cannibalization.

## Quick links
- Entry point: `index.html` (English homepage + Plan Finder)
- Arabic: `ar/index.html`
- Number picker (reused): `choose-number/index.html`
- Deploy config: `wrangler.toml`, `worker.js`
- SEO: `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, IndexNow key `7ca1a2e6bf1196e5d1a2582f53300947.txt`
- Project rules: `CLAUDE.md`

## Architecture (verified 2026-05-25)
- Pure static HTML/CSS/JS, all inline per page (no build step, no framework).
- Theme: **light / Etisalat-red** (`--red:#E30613`, gold accents) — intentionally distinct from the dark-gold sister sites.
- Deploy: Cloudflare "Workers with Static Assets" (`wrangler.toml` + `worker.js`), connected to GitHub `mallikamin/postpaidplans`. DNS GoDaddy → Cloudflare.
- WhatsApp: `971569028087` (all WA links). `tel:` voice line: `+971566999377`.
- `/choose-number/` reused verbatim from uaepremiumnumbers (same SHEETS inventory + PARTNER_API); only domain/branding swapped.
- Tracking: GA4 + Meta Pixel + GSC are PLACEHOLDERS pending real IDs.

## Current status (2026-05-25 — LIVE)
- ✅ **Site is LIVE** at https://postpaidplans.com (+ www), valid SSL, deployed via Cloudflare Worker connected to repo `mallikamin/postpaidplans` (push = auto-deploy).
- ✅ Steps 1–3 done + verified: DNS cutover (GoDaddy→Cloudflare NS daisy/vick), Worker deploy, custom domains + SSL, `.assetsignore` security fix, AI-bot block + Cloudflare robots.txt injection both disabled.
- ⏳ **ONLY Step 4 remains**: paste real GA4 (`__GA4_PLACEHOLDER__`) + Meta Pixel (`__FB_PIXEL_PLACEHOLDER__`) IDs into index.html/ar/choose-number → push; then GSC Domain-property (DNS TXT) + submit sitemap; Bing/IndexNow.
- 📋 Full resume detail: `PAUSE_CHECKPOINT_2026-05-25.md` (project root). Known issues: `ERROR_LOG.md`.

## People involved
- Malik Amin (owner)
- Bilal Khalid (UAE partner)

## Reference material
| Date | File | Purpose |
|------|------|---------|
| 2026-05-25 | `screenshots/2026-05-25_godaddy-cloudflare-nameservers.png` | GoDaddy confirming custom NS = daisy/vick.ns.cloudflare.com (Step 1 DNS cutover). Verified propagated at 1.1.1.1 + 8.8.8.8 same day. |

## Pending decisions / open questions
- Phase 2: fresh plan-detail pages, blog, location pages (must be distinct copy, not cloned from sisters).
- ~~Decide whether to generate per-number SEO pages~~ → **DONE 2026-05-25** (owner-approved): built ~3,322 `/numbers/etisalat-<digits>/` pages via `generate_number_pages.py` with a **distinct plan-pairing angle** (not cloned) to manage duplicate-content risk. Hub `/numbers/`, `sitemap-numbers.xml` + `sitemap-index.xml`, IndexNow-submitted. **Remaining: submit `sitemap-index.xml` in Google Search Console once GSC is set up.**
- New OG image with postpaidplans branding (currently reuses sister og-image.png).
