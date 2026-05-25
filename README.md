# postpaidplans.com

Tool-led Etisalat postpaid-plan site for the UAE — an **interactive Plan Finder** + side-by-side comparison of all 11 Etisalat postpaid plans. Authorized Etisalat dealer. Conversion via WhatsApp + the reused `/choose-number/` picker.

Static HTML/CSS/JS (inline, no build step). Deploys on Cloudflare as **Workers with Static Assets** (`wrangler.toml` + `worker.js`). Repo: `mallikamin/postpaidplans`.

---

## 🚀 Go-live runbook (GoDaddy domain → Cloudflare)

Domain `postpaidplans.com` is registered at **GoDaddy**. These steps are account-level (do them in your dashboards):

### 1. Add the site to Cloudflare
1. Cloudflare dashboard → **Add a site** → `postpaidplans.com` → Free plan.
2. Cloudflare shows **two nameservers** (e.g. `xxx.ns.cloudflare.com`). Copy them.

### 2. Point GoDaddy → Cloudflare nameservers
1. GoDaddy → **My Products** → `postpaidplans.com` → **DNS** → **Nameservers** → **Change**.
2. Choose **"I'll use my own nameservers"**, paste the two Cloudflare nameservers, save.
3. Propagation: usually 15 min–2 h (can be up to 24 h). Cloudflare emails you when active.

### 3. Create the Cloudflare project from this repo
- **Workers & Pages** → **Create** → **Import a repository** → connect GitHub → pick `mallikamin/postpaidplans`.
- Framework preset: **None**. Build command: *(empty)*. Output dir: `/` (root).
- Cloudflare reads `wrangler.toml` and deploys the worker + static assets. Every `git push origin main` auto-deploys.

### 4. Attach the custom domain
- In the project → **Settings → Domains → Add custom domain** → `postpaidplans.com` (and `www.postpaidplans.com`).
- Because DNS is now on Cloudflare, the records are created automatically. The `CNAME` file in this repo names the apex domain.

### 5. SSL
- Cloudflare → **SSL/TLS** → set to **Full** (or **Full (strict)** once the cert is active). HTTPS is automatic.

---

## 🔑 Before / right after launch — paste real IDs

Search-and-replace these placeholders across `index.html`, `ar/index.html`, `choose-number/index.html`:

| Placeholder | What to paste |
|---|---|
| `__GA4_PLACEHOLDER__` | GA4 Measurement ID for postpaidplans.com (`G-XXXXXXXXXX`) — create a **new GA4 property** |
| `__FB_PIXEL_PLACEHOLDER__` | Meta Pixel ID (new pixel for this domain) — `index.html` only |
| `__GSC_PLACEHOLDER__` | Google Search Console HTML-tag verification code |

Commit + push and they go live on the next deploy.

## 📈 Post-launch SEO checklist
- [ ] **Google Search Console**: add `postpaidplans.com` (Domain property → verify via Cloudflare DNS TXT, easiest now), submit `https://postpaidplans.com/sitemap.xml`.
- [ ] **Bing Webmaster Tools**: add site, submit sitemap. IndexNow key already live at `/7ca1a2e6bf1196e5d1a2582f53300947.txt`.
- [ ] Confirm `https://postpaidplans.com/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/manifest.json` all load.
- [ ] Test the Plan Finder + comparison table + every WhatsApp CTA on mobile.
- [ ] Rich Results test on the homepage (LocalBusiness + WebApplication + FAQPage).
- [ ] (Optional) New branded `og-image.png` — currently reuses the sister-site image.

## 🔁 Shared backend (do not diverge)
- WhatsApp: **`971569028087`** (all WA links). `tel:` voice line: `+971566999377`.
- `/choose-number/` is reused verbatim from `uae-premium-numbers` — same Google Sheets inventory + `PARTNER_API` Apps Script. Keep it functionally identical.

## ⚠️ Positioning rule
Keep copy + titles **distinct** from `uaepremiumnumbers.com` (catalog) and `goldennummbers.com` (numbers) — this site is the **finder/calculator** angle. Etisalat-only; never write "Du". Do **not** clone the per-number or location pages from the sisters (duplicate-content risk).
