"""
Per-number SEO page generator for postpaidplans.com.

Reads the SAME live Google Sheets inventory the /choose-number/ picker uses,
and writes one static page per Available Silver/Gold/Platinum number to
  /numbers/etisalat-<digits>/index.html
plus a hub at /numbers/index.html, a sitemap-numbers.xml and a sitemap-index.xml.

DELIBERATELY DISTINCT from the sister sites (goldennummbers.com / uaepremiumnumbers.com),
which also publish these same numbers. To avoid duplicate-content cannibalization the
postpaidplans angle is PLAN-PAIRING: every page is built around the Etisalat postpaid
plan the number comes with (Silver -> entry plans from AED 188, Gold -> Gold Plan 500,
Platinum -> Platinum Plan AED 1,000), cross-links the interactive Plan Finder, lists the
matching plans, uses the site's red/light theme (shared /assets/site.css + numbers.css),
and carries its own plan-led copy, FAQ and schema. Self-canonical to postpaidplans.com.

Usage:
    python generate_number_pages.py
"""

import csv
import html
import io
import json
import os
import shutil
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PROJECT_DIR = r"C:\ST\Sitara Infotech\postpaidplans"
BASE_URL = "https://postpaidplans.com"
BRAND = "PostpaidPlans UAE"
DOMAIN = "postpaidplans.com"
WA_NUMBER = "971569028087"
PHONE_DISPLAY = "+971 56 902 8087"
GA4 = "G-B4813N8J6J"  # real PPP GA4 (hardcoded so regen keeps tracking; no post-sweep needed)

# How many of the strongest numbers stay indexable (index,follow + in sitemap).
# The rest are noindex,follow — crawlable as an internal-link layer to the money
# pages, but kept out of the index (thin, near-duplicate, cross-domain dupes with
# the sisters → they earned 0 clicks in GSC and only wasted crawl budget).
INDEXABLE_LIMIT = 100
HUB_PER_TIER = 48  # cap per-tier cards on /numbers/ hub (was: all 3,322 → 505 KB sink)

# Same master sheet the /choose-number/ page consumes.
# 2026-07-13: was still on the two legacy sheets (1qAw dead-404 since 06-17,
# 1Lmfsc empty/mismatched schema) — missed in the 06-17 single-source migration.
SHEETS = [
    {"id": "1CoG5IYOxKdeTlOqCYuntfXxOUlOFWlSX9AiDB1ZBBQs", "gid": "0"},
]
ACCEPTED_CATEGORIES = {"gold": "Gold", "silver": "Silver", "platinum": "Platinum"}

PREFIX_INFO = {
    "050": "Etisalat's original 1994 mobile series — the most recognised prefix in the UAE and a quiet status marker for long-standing residents.",
    "054": "An Etisalat series that grew with Dubai and Abu Dhabi — common on business lines across the Emirates.",
    "056": "Etisalat's modern prefix block — heavily issued with postpaid plans and VIP numbers in Dubai, Sharjah and the Northern Emirates.",
    "058": "A newer Etisalat block with fresh ranges still open — a popular pick for a first UAE business number.",
}

# The 11 live Etisalat postpaid plans (mirrors the homepage Plan Finder dataset).
PLANS = [
    {"id": "fp250",   "name": "Freedom Plan 250",            "price": 188,  "was": 250,  "data": "Non-stop data @3Mbps",   "mins": "1,000 local min",          "best": "Light users on a budget",          "tier": "silver"},
    {"id": "nfp260",  "name": "New Freedom Plan 260",        "price": 195,  "was": 260,  "data": "Non-stop data",          "mins": "1,000 local min",          "best": "Entry postpaid + free number",     "tier": "silver"},
    {"id": "fp325",   "name": "Freedom Plan 325",            "price": 228,  "was": 325,  "data": "Non-stop data",          "mins": "More local min",           "best": "More allowance, still affordable", "tier": "silver"},
    {"id": "ud500",   "name": "Freedom Unlimited Data 500",  "price": 300,  "was": 600,  "data": "Unlimited high-speed",   "mins": "1,000 flexi min",          "best": "Heavy data / streaming / WFH",     "tier": "silver"},
    {"id": "ulc325",  "name": "Unlimited Local Calls 325",   "price": 325,  "was": 325,  "data": "Non-stop data",          "mins": "Unlimited local",          "best": "People who call a lot in the UAE", "tier": "silver"},
    {"id": "u1c325",  "name": "Unlimited 1 Country 325",     "price": 325,  "was": 325,  "data": "30GB",                   "mins": "300 local min + 1 country","best": "Expats calling one home country",  "tier": "silver"},
    {"id": "uc600",   "name": "Unlimited Calls 600 Flexi",   "price": 360,  "was": 600,  "data": "50GB",                   "mins": "Unlimited local + intl",   "best": "Frequent international callers",    "tier": "silver"},
    {"id": "gold500", "name": "Gold Plan 500",               "price": 500,  "was": 500,  "data": "Unlimited data",         "mins": "Unlimited local + intl",   "best": "Families & professionals",         "tier": "gold"},
    {"id": "ldc1200", "name": "Local Data & Calls 1200 Flexi","price": 600, "was": 600,  "data": "200GB",                  "mins": "3,000 flexi min",          "best": "Business owners & power users",     "tier": "gold"},
    {"id": "platinum","name": "Platinum Plan",               "price": 1000, "was": 1000, "data": "Unlimited everything",   "mins": "Unlimited local + intl",   "best": "Top-tier plan + Platinum number",  "tier": "platinum"},
]
PLANS_BY_TIER = defaultdict(list)
for _p in PLANS:
    PLANS_BY_TIER[_p["tier"]].append(_p)

# Per number-tier plan-pairing copy.
PAIRING = {
    "Silver": {
        "offer_price": 188,
        "price_html": 'Free with plans from <b>AED&nbsp;188</b> <small>/mo</small>',
        "headline": "Which Etisalat plan comes with this Silver number?",
        "intro": ("A Silver VIP number like this one is included <strong>free</strong> with most Etisalat "
                  "postpaid plans, starting from just AED 188/month. You lock the number first, then pick the "
                  "plan that matches how you actually use your phone — the number never changes."),
        "tier_key": "silver",
    },
    "Gold": {
        "offer_price": 500,
        "price_html": 'Comes with the <b>Gold Plan 500</b> <small>· AED 500/mo</small>',
        "headline": "Which Etisalat plan comes with this Gold number?",
        "intro": ("A Gold VIP number pairs with Etisalat's <strong>Gold Plan 500</strong> (AED 500/month) — "
                  "unlimited data, unlimited local and international minutes, with the number reserved against "
                  "your Emirates ID. Business users often pair it with the Local Data &amp; Calls 1200 Flexi instead."),
        "tier_key": "gold",
    },
    "Platinum": {
        "offer_price": 1000,
        "price_html": 'Reserved for the <b>Platinum Plan</b> <small>· AED 1,000/mo</small>',
        "headline": "Which Etisalat plan comes with this Platinum number?",
        "intro": ("A Platinum VIP number is the rarest tier and is released with Etisalat's flagship "
                  "<strong>Platinum Plan</strong> (AED 1,000/month) — unlimited everything plus 20GB roaming, "
                  "with full Etisalat backing under your Emirates ID."),
        "tier_key": "platinum",
    },
}


# ===========================================================================
# FETCH + PARSE  (same source as /choose-number/)
# ===========================================================================
def fetch_csv(sheet):
    base = f"https://docs.google.com/spreadsheets/d/{sheet['id']}"
    urls = [
        f"{base}/gviz/tq?tqx=out:csv&headers=1&gid={sheet['gid']}",
        f"{base}/export?format=csv&gid={sheet['gid']}",
    ]
    last_err = None
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                text = r.read().decode("utf-8", errors="replace").strip()
            if text and not text.startswith("<!DOCTYPE") and not text.startswith("<html"):
                return text
            last_err = "non-csv response"
        except Exception as e:
            last_err = str(e)
    raise RuntimeError(f"All CSV endpoints failed for sheet {sheet['id']}: {last_err}")


def parse_csv(text):
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return []
    header = [h.strip().lower() for h in rows[0]]

    def idx(name, default):
        return header.index(name) if name in header else default

    i_cat  = idx("category", 1)
    i_msi  = idx("msisdn", 2)
    i_with = idx("with zero", 3)
    i_no   = idx("without zero", 4)
    i_stat = idx("status", 5)

    out = []
    for row in rows[1:]:
        if len(row) < 4:
            continue
        cat_raw = (row[i_cat] if i_cat < len(row) else "").strip()
        msi     = (row[i_msi] if i_msi < len(row) else "").strip()
        with_z  = (row[i_with] if i_with < len(row) else "").strip().replace(" ", "")
        no_z    = (row[i_no]   if i_no  < len(row) else "").strip().replace(" ", "")
        stat    = (row[i_stat] if i_stat < len(row) else "").strip().lower()

        if stat != "available" or msi == "MSISDN":
            continue
        cat = ACCEPTED_CATEGORIES.get(cat_raw.lower())
        if not cat:
            continue
        if not with_z and no_z:
            with_z = "0" + no_z
        if not with_z:
            continue
        if not msi:
            if no_z:
                msi = "971" + no_z
            elif len(with_z) == 10 and with_z.startswith("0"):
                msi = "971" + with_z[1:]
        if not msi:
            continue

        digits = with_z
        if len(digits) == 10 and digits.startswith("0"):
            formatted = f"{digits[0:3]} {digits[3:6]} {digits[6:]}"
        else:
            formatted = digits

        out.append({"category": cat, "msisdn": msi, "formatted": formatted, "digits": digits})
    return out


def load_all_numbers():
    merged, seen = [], set()
    for s in SHEETS:
        try:
            for n in parse_csv(fetch_csv(s)):
                key = n["digits"] or n["msisdn"]
                if key and key not in seen:
                    seen.add(key)
                    merged.append(n)
        except Exception as e:
            print(f"  [warn] sheet {s['id']}: {e}")
    return merged


# ===========================================================================
# PATTERN ANALYSIS (factual features -> distinct prose)
# ===========================================================================
def analyze(digits):
    if len(digits) != 10:
        return {"prefix": digits[:3], "patterns": [], "digit_sum_root": 0}
    body, last4, last5, last6 = digits[3:], digits[-4:], digits[-5:], digits[-6:]
    patterns = []

    for k in (6, 5, 4, 3):
        if len(set(digits[-k:])) == 1:
            patterns.append(f"ends in {k} identical {digits[-1]}s ({digits[-k:]})")
            break
    z = 0
    for ch in reversed(digits):
        if ch == "0":
            z += 1
        else:
            break
    if z >= 3:
        patterns.append(f"ends in {z} consecutive zeros — a classic round-number signature")
    if last4 in ("0123", "1234", "2345", "3456", "4567", "5678", "6789"):
        patterns.append(f"ends with the ascending run {last4}")
    if last4 in ("9876", "8765", "7654", "6543", "5432", "4321", "3210"):
        patterns.append(f"ends with the descending run {last4}")
    if last5 == last5[::-1]:
        patterns.append(f"ends with the palindrome {last5}")
    elif last4 == last4[::-1] and len(set(last4)) > 1:
        patterns.append(f"ends with the palindrome {last4}")
    if len(last4) == 4 and last4[:2] == last4[2:] and last4[0] != last4[1]:
        patterns.append(f"ends with the repeating pair {last4}")
    if len(last6) == 6 and last6[:3] == last6[3:] and len(set(last6[:3])) > 1:
        patterns.append(f"ends with the repeating triplet {last6}")
    if last4[0] == last4[1] and last4[2] == last4[3] and last4[0] != last4[2]:
        patterns.append(f"ends with the AABB block {last4}")

    s = sum(int(c) for c in digits)
    while s > 9:
        s = sum(int(c) for c in str(s))
    return {"prefix": digits[:3], "patterns": patterns, "digit_sum_root": s}


# ===========================================================================
# HELPERS
# ===========================================================================
def slug_for(num):
    return f"etisalat-{num['digits']}"


def url_for(num):
    return f"{BASE_URL}/numbers/{slug_for(num)}/"


def wa_link(num, context=""):
    msg = (f"Hi, I'm interested in the {num['category']} VIP number {num['formatted']} "
           f"and the plan it comes with, from {DOMAIN}.")
    return f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(msg)}"


def seo_intro(num, info):
    parts = [
        f"Etisalat number <strong>{num['formatted']}</strong> is currently available as a "
        f"{num['category']} VIP listing — and on postpaidplans.com you choose it together with the "
        f"Etisalat postpaid plan that suits you."
    ]
    meta = PREFIX_INFO.get(info["prefix"])
    if meta:
        parts.append(f"The <strong>{info['prefix']}</strong> prefix is {meta}")
    if info["patterns"]:
        focus = info["patterns"][:2]
        if len(focus) == 1:
            parts.append(f"This number {focus[0]}, which makes it easy to say once and never repeat.")
        else:
            parts.append(f"This number {focus[0]}, and also {focus[1]} — a combination that is scarce in active Etisalat ranges.")
    else:
        parts.append("It has a clean, easy-to-recall shape that lifts it out of the standard pool.")
    parts.append(
        f"Its digit-sum reduces to <strong>{info['digit_sum_root']}</strong>, a detail "
        f"numerology-minded buyers in the UAE often weigh when choosing a personal number."
    )
    return " ".join(parts)


def plan_rows_html(tier_key):
    rows = []
    for p in PLANS_BY_TIER.get(tier_key, []):
        was = f'<small>was AED {p["was"]}</small>' if p["was"] > p["price"] else ""
        rows.append(
            f'<div class="plan-row"><div><span class="pn">{html.escape(p["name"])}</span>'
            f'<div class="pmeta">{html.escape(p["data"])} · {html.escape(p["mins"])} · {html.escape(p["best"])}</div></div>'
            f'<div class="pp">AED {p["price"]}{was}</div></div>'
        )
    return '<div class="plan-list">' + "".join(rows) + "</div>"


def faqs_for(num, info):
    cat = num["category"]
    f = num["formatted"]
    qs = []
    if cat == "Silver":
        qs.append((f"What is the cheapest plan I can get {f} on?",
                   f"You can take {f} on the Freedom Plan 250 at AED 188/month — Etisalat's entry postpaid plan, "
                   f"with non-stop data, 1,000 local minutes and this Silver number included free."))
    elif cat == "Gold":
        qs.append((f"Which plan does {f} come with?",
                   f"This Gold number is released with the Gold Plan 500 at AED 500/month — unlimited data plus "
                   f"unlimited local and international minutes. Business users can pair it with the Local Data & Calls 1200 Flexi."))
    else:
        qs.append((f"Which plan does {f} come with?",
                   f"Platinum numbers like {f} are reserved for Etisalat's Platinum Plan at AED 1,000/month — "
                   f"unlimited everything plus 20GB roaming, held under your Emirates ID."))
    qs.append((f"Can I keep {f} if I change my plan later?",
               "Yes. The number is registered to you under your Emirates ID, so you can move it up or down the "
               "Etisalat postpaid range later — the number stays the same."))
    qs.append((f"How do I find the right plan for {f}?",
               "Use the free Plan Finder on postpaidplans.com — answer three quick questions about your budget and "
               "what you use most, and it recommends the matching Etisalat plan in about 60 seconds."))
    qs.append((f"Is {f} still available?",
               f"At the last refresh of this page, {f} was listed as Available in the Etisalat VIP catalogue. "
               f"Inventory moves quickly — confirm on WhatsApp before reserving."))
    return qs


def find_related(num, all_numbers):
    same_tier = [n for n in all_numbers if n["category"] == num["category"] and n["digits"] != num["digits"]][:300]
    same_prefix = [n for n in all_numbers if n["digits"][:3] == num["digits"][:3] and n["digits"] != num["digits"]][:300]
    seed = sum(int(c) for c in num["digits"])

    def rotate(arr, k, n):
        if not arr:
            return []
        k %= len(arr)
        return (arr[k:] + arr[:k])[:n]

    return rotate(same_tier, seed, 6), rotate(same_prefix, seed + 7, 6)


# Tier-aware contextual links from each number page into the matching money page
# (keyword-anchored, pointing at the real landing pages — not /#finder).
MONEY_LINKS = {
    "Silver": [("/cheapest-etisalat-postpaid-plan/", "Cheapest Etisalat plan →"),
               ("/etisalat-plans-under-200-aed/", "Plans under AED 200")],
    "Gold": [("/best-etisalat-plan-for-family/", "Best family plan →"),
             ("/best-etisalat-unlimited-data-plan/", "Best unlimited data plan")],
    "Platinum": [("/best-etisalat-plan-for-family/", "Best family plan →"),
                 ("/etisalat-business-postpaid-plans/", "Business plans")],
}


def number_score(num):
    """Strength score — patterns + repeated-tail + premium tier. Drives which
    numbers stay indexable and which lead the hub. Plain numbers score 0."""
    info = analyze(num["digits"])
    d = num["digits"]
    score = len(info["patterns"]) * 10
    if len(d) == 10:
        for k in (6, 5, 4, 3):
            if len(set(d[-k:])) == 1:
                score += k * 6
                break
    score += {"Platinum": 18, "Gold": 9, "Silver": 0}.get(num["category"], 0)
    return score


def pick_indexable(numbers, limit=INDEXABLE_LIMIT):
    """Return the set of digit-strings for the top-`limit` strongest numbers
    (score > 0). Everything else is noindex,follow + excluded from the sitemap."""
    ranked = sorted(numbers, key=lambda n: (number_score(n), n["digits"]), reverse=True)
    return {n["digits"] for n in ranked[:limit] if number_score(n) > 0}


# ===========================================================================
# SHARED CHROME (header / footer / scripts) — matches the live sub-pages
# ===========================================================================
ANALYTICS = (
    '<script async src="https://www.googletagmanager.com/gtag/js?id=' + GA4 + '"></script>'
    '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
    "gtag('js',new Date());gtag('config','" + GA4 + "');</script>"
)

HEADER = (
    '<header><div class="wrap nav"><a href="/" class="brand"><span class="dot"></span>Postpaid<b>Plans</b>&nbsp;UAE</a>'
    '<nav class="nav-links"><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a>'
    '<a href="/numbers/">VIP Numbers</a><a href="/blog/">Blog</a><a href="/choose-number/">Choose Number</a>'
    '<a href="/about/">About</a></nav><div class="nav-cta">'
    '<a href="https://wa.me/' + WA_NUMBER + '" target="_blank" rel="noopener noreferrer" class="btn btn-wa">WhatsApp</a></div>'
    '<button class="burger" id="burger" aria-label="Open menu">&#9776;</button></div>'
    '<div class="mobile-menu" id="mobileMenu"><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a>'
    '<a href="/numbers/">VIP Numbers</a><a href="/blog/">Blog</a><a href="/choose-number/">Choose Number</a>'
    '<a href="/about/">About Us</a></div></header>'
)

FOOTER = (
    '<footer><div class="wrap"><div class="foot-grid">'
    '<div><div class="foot-brand">Postpaid<b>Plans</b> UAE</div>'
    '<p style="max-width:24rem">Official e&amp; Partner &amp; Authorized Etisalat Dealer helping UAE residents pick the right '
    'Etisalat postpaid plan and a premium VIP number — fast. Same-day SIM delivery in Dubai, Abu Dhabi &amp; Sharjah.</p>'
    '<a href="https://wa.me/' + WA_NUMBER + '" target="_blank" rel="noopener noreferrer" class="btn btn-wa" style="margin-top:1rem">WhatsApp ' + PHONE_DISPLAY + '</a>'
    '<div style="font-size:.82rem;color:rgba(255,255,255,.62);margin-top:.85rem;line-height:1.55">&#128205; Al Zarooni Building, Office 1904, Ayal Nasir, Deira, Dubai, UAE</div></div>'
    '<div><h4>Etisalat Plan Guides</h4>'
    '<a href="/best-etisalat-unlimited-data-plan/">Best Unlimited Data Plan</a>'
    '<a href="/best-etisalat-plan-for-family/">Best Family Plan</a>'
    '<a href="/etisalat-plans-under-200-aed/">Plans Under AED 200</a>'
    '<a href="/cheapest-etisalat-postpaid-plan/">Cheapest Postpaid Plan</a>'
    '<a href="/etisalat-business-postpaid-plans/">Business Plans</a></div>'
    '<div><h4>Explore</h4><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a>'
    '<a href="/choose-number/">Choose Your Number</a><a href="/numbers/">All VIP Numbers</a>'
    '<a href="/reviews/">Reviews</a><a href="/blog/">Blog</a></div>'
    '<div><h4>Legal</h4><a href="/privacy/">Privacy Policy</a><a href="/terms/">Terms of Service</a>'
    '<a href="/refund-policy/">Refund &amp; Contact</a><a href="/ar/">العربية</a></div></div>'
    '<p class="disclaimer">© 2026 postpaidplans.com. Postpaid Plans UAE is an Official e&amp; Partner and Authorized '
    'Etisalat Dealer, operated independently; we are not Emirates Telecommunications Group Company (e&amp;) PJSC itself. '
    '"Etisalat" and "e&amp;" are trademarks of their respective owners. Prices are set by Etisalat and may change; '
    'final pricing confirmed at order.</p></div></footer>'
)

PAGE_JS = (
    "<script>var b=document.getElementById('burger'),m=document.getElementById('mobileMenu');"
    "if(b)b.addEventListener('click',function(){m.style.display=m.style.display==='flex'?'none':'flex';});"
    "function closeNav(){if(m)m.style.display='none';}"
    "var fl=document.getElementById('faqList');"
    "if(fl)fl.addEventListener('click',function(e){var q=e.target.closest('.faq-q');if(!q)return;"
    "var o=q.getAttribute('aria-expanded')==='true';var a=q.nextElementSibling;"
    "q.setAttribute('aria-expanded',!o);a.style.maxHeight=o?'0':(a.scrollHeight+40)+'px';});</script>"
)

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">'
)


# ===========================================================================
# PAGE TEMPLATE
# ===========================================================================
def page_html(num, all_numbers, indexable):
    info = analyze(num["digits"])
    cat = num["category"]
    pair = PAIRING[cat]
    page_url = url_for(num)
    wa = wa_link(num)
    f = html.escape(num["formatted"])
    faqs = faqs_for(num, info)
    rel_tier, rel_prefix = find_related(num, all_numbers)
    robots_val = ("index, follow, max-image-preview:large, max-snippet:-1"
                  if num["digits"] in indexable else "noindex, follow")
    money = MONEY_LINKS[cat]
    money_cta = (f'<a class="btn btn-red" href="{money[0][0]}">{money[0][1]}</a>'
                 f'<a class="btn btn-ghost" href="{money[1][0]}">{money[1][1]}</a>')

    # ---- meta ----
    title = f"Etisalat {num['formatted']} — {cat} VIP Number + Plan | {BRAND}"
    description = (
        f"Get Etisalat number {num['formatted']} ({cat} VIP) with the postpaid plan it comes with — "
        f"{'free from AED 188/mo' if cat=='Silver' else ('the Gold Plan 500' if cat=='Gold' else 'the Platinum Plan')}. "
        f"Official e& Partner & Authorized Etisalat Dealer. Match it to your usage with the free Plan Finder, order on WhatsApp."
    )
    keywords = (
        f"etisalat {num['digits']}, {num['formatted']}, etisalat {cat.lower()} number plan, "
        f"etisalat {info['prefix']} number, {cat.lower()} number postpaid plan uae, "
        f"buy etisalat vip number with plan, postpaidplans"
    )
    og_image = f"{BASE_URL}/og-image.png"

    # ---- schema ----
    product = {
        "@context": "https://schema.org", "@type": "Product",
        "name": f"Etisalat {num['formatted']} ({cat} VIP Number + Postpaid Plan)",
        "description": (f"Etisalat {num['formatted']} — {cat} VIP number from {BRAND}, paired with its "
                        f"Etisalat postpaid plan. Authorized Etisalat Dealer in the UAE."),
        "url": page_url, "sku": num["msisdn"], "mpn": num["digits"],
        "category": f"{cat} VIP Mobile Number + Postpaid Plan",
        "brand": {"@type": "Brand", "name": "Etisalat"},
        "offers": {"@type": "Offer", "price": str(pair["offer_price"]), "priceCurrency": "AED",
                   "availability": "https://schema.org/InStock", "url": page_url,
                   "seller": {"@type": "Organization", "name": BRAND, "url": BASE_URL + "/"}},
    }
    breadcrumb = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "VIP Numbers", "item": BASE_URL + "/numbers/"},
            {"@type": "ListItem", "position": 3, "name": f"Etisalat {num['formatted']}", "item": page_url},
        ],
    }
    faq_schema = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in faqs],
    }
    jsonld = "\n".join(f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>'
                       for b in (product, breadcrumb, faq_schema))

    # ---- body fragments ----
    pattern_list = ""
    if info["patterns"]:
        pattern_list = ("<ul style='margin:.4rem 0 .2rem 1.2rem;color:var(--body)'>"
                        + "".join(f"<li style='margin-bottom:.3rem'>{html.escape(p.capitalize())}</li>" for p in info["patterns"])
                        + "</ul>")

    def rcards(nums):
        return "".join(
            f'<a class="rcard" href="/numbers/{slug_for(n)}/"><span class="rnum">{html.escape(n["formatted"])}</span>'
            f'<span class="rmeta">{n["category"]} · plan from AED {PAIRING[n["category"]]["offer_price"]}</span></a>'
            for n in nums)

    rel_tier_html = (f'<section class="block"><div class="wrap"><h2 style="font-size:1.4rem;margin-bottom:.3rem">More {cat} VIP numbers</h2>'
                     f'<p style="color:var(--muted);margin-bottom:.4rem">Same tier, same plan pairing.</p>'
                     f'<div class="related">{rcards(rel_tier)}</div></div></section>') if rel_tier else ""
    rel_prefix_html = (f'<section class="block bg-soft"><div class="wrap"><h2 style="font-size:1.4rem;margin-bottom:.3rem">More Etisalat {info["prefix"]} numbers</h2>'
                       f'<div class="related">{rcards(rel_prefix)}</div></div></section>') if rel_prefix else ""

    faq_html = "".join(
        f'<div class="faq-item"><button class="faq-q" aria-expanded="false">{html.escape(q)}<span class="pm">+</span></button>'
        f'<div class="faq-a"><p>{html.escape(a)}</p></div></div>'
        for q, a in faqs)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{ANALYTICS}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="keywords" content="{html.escape(keywords)}">
<meta name="theme-color" content="#E30613">
<meta name="robots" content="{robots_val}">
<meta name="author" content="{DOMAIN}">
<link rel="canonical" href="{page_url}">
<meta property="og:type" content="product">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{page_url}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_AE">
<meta property="og:image" content="{og_image}">
<meta property="product:price:amount" content="{pair['offer_price']}">
<meta property="product:price:currency" content="AED">
<meta property="product:availability" content="in stock">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(description)}">
<meta name="twitter:image" content="{og_image}">
<meta name="geo.region" content="AE">
<meta name="geo.placename" content="Dubai, United Arab Emirates">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/numbers.css">
{jsonld}
</head>
<body>
{HEADER}

<div class="wrap"><div class="crumb"><a href="/">Home</a> › <a href="/numbers/">VIP Numbers</a> › <span>Etisalat {f}</span></div></div>

<header class="num-hero"><div class="wrap">
  <span class="tier-pill {pair['tier_key']}">{cat} VIP Number</span>
  <h1 class="num-h1">Etisalat VIP Number</h1>
  <div class="big-num">{f}</div>
  <p class="num-sub">An Official e&amp; Partner listing — choose this {cat} number together with the Etisalat postpaid plan it comes with.</p>
  <div class="num-price">{pair['price_html']}</div>
  <div class="cta-row">
    <a class="btn btn-wa btn-lg" href="{wa}" target="_blank" rel="noopener noreferrer" data-cta="hero_wa">Reserve on WhatsApp</a>
    <a class="btn btn-ghost btn-lg" href="/#finder">Find my plan →</a>
  </div>
</div></header>

<div class="wrap">
  <div class="facts">
    <div class="fact"><div class="k">Tier</div><div class="v">{cat}</div></div>
    <div class="fact"><div class="k">Prefix</div><div class="v">{info['prefix']}</div></div>
    <div class="fact"><div class="k">Plan from</div><div class="v">AED {pair['offer_price']}</div></div>
    <div class="fact"><div class="k">Digit-sum</div><div class="v">{info['digit_sum_root']}</div></div>
  </div>

  <div class="pairing">
    <h2>{pair['headline']}</h2>
    <p>{pair['intro']}</p>
    {plan_rows_html(pair['tier_key'])}
    <div class="cta-row" style="justify-content:flex-start">
      {money_cta}
    </div>
  </div>
</div>

<section class="block"><div class="wrap prose">
  <h2>About this Etisalat number</h2>
  <p>{seo_intro(num, info)}</p>
  {pattern_list}
</div></section>

<section class="block bg-soft"><div class="wrap">
  <h2 style="font-size:1.5rem;margin-bottom:1rem">How to get {f}</h2>
  <ol class="steps">
    <li><strong>Tap “Reserve on WhatsApp”</strong> — your message opens with this exact number already filled in.</li>
    <li><strong>Pick your plan</strong> — keep the {cat} tier’s plan, or use the <a href="/#finder">Plan Finder</a> to match a plan to how you use your phone.</li>
    <li><strong>Share your Emirates ID</strong> — we reserve {f} in your name with Etisalat and deliver the SIM the same day across Dubai, Abu Dhabi &amp; Sharjah.</li>
  </ol>
  <div class="cta-row" style="justify-content:flex-start"><a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener noreferrer" data-cta="mid_wa">Reserve {f} on WhatsApp</a></div>
</div></section>

{rel_tier_html}
{rel_prefix_html}

<section class="block"><div class="wrap" style="max-width:780px">
  <h2 style="font-size:1.5rem;margin-bottom:1rem">Frequently asked questions</h2>
  <div id="faqList">{faq_html}</div>
</div></section>

{FOOTER}

<div class="sticky-cta">
  <div class="meta"><span>Etisalat · {cat}</span><b>{f}</b></div>
  <a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener noreferrer" data-cta="sticky_wa">Reserve on WhatsApp</a>
</div>

{PAGE_JS}
</body>
</html>"""


# ===========================================================================
# HUB  (/numbers/)
# ===========================================================================
def hub_html(numbers):
    by_tier = defaultdict(list)
    for n in numbers:
        by_tier[n["category"]].append(n)
    title = f"All Etisalat VIP Numbers UAE — {len(numbers)} Available + Plans | {BRAND}"
    description = (f"Browse all {len(numbers)} available Etisalat VIP numbers — Silver, Gold and Platinum — each paired "
                   f"with its postpaid plan. Official e& Partner & Authorized Etisalat Dealer. Match a plan with the free Plan Finder.")

    def block(tier):
        nums = by_tier.get(tier, [])
        if not nums:
            return ""
        total = len(nums)
        shown = sorted(nums, key=number_score, reverse=True)[:HUB_PER_TIER]
        cards = "".join(
            f'<a class="rcard" href="/numbers/{slug_for(n)}/"><span class="rnum">{html.escape(n["formatted"])}</span>'
            f'<span class="rmeta">{tier} · plan from AED {PAIRING[tier]["offer_price"]}</span></a>' for n in shown)
        sub = f'Plan from AED {PAIRING[tier]["offer_price"]}/mo.'
        more = ""
        if total > len(shown):
            sub = f'Plan from AED {PAIRING[tier]["offer_price"]}/mo — showing the top {len(shown)} of {total}.'
            more = (f'<p style="margin-top:.8rem"><a href="/choose-number/" class="btn btn-ghost">'
                    f'Search all {total} live {tier} numbers →</a></p>')
        return (f'<section class="block"><div class="wrap"><h2 style="font-size:1.5rem;margin-bottom:.2rem">{tier} VIP Numbers '
                f'<small style="font-weight:400;color:var(--muted);font-size:.95rem">({total} available)</small></h2>'
                f'<p style="color:var(--muted);margin-bottom:.7rem">{sub}</p>'
                f'<div class="related">{cards}</div>{more}</div></section>')

    blocks = "".join(block(t) for t in ("Platinum", "Gold", "Silver"))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{ANALYTICS}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="theme-color" content="#E30613">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{BASE_URL}/numbers/">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{BASE_URL}/numbers/">
<meta property="og:image" content="{BASE_URL}/og-image.png">
<link rel="icon" type="image/x-icon" href="/favicon.ico">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/numbers.css">
</head>
<body>
{HEADER}

<div class="wrap"><div class="crumb"><a href="/">Home</a> › <span>VIP Numbers</span></div></div>

<section class="hero"><div class="wrap hero-inner">
  <span class="eyebrow">⚡ Official e&amp; Partner · Authorized Etisalat Dealer</span>
  <h1>All Etisalat <span class="hl">VIP Numbers</span> — with the plan they come with</h1>
  <p class="lead">Live inventory of every available Etisalat VIP number, grouped by tier. Each number has its own page with the postpaid plan it pairs with, pattern detail and an instant WhatsApp inquiry. Not sure which plan? <a href="/#finder" style="color:var(--red);font-weight:600">Use the free Plan Finder →</a></p>
  <div class="hero-cta"><a href="/#finder" class="btn btn-red btn-lg">Find my plan</a><a href="/choose-number/" class="btn btn-ghost btn-lg">Search the live list</a></div>
</div></section>

{blocks}

{FOOTER}
{PAGE_JS}
</body>
</html>"""


# ===========================================================================
# SITEMAPS
# ===========================================================================
def write_sitemaps(numbers, indexable):
    indexable_nums = [n for n in numbers if n["digits"] in indexable]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             f'  <url><loc>{BASE_URL}/numbers/</loc><changefreq>daily</changefreq><priority>0.8</priority></url>']
    for n in indexable_nums:
        lines.append(f'  <url><loc>{BASE_URL}/numbers/{slug_for(n)}/</loc><changefreq>weekly</changefreq><priority>0.5</priority></url>')
    lines.append('</urlset>')
    p = os.path.join(PROJECT_DIR, "sitemap-numbers.xml")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"  wrote sitemap-numbers.xml ({len(indexable_nums)+1} URLs — {len(indexable_nums)} indexable numbers + hub)")

    idx = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
           f'  <sitemap><loc>{BASE_URL}/sitemap.xml</loc></sitemap>',
           f'  <sitemap><loc>{BASE_URL}/sitemap-numbers.xml</loc></sitemap>',
           '</sitemapindex>']
    with open(os.path.join(PROJECT_DIR, "sitemap-index.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(idx))
    print("  wrote sitemap-index.xml")


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print(f"Loading numbers from {len(SHEETS)} sheets...")
    numbers = load_all_numbers()
    print(f"  -> {len(numbers)} Available numbers")
    for k, v in Counter(n["category"] for n in numbers).most_common():
        print(f"     {k}: {v}")
    if not numbers:
        print("No numbers fetched — aborting.")
        return 1

    out_root = os.path.join(PROJECT_DIR, "numbers")
    os.makedirs(out_root, exist_ok=True)

    indexable = pick_indexable(numbers)
    print(f"  -> {len(indexable)} numbers kept indexable (top by pattern score); rest noindex,follow")

    written = 0
    for num in numbers:
        out_dir = os.path.join(out_root, slug_for(num))
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page_html(num, numbers, indexable))
        written += 1
        if written % 500 == 0:
            print(f"  ...{written} pages")

    # Prune stale number dirs — numbers no longer in live inventory (sold) would
    # otherwise linger as thin, index,follow orphans that waste crawl budget.
    current_slugs = {slug_for(n) for n in numbers}
    pruned = 0
    for entry in os.listdir(out_root):
        full = os.path.join(out_root, entry)
        if os.path.isdir(full) and entry.startswith("etisalat-") and entry not in current_slugs:
            shutil.rmtree(full, ignore_errors=True)
            pruned += 1
    print(f"  pruned {pruned} stale number dirs (no longer in inventory)")

    with open(os.path.join(out_root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(hub_html(numbers))
    print(f"  wrote /numbers/index.html (hub)")

    write_sitemaps(numbers, indexable)
    print(f"\nDone: {written} per-number pages + hub + sitemaps.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
