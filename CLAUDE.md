# Claude — Project Instructions (postpaidplans)

**Read `_context/INDEX.md` first.** It is the wikipedia of this project.

## What this is

`postpaidplans.com` — a **tool-led** Etisalat postpaid-plan site. The differentiator vs the sister sites is an **interactive Plan Finder** (recommends a plan from budget + need) plus a side-by-side comparison table. Positioned as an **Authorized Etisalat Dealer**.

**Du-rule — UPDATED 2026-06-14 (owner decision, supersedes the old "never write Du" rule):** PPP MAY now publish honest **du-vs-e& comparison** content — this is goldennummbers' single biggest traffic engine (5,800+ impr EN+AR) and the GSC benchmark proved the demand. Du may be named **as a competitor, for comparison purposes only**, with every comparison concluding from the Authorized Etisalat Dealer point of view (Etisalat as the recommended choice). Outside comparison content, stay Etisalat-first: do not promote Du, sell Du products, or use Du hashtags. The exact-match domain advantage is on "postpaid plans" — comparison content is additive, not a pivot away from the plan-finder angle.

## Sister sites (coordinate, don't duplicate)
- `goldennummbers.com` — numbers-led, Etisalat-positioned (`C:\Users\Malik\desktop\etisalat-shop`)
- `uaepremiumnumbers.com` — plan-led catalog (`C:\ST\Sitara Infotech\uae-premium-numbers`)
- `postpaidplans.com` (this) — **plan-FINDER / calculator angle.** Keep copy + titles distinct from uaepremiumnumbers to avoid duplicate-content cannibalization. Do NOT clone the location pages from the sisters.

### ⛔ Per-number pages — REMOVED 2026-08-09 (owner directive). DO NOT REBUILD.
- The `/numbers/etisalat-<digits>/` tree (3,680 pages), the `/numbers/` hub, `sitemap-numbers.xml`, and the `generate_number_pages.py` generator were **all deleted**. They existed 2026-05-25 → 2026-08-09.
- **Why:** the same mass-generated per-number page pattern **drew a penalty on the sister site goldennummbers**. On PPP the tree never earned a click (GSC 3 mo to 2026-08-09: ~2-3 impressions per page, **0 clicks**) while producing 425 of the 640 "not indexed" URLs. The June 2026 mitigation (`noindex` all but the top-100) reduced the bloat but did not make the pages earn anything.
- **URLs now return `410 Gone`** via `worker.js` (`isRemovedNumberPage()`), which de-indexes faster than a 404. **Keep that rule permanently.**
- **Do NOT add `Disallow: /numbers/` to robots.txt** — a blocked crawler can never see the 410, so the URLs would stay indexed forever. See the note in `robots.txt`.
- **Do not propose per-number / per-SKU mass page generation for this site again.** Number inventory is served by the interactive `/choose-number/` tool, which is the supported surface. If mass pages are ever reconsidered, it needs an explicit owner decision that overrides this line.

## Shared backend (reused, keep identical)
- WhatsApp / phone number: **`971569028087`** (the 8087 line) for ALL links — WhatsApp *and* `tel:` voice. **The old 9377 voice line (`+971566999377`) was retired 2026-07-18 (Malik) and must not be reintroduced anywhere.** (Superseded the earlier "keep the tel: voice line as 9377" rule.)
- `/choose-number/` — the number picker is reused verbatim from uaepremiumnumbers; same Google Sheets inventory + `PARTNER_API` Apps Script. Only domain/canonical/branding were swapped. **Stays functionally the same.**
- Google Sheets inventory (SHEETS array in choose-number) is shared across all three sites.

## Tracking
- GA4 + Meta Pixel are **placeholders** (`__GA4_PLACEHOLDER__`, `__FB_PIXEL_PLACEHOLDER__`, `__GSC_PLACEHOLDER__`). Paste the postpaidplans.com property IDs before/after first deploy.

## Deploy
- Cloudflare "Workers with Static Assets" via `wrangler.toml` + `worker.js`, connected to GitHub repo `mallikamin/postpaidplans`. Domain DNS: GoDaddy → Cloudflare nameservers. `git push origin main` → auto-deploy.

## File hygiene (mandatory)
- Daily scratch / drafts / generated → `_files/YYYY-MM-DD/`, not project root.
- Shared images/notes/refs → `_context/screenshots|notes|refs/`, logged in `_context/INDEX.md`.
- Never commit `_context/CREDENTIALS.md`, `*.env`, `_files/`, `_archive/` (all gitignored). Check `git status` before `git add`.

## Git
- Identity: `Malik Amin <amin@sitaratech.info>` — no Co-Authored-By/Claude/Anthropic lines.
- Stage specific paths, not `git add .`.

## Rebrand rule (inherited)
Any title/H1/schema must keep "Etisalat" prominent as a relationship descriptor (Authorized Dealer). H1 must repeat the primary noun from `<title>`.
