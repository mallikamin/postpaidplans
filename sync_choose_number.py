# -*- coding: utf-8 -*-
"""
sync_choose_number.py — sync postpaidplans.com /choose-number/ to the newest
goldennummbers (etisalat-shop) version, which adds: Platinum category tab,
per-card Reserve + Share buttons, the reservation modal, and the shareable
deep-link. Same Google Sheets inventory + same PARTNER_API on both, so this is a
branding/link swap only (the project's "reused tool, branding swapped" rule).

Run:  python sync_choose_number.py
"""
import re

SRC = r"C:\Users\Malik\Desktop\etisalat-shop\choose-number\index.html"
DST = r"C:\ST\Sitara Infotech\postpaidplans\choose-number\index.html"

t = open(SRC, encoding="utf-8").read()

# 1) Remove the GN "Etisalat Consultant" bar block (PPP lacks /etisalat-logo.png and
#    its current choose-number has no such bar).
t = re.sub(r"<!-- ec-bar -->.*?<!-- /ec-bar -->\n?", "", t, flags=re.S)

# 2) Ordered string replacements (specific -> generic).
reps = [
    # --- tracking: GN shared IDs -> PPP dedicated ---
    ("G-G34631QW03", "G-B4813N8J6J"),                 # GA4
    ("1456083435966506", "3266474320203798"),         # Meta Pixel (init + noscript img)
    # --- head identity (keep PPP's plan-led title; advertise Platinum) ---
    ("<title>Golden &amp; VIP Mobile Numbers UAE — Buy Etisalat Special Numbers Online | Dubai</title>",
     "<title>Choose Your Etisalat Number | VIP Silver, Gold &amp; Platinum Numbers UAE | postpaidplans.com</title>"),
    ('content="Golden &amp; VIP Mobile Numbers UAE | Buy Etisalat Special Numbers — Dubai"',
     'content="Choose Your Etisalat Number | VIP Numbers UAE"'),
    ('<meta name="theme-color" content="#0D1117">', '<meta name="theme-color" content="#ED1C24">'),
    # --- brand name / positioning ---
    ("Golden Numbers UAE", "Postpaid Plans UAE"),
    ("Etisalat Authorized Consultant", "Authorized Etisalat Dealer"),
    # --- internal links: GN-only pages -> PPP equivalents ---
    ('href="../numbers/gold-numbers/"', 'href="../numbers/"'),
    ('href="../numbers/786-numbers/"', 'href="../numbers/"'),
    ('href="../numbers/repeating-digit-numbers/"', 'href="../numbers/"'),
    ('href="../emirati/"', 'href="../premium-numbers-uae/"'),
    ('href="../#plans"', 'href="../#compare"'),
    ('href="../#contact"', 'href="../about/"'),
    ('href="../#vip"', 'href="../premium-numbers-uae/"'),
    # --- domain (generic, last) ---
    ("goldennummbers.com", "postpaidplans.com"),
    ("goldennummbers", "postpaidplans"),
]
for a, b in reps:
    t = t.replace(a, b)

# 3) Turnstile resilience — a Turnstile failure (domain not whitelisted on the sitekey,
#    ad-blocker, or network) must NEVER hard-block a real customer. Re-applied on every
#    sync so re-pulls keep the fix. (The bilal-sales worker still applies its own checks.)
ts_patches = [
    ("var _tsWidgetId = null;\nvar _tsLoading = false;",
     "var _tsWidgetId = null;\nvar _tsLoading = false;\nvar _tsFailed = false; // Turnstile failed (wrong domain/ad-blocker/network) — must not block checkout"),
    ("      _tsWidgetId = window.turnstile.render('#coTurnstile', { sitekey: TURNSTILE_SITE_KEY, theme: 'dark' });\n    } catch (e) {}",
     "      _tsWidgetId = window.turnstile.render('#coTurnstile', {\n        sitekey: TURNSTILE_SITE_KEY, theme: 'dark',\n        'error-callback': function() { _tsFailed = true; }\n      });\n    } catch (e) { _tsFailed = true; }"),
    ("  s.async = true;\n  document.head.appendChild(s);\n}",
     "  s.async = true;\n  s.onerror = function() { _tsFailed = true; };\n  document.head.appendChild(s);\n  setTimeout(function() {\n    try { if (!(window.turnstile && _tsWidgetId !== null && window.turnstile.getResponse(_tsWidgetId))) _tsFailed = true; }\n    catch (e) { _tsFailed = true; }\n  }, 10000);\n}"),
    ("if (!tsToken) return checkoutShowError('Please complete the verification box above.');",
     "if (!tsToken && !_tsFailed && _tsWidgetId !== null) return checkoutShowError('Please complete the verification box above.');"),
]
for a, b in ts_patches:
    assert a in t, "ts patch anchor missing: " + repr(a[:45])
    t = t.replace(a, b)

open(DST, "w", encoding="utf-8", newline="\n").write(t)

# --- verify ---
leaks = {k: t.count(k) for k in
         ["goldennummbers", "G-G34631QW03", "1456083435966506", "Golden Numbers UAE",
          "etisalat-logo", "ec-bar", "../emirati/", "../#plans", "gold-numbers/"]}
feats = {k: t.count(k) for k in
         ["btn-reserve", "btn-share", 'data-category="platinum"', "PARTNER_API",
          "1qAw1YQkKEbq", "G-B4813N8J6J", "3266474320203798", "postpaidplans.com"]}
print("LEAKS (should all be 0):")
for k, v in leaks.items():
    print(f"  {v:3d}  {k}")
print("FEATURES/EXPECTED (should be > 0):")
for k, v in feats.items():
    print(f"  {v:3d}  {k}")
print("bytes:", len(t))
