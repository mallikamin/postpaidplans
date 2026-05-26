# Verification Log

Append-only log of what was verified, when, and how. Newest at top.

## 2026-05-25 (eve) — Per-number SEO pages live (~3,322) + combined sitemap submitted

- **Category**: code / SEO / infra
- **What**: Owner-approved reversal of the "deferred" per-number-pages decision. Built `generate_number_pages.py` (postpaidplans) → one static page per Available number from the **shared Google Sheet** (same source as `/choose-number/`) at `/numbers/etisalat-<digits>/` + a `/numbers/` hub. Counts: **3,322 numbers (Silver 3128 / Gold 152 / Platinum 42)**.
- **Distinctness (vs sister number pages that publish the same numbers)**: deliberate **plan-pairing angle** — each page is built around the Etisalat postpaid plan the number comes with (Silver→entry plans from AED 188, Gold→Gold Plan 500, Platinum→Platinum Plan), lists the matching plans, cross-links the Plan Finder, plan-led FAQ + copy, red/light theme via shared `/assets/site.css` + new `/assets/numbers.css`, self-canonical. Genuinely different from the number-led sister template (mitigates 3-way cannibalization that CLAUDE.md warned about).
- **Sitemap**: `sitemap-numbers.xml` (3,323 URLs incl. hub) + `sitemap-index.xml` (points to sitemap.xml + sitemap-numbers.xml). robots.txt now advertises the index.
- **How verified**: rendered Gold/Silver/Platinum + hub samples (desktop + true-mobile via Playwright) before the full run; committed (1657179) + pushed → Cloudflare auto-deploy. Live checks: `/numbers/etisalat-0501450770/`=200 (distinct plan copy present), `/numbers/`=200, `sitemap-index.xml`=200, `sitemap-numbers.xml`=200, `generate_number_pages.py`=**404** (`.assetsignore` `*.py` works). **IndexNow: all 3,323 URLs submitted, 4 batches all HTTP 200** (Bing/Yandex). Homepage footer links the hub.
- **UPDATE (2026-05-26)**: GSC Domain property verified + `sitemap-index.xml` submitted. Initial "Couldn't fetch" on the child sitemaps was transient (files verified 200 + well-formed + Googlebot-fetchable); after also submitting `sitemap.xml` + `sitemap-numbers.xml` directly, GSC shows **both Success — 3,342 discovered pages**. Bing: `BingSiteAuth.xml` added (same account code as the sister sites `FB75C28E2BBCE9DF7516EC8D1093DAD5`) for one-click XML-file verification; IndexNow already pushed all 3,323 URLs.

## 2026-05-25 (eve) — Header responsiveness fixed (desktop crowding + mobile + Arabic)

- **Category**: code / UI
- **What**: Fixed non-optimized headers across all custom pages. Three issues found & fixed:
  1. **Desktop crowding (881–1080px)**: nav only collapsed at 880px, so on small laptops / iPad-landscape the 6 links + brand + CTAs overcrowded (link text wrapped to 2 lines, ghost/WhatsApp buttons overlapped). → Collapse to burger now at **≤1080px**; added `white-space:nowrap` on nav links; tightened gap to 1.4rem.
  2. **Mobile (≤560px)**: inline WhatsApp pill crowded the bar next to the burger. → Hide `.nav-cta` on phones (WhatsApp stays in the burger menu + floating fab); brand shrinks to 1.12rem.
  1b. **Desktop density / brand touching first link**: even one-line, the homepage bar was dense (a "Plan Finder" link AND a "Find my plan" button both jump to the same tool) and the brand "UAE" butted against "Plan Finder". → Added `gap:1.2rem` to `.nav` (guaranteed min separation, all 3 header defs) and **removed the duplicate "Plan Finder" desktop nav link** on the homepage (kept the prominent "Find my plan" button + the "Plan Finder" item in the mobile menu). Per Malik's choice. Sub-pages keep their "Plan Finder" link (they have no button, so it's not a duplicate there).
  3. **Arabic (`ar/index.html`) was broken**: mobile hid `.nav-links` with **no burger and no mobile menu at all** → zero navigation on Arabic phones. → Added burger + mobile-menu markup, CSS, and toggle JS (mirrors English).
- **Files**: `index.html` (inline CSS), `ar/index.html` (inline CSS + markup + JS), `assets/site.css` (shared by 14 sub-pages). `choose-number/` left untouched (reused picker, stays identical to sister site).
- **How verified**: Playwright (true mobile viewport) + headless Chrome over `python -m http.server`. Confirmed: 1120px inline-clean, 1000px collapses to burger w/ WhatsApp kept, 360/390px = clean brand+burger (EN & loc burger right, AR burger left RTL), burger opens full menu on both EN + AR. **Gotcha logged**: headless Chrome `--window-size` clamps to a ~min width and crops the right edge below ~450px — use Playwright with an explicit `viewport` for true narrow-width shots.
- **STILL TODO**: unchanged — GA4/Pixel/GSC IDs (placeholders). Changes are uncommitted (not yet pushed/deployed).

## 2026-05-25 (pm) — Content expansion live + business facts confirmed

- **Category**: code / content / business
- **What**: 5 location pages + blog (index+6 posts) + About + Refund policy + reviews + address + Official-e&-Partner wording — all LIVE (commit b10ec78), every URL verified 200.
- **Confirmed business facts (per Malik)**:
  - Status: **Official e& Partner & Authorized Etisalat Dealer** (Malik confirmed legally true → wording used sitewide).
  - Address: **Al Zarooni Building, Office 1904, Ayal Nasir, Deira, Dubai, UAE** (in footer + all LocalBusiness schemas, NAP normalized to this).
  - Google reviews: **5.0 ★ (3 reviews)** — reviewers Labeeb AK, Bilal Khalid, Ali Murtaza Sarajdin. Place CID `11719519233119757422` → link `https://www.google.com/maps?cid=11719519233119757422`.
- **Compliance call**: did NOT add AggregateRating/Review JSON-LD for the Google reviews (third-party / self-serving review guideline) — shown as visible testimonials only. Screenshots in `_context/screenshots/`.
- **STILL TODO**: GA4/Pixel/GSC IDs (placeholders); real delivery PHOTO files (Malik sent a streetview link, not usable image files); optional www→apex redirect + branded og-image.

## 2026-05-25 — LIVE on Cloudflare custom domain

- **Category**: infra
- **What**: postpaidplans.com fully deployed + reachable on the real domain.
- **How**: GoDaddy NS → Cloudflare (daisy/vick.ns.cloudflare.com, verified at 1.1.1.1 + 8.8.8.8). Worker "postpaidplans" connected to GitHub repo (auto-deploy on push). Custom domains `postpaidplans.com` + `www` attached (after deleting GoDaddy parked A records 13.248.243.5 / 76.223.105.230 + www CNAME; kept _dmarc TXT + _domainconnect CNAME).
- **Result**: `https://postpaidplans.com/` + www = 200 w/ valid SSL; `/choose-number/`,`/robots.txt`,`/sitemap.xml`=200; `/.git/*`,`/_context/*`,`worker.js`,`wrangler.toml`,`README.md`=404 (`.assetsignore` fix confirmed live). Account/account-id cf6f829b0a562dcbeff59a286900c25f.
- **STILL TODO**: real GA4/Pixel/GSC IDs (placeholders live); turn OFF Cloudflare "Block AI training bots" (was set to Block on all pages — kills GEO); optional www→apex redirect.

## 2026-05-25 — Initial build + backend reuse verified

- **Category**: code / infra
- **What**: postpaidplans.com v1 scaffolded; backend reused from uae-premium-numbers.
- **How**: read `uae-premium-numbers/choose-number/index.html` + `worker.js` + `wrangler.toml` this session.
- **Result**:
  - choose-number SHEETS inventory (2 sheets, gid 0) + `PARTNER_API` Apps Script copied verbatim; only domain + `WA_NUMBER` changed.
  - `WA_NUMBER` set to `971569028087` per Malik (used across all sister sites now). `tel:` voice line kept at `+971566999377`.
  - Plan dataset (11 plans, AED 188–1,000) pulled from uae-premium-numbers ItemList + FAQ schema.
  - Deploy model confirmed = "Workers with Static Assets" (no `.github` workflow; Cloudflare connects to repo via wrangler.toml).
- **Still UNVERIFIED (do this session/next)**: live Cloudflare project not yet created; DNS not yet cut over; GA4/Pixel/GSC IDs are placeholders.
