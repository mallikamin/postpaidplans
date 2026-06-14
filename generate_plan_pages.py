# -*- coding: utf-8 -*-
"""
generate_plan_pages.py, builds the intent-specific Etisalat plan landing pages
for postpaidplans.com (the pages goldennummbers profits from but PPP was missing).

Each page reuses the proven /etisalat-postpaid-plans-dubai/ template shell
(GA4 + Meta Pixel + LocalBusiness/Breadcrumb/ItemList/FAQ schema + plan table +
FAQ accordion + footer) so analytics & markup are byte-identical site-wide.
Only the per-intent copy (hero, quick answer, prose, which-plan list, FAQs,
title/meta, plan ordering) is authored per page.

Run:  python generate_plan_pages.py   -> writes <slug>/index.html for each page.
Excluded from public serving via .assetsignore (*.py), like generate_number_pages.py.
"""
import os
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
WA = "971569028087"

# --- Canonical 11-plan catalogue (values match the live Dubai landing page) -----
# (key, name, price, old_price, data, minutes, roaming, free_number, popular, schema_desc, note)
PLANS = {
    "freedom250":   ("Freedom Plan 250", "188", "250", "Non-stop @3Mbps", "1,000 local", "2GB", "Silver", False,
                      "Non-stop data at 3Mbps, 1,000 local minutes, 2GB roaming and a free Silver VIP number.", ""),
    "newfreedom260":("New Freedom Plan 260", "195", "260", "Non-stop", "1,000 local", "2GB", "Silver", False,
                      "Non-stop data, 1,000 local minutes, 2GB roaming and a free Silver VIP number.", ""),
    "freedom325":   ("Freedom Plan 325", "228", "325", "Non-stop", "More local", "3GB", "Silver", False,
                      "Non-stop data, more local minutes, 3GB roaming and a free Silver VIP number.", ""),
    "unldata500":   ("Freedom Unlimited Data 500", "300", "600", "Unlimited high-speed", "1,000 flexi", "5GB", "Silver", False,
                      "Unlimited high-speed data, 1,000 flexi minutes, 5GB roaming and a free Silver VIP number.", ""),
    "unllocal325":  ("Unlimited Local Calls 325", "325", "", "Non-stop", "Unlimited local", "3GB", "Silver", False,
                      "Non-stop data, unlimited local calls, 3GB roaming and a free Silver VIP number.", ""),
    "unl1country":  ("Unlimited 1 Country 325", "325", "", "30GB", "300 local + unltd 1 country", "3GB", "Silver", False,
                      "30GB data, 300 local minutes plus unlimited calls to one country, 3GB roaming and a free Silver VIP number.", ""),
    "unlcalls600":  ("Unlimited Calls 600 Flexi", "360", "600", "50GB", "Unlimited flexi", "2GB", "Silver", True,
                      "50GB data, unlimited flexi minutes (local and international), 2GB roaming and a free Silver VIP number.", ""),
    "gold500":      ("Gold Plan 500", "500", "", "Unlimited", "Unltd local + intl", "5GB", "Gold", False,
                      "Unlimited data, unlimited local and international minutes, 5GB roaming and a free Gold VIP number.", ""),
    "local1200":    ("Local Data & Calls 1200 Flexi", "600", "", "200GB", "3,000 flexi", "5GB", "Gold", False,
                      "200GB data, 3,000 flexi minutes, 5GB roaming and a free Gold VIP number.", ""),
    "emirati":      ("Emirati Freedom", "250", "", "Unlimited high-speed", "Unlimited local", "n/a", "VIP", False,
                      "Unlimited high-speed data and unlimited local calls with a VIP number, for UAE nationals with a valid Emirati ID.", "(UAE Nationals)"),
    "platinum":     ("Platinum Plan", "1,000", "", "Unlimited everything", "Unltd local + intl", "20GB", "Platinum", False,
                      "Unlimited everything, unlimited data, unlimited local and international minutes, 20GB roaming and a free Platinum VIP number.", ""),
}
DEFAULT_ORDER = ["freedom250","newfreedom260","freedom325","unldata500","unllocal325",
                 "unl1country","unlcalls600","gold500","local1200","emirati","platinum"]


def price_cell(price, old):
    if old:
        return ('AED %s <span style="color:var(--muted);font-weight:400;'
                'text-decoration:line-through;font-size:.8rem">%s</span>' % (price, old))
    return "AED %s" % price


def wa(text):
    return "https://wa.me/%s?text=%s" % (WA, quote(text))


def render_rows(order, ctx):
    rows = []
    for k in order:
        name, price, old, data, mins, roam, num, pop, _, note = PLANS[k]
        badge = ('<span style="display:inline-block;background:#FDE7E8;color:var(--red);'
                 'font-size:.66rem;font-weight:700;padding:.1rem .45rem;border-radius:999px;'
                 'vertical-align:middle">POPULAR</span>') if pop else ""
        notespan = ('<span style="color:var(--muted);font-size:.74rem">%s</span>' % note) if note else ""
        link = wa("Hi, I'd like the %s plan%s." % (name, ctx))
        rows.append(
            '<tr><td class="pname">%s %s%s</td><td class="price">%s</td><td>%s</td>'
            '<td>%s</td><td>%s</td><td>%s</td>'
            '<td><a class="mini-wa" href="%s" target="_blank" rel="noopener noreferrer">Order</a></td></tr>'
            % (name, badge, (" " + notespan) if notespan else "", price_cell(price, old), data, mins, roam, num, link))
    return "\n            ".join(rows)


def render_itemlist(order, list_name):
    items = []
    for i, k in enumerate(order, 1):
        name, price, old, data, mins, roam, num, pop, desc, note = PLANS[k]
        price_num = price.replace(",", "")
        items.append(
            '{ "@type": "ListItem", "position": %d, "item": { "@type": "Product", "name": "%s", '
            '"brand": { "@type": "Brand", "name": "Etisalat by e&" }, "description": "%s", '
            '"offers": { "@type": "Offer", "price": "%s", "priceCurrency": "AED", '
            '"availability": "https://schema.org/InStock", "priceValidUntil": "2026-12-31", '
            '"seller": { "@type": "Organization", "name": "Postpaid Plans UAE" } } } }'
            % (i, name, desc, price_num))
    return ",\n      ".join(items)


def render_faq_schema(faqs):
    out = []
    for q, a in faqs:
        out.append('{ "@type": "Question", "name": "%s", "acceptedAnswer": { "@type": "Answer", "text": "%s" } }'
                   % (q.replace('"', '\\"'), a.replace('"', '\\"')))
    return ",\n      ".join(out)


def render_faq_html(faqs):
    out = []
    for q, a in faqs:
        out.append('<div class="faq-item"><button class="faq-q" aria-expanded="false">%s'
                   '<span class="pm">+</span></button><div class="faq-a"><p>%s</p></div></div>' % (q, a))
    return "\n      ".join(out)


HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js), GA4 (postpaidplans dedicated property). -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B4813N8J6J"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-B4813N8J6J');
  </script>
  <!-- Meta Pixel (postpaidplans dedicated dataset 3266474320203798). -->
  <script>
    !function(f, b, e, v, n, t, s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n, arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t, s)}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', '3266474320203798');
    fbq('track', 'PageView');
  </script>

  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>@@TITLE@@</title>
  <meta name="description" content="@@META_DESC@@">
  <meta name="keywords" content="@@KEYWORDS@@">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#E30613">
  <link rel="canonical" href="https://postpaidplans.com/@@SLUG@@/">
  <link rel="alternate" hreflang="en" href="https://postpaidplans.com/@@SLUG@@/">
  <link rel="alternate" hreflang="x-default" href="https://postpaidplans.com/@@SLUG@@/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="@@TITLE@@">
  <meta property="og:description" content="@@META_DESC@@">
  <meta property="og:url" content="https://postpaidplans.com/@@SLUG@@/">
  <meta property="og:site_name" content="Postpaid Plans UAE">
  <meta property="og:image" content="https://postpaidplans.com/og-image.png">
  <meta name="geo.region" content="AE">
  <meta name="geo.placename" content="United Arab Emirates">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="manifest" href="/manifest.json">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/site.css">

  <!-- Structured Data: LocalBusiness -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "LocalBusiness",
    "name": "@@LB_NAME@@",
    "alternateName": "Official e& Partner & Authorized Etisalat Dealer",
    "description": "@@LB_DESC@@",
    "url": "https://postpaidplans.com/@@SLUG@@/",
    "telephone": "+971569028087",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "Al Zarooni Building, Office 1904, Ayal Nasir, Deira",
      "addressLocality": "Dubai",
      "addressRegion": "Dubai",
      "addressCountry": "AE"
    },
    "areaServed": [ { "@type": "Country", "name": "United Arab Emirates" } ],
    "priceRange": "AED 188 - AED 1,000",
    "contactPoint": {
      "@type": "ContactPoint",
      "telephone": "+971569028087",
      "contactType": "sales",
      "availableLanguage": ["English", "Arabic"]
    }
  }
  </script>

  <!-- Structured Data: BreadcrumbList -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://postpaidplans.com/" },
      { "@type": "ListItem", "position": 2, "name": "@@BREADCRUMB@@", "item": "https://postpaidplans.com/@@SLUG@@/" }
    ]
  }
  </script>

  <!-- Structured Data: ItemList of Products (plans) -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "@@ITEMLIST_NAME@@",
    "itemListElement": [
      @@PLAN_ITEMLIST@@
    ]
  }
  </script>

  <!-- Structured Data: FAQPage -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      @@FAQ_SCHEMA@@
    ]
  }
  </script>
</head>
<body>
  <header><div class="wrap nav"><a href="/" class="brand"><span class="dot"></span>Postpaid<b>Plans</b>&nbsp;UAE</a><nav class="nav-links"><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a><a href="/premium-numbers-uae/">VIP Numbers</a><a href="/blog/">Blog</a><a href="/choose-number/">Choose Number</a><a href="/about/">About</a></nav><div class="nav-cta"><a href="https://wa.me/971569028087" target="_blank" rel="noopener noreferrer" class="btn btn-wa">WhatsApp</a></div><button class="burger" id="burger" aria-label="Open menu">&#9776;</button></div><div class="mobile-menu" id="mobileMenu"><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a><a href="/premium-numbers-uae/">VIP Numbers</a><a href="/blog/">Blog</a><a href="/choose-number/">Choose Number</a><a href="/about/">About Us</a></div></header>

  <div class="wrap"><div class="crumb"><a href="/">Home</a> › <span>@@BREADCRUMB@@</span></div></div>

  <section class="hero"><div class="wrap hero-inner"><span class="eyebrow">⚡ Official e&amp; Partner · Authorized Etisalat Dealer</span><h1>@@H1@@</h1><p class="lead">@@LEAD@@</p><div class="hero-cta"><a href="/#finder" class="btn btn-red btn-lg">Find my plan in 60s →</a><a href="@@HERO_WA@@" target="_blank" rel="noopener noreferrer" class="btn btn-ghost btn-lg">Talk to a LIVE Etisalat Specialist</a></div><div class="trust-row"><span>✓ Same-day delivery</span><span>✓ Free VIP number</span><span>✓ All UAE</span></div></div></section>

  <section class="block"><div class="wrap">
    <div class="answer"><h3>Quick answer</h3><p>@@QUICK_ANSWER@@</p></div>

    <div class="prose">
      @@PROSE@@

      <h2>@@TABLE_HEADING@@</h2>
      <div class="table-scroll">
        <table class="cmp">
          <thead><tr><th>Plan</th><th>Price /mo</th><th>Data</th><th>Minutes</th><th>Roaming</th><th>Free number</th><th></th></tr></thead>
          <tbody>
            @@PLAN_ROWS@@
          </tbody>
        </table>
      </div>
      <p style="font-size:.82rem;color:var(--muted);margin-top:.8rem">Prices are set by Etisalat and may change; final pricing is confirmed at order. The Emirati Freedom plan requires a valid Emirati ID.</p>

      <h3>@@WHICH_HEADING@@</h3>
      <ul>
        @@WHICH_LIST@@
      </ul>

      <h3>Pair your plan with a free VIP number</h3>
      <p>Most plans here include a free VIP number, a <strong>Silver</strong> on standard plans, a <strong>Gold</strong> on the Gold Plan, and a <strong>Platinum</strong> on the top tier. Browse the live inventory of 2,500+ numbers at <a href="/choose-number/">Choose Number</a> and lock a memorable line before you order. Not sure which plan? Run the <a href="/#finder">Plan Finder</a> or <a href="/#compare">compare plans</a> on the homepage.</p>

      <div class="link-chips">
        <a href="/#finder">Plan Finder</a>
        <a href="/#compare">Compare Plans</a>
        <a href="/best-etisalat-unlimited-data-plan/">Unlimited Data Plans</a>
        <a href="/best-etisalat-plan-for-family/">Best Family Plan</a>
        <a href="/etisalat-plans-under-200-aed/">Plans Under AED 200</a>
        <a href="/cheapest-etisalat-postpaid-plan/">Cheapest Plan</a>
        <a href="/etisalat-business-postpaid-plans/">Business Plans</a>
        <a href="/etisalat-postpaid-plans-dubai/">Plans in Dubai</a>
        <a href="/international-calling-plans/">International calling</a>
        <a href="/best-etisalat-plan-calling-india/">Calling India</a>
        <a href="/blog/etisalat-vs-du-postpaid-plans-uae/">Etisalat vs Du</a>
        <a href="/reviews/">Reviews</a>
        <a href="/choose-number/">Browse live numbers</a>
        <a href="/blog/">Read the blog</a>
      </div>
    </div>
  </div></section>

  <section class="block bg-soft"><div class="wrap">
    <div class="grid-3">
      <div class="card"><div class="ico">\U0001f4b8</div><h3>From AED 188</h3><p>Genuine Etisalat pricing, including discounted Freedom plans, no dealer mark-up.</p></div>
      <div class="card"><div class="ico">⚡</div><h3>Same-day SIM</h3><p>Order before the afternoon cut-off and a rider delivers across the UAE today.</p></div>
      <div class="card"><div class="ico">\U0001f381</div><h3>Free VIP number</h3><p>A Silver, Gold or Platinum number included with eligible plans, pick yours first.</p></div>
    </div>
  </div></section>

  <section class="block"><div class="wrap">
    <h2 style="font-size:clamp(1.6rem,3vw,2.25rem);margin-bottom:1.4rem">@@FAQ_HEADING@@</h2>
    <div id="faqList">
      @@FAQ_HTML@@
    </div>
  </div></section>

  <section class="block bg-soft"><div class="wrap"><div class="cta-band"><h2>@@CTA_H2@@</h2><p>@@CTA_P@@</p><a href="@@CTA_WA@@" class="btn btn-wa btn-lg" target="_blank" rel="noopener noreferrer">Talk to a LIVE Etisalat Specialist now</a></div></div></section>

  <footer><div class="wrap"><div class="foot-grid"><div><div class="foot-brand">Postpaid<b>Plans</b> UAE</div><p style="max-width:24rem">Official e&amp; Partner &amp; Authorized Etisalat Dealer helping UAE residents pick the right Etisalat postpaid plan and a premium VIP number, fast. Same-day SIM delivery in Dubai, Abu Dhabi &amp; Sharjah.</p><a href="https://wa.me/971569028087" target="_blank" rel="noopener noreferrer" class="btn btn-wa" style="margin-top:1rem">Talk to a LIVE Etisalat Specialist</a><div style="display:inline-flex;align-items:center;gap:.45rem;margin-top:.9rem;font-size:.8rem;color:rgba(255,255,255,.72);background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:.4rem .7rem">\U0001f512 SSL secured · Official e&amp; Partner</div><div style="font-size:.82rem;color:rgba(255,255,255,.62);margin-top:.85rem;line-height:1.55">&#128205; Al Zarooni Building, Office 1904, Ayal Nasir, Deira, Dubai, UAE<br><a href="https://www.google.com/maps?cid=11719519233119757422" target="_blank" rel="noopener noreferrer" style="color:var(--gold)">&#9733; 5.0 &mdash; Read our Google reviews &rarr;</a></div></div><div><h4>Plan guides</h4><a href="/best-etisalat-unlimited-data-plan/">Unlimited Data Plan</a><a href="/best-etisalat-plan-for-family/">Best Family Plan</a><a href="/etisalat-plans-under-200-aed/">Plans Under AED 200</a><a href="/cheapest-etisalat-postpaid-plan/">Cheapest Plan</a><a href="/etisalat-business-postpaid-plans/">Business Plans</a><a href="/etisalat-postpaid-plans-dubai/">Plans in Dubai</a></div><div><h4>VIP Numbers</h4><a href="/premium-numbers-uae/">Premium Numbers UAE</a><a href="/vip-numbers-dubai/">VIP Numbers Dubai</a><a href="/vip-numbers-abu-dhabi/">VIP Numbers Abu Dhabi</a><a href="/golden-numbers-sharjah/">Golden Numbers Sharjah</a><a href="/choose-number/">Choose Your Number</a></div><div><h4>Company</h4><a href="/about/">About Us</a><a href="/reviews/">Reviews</a><a href="/faq/">FAQ</a><a href="/privacy/">Privacy Policy</a><a href="/refund-policy/">Refund &amp; Contact</a><a href="/ar/">العربية</a></div></div><p class="disclaimer">© 2026 postpaidplans.com. Postpaid Plans UAE is an Official e&amp; Partner and Authorized Etisalat Dealer, operated independently; we are not Emirates Telecommunications Group Company (e&amp;) PJSC itself. "Etisalat" and "e&amp;" are trademarks of their respective owners. Prices are set by Etisalat and may change; final pricing confirmed at order.</p></div></footer>

  <a class="wa-fab" href="https://wa.me/971569028087" target="_blank" rel="noopener noreferrer" aria-label="Talk to a live Etisalat specialist on WhatsApp"><svg viewBox="0 0 24 24"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38c1.45.79 3.08 1.21 4.79 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0012.04 2zm5.8 14.13c-.24.68-1.42 1.31-1.95 1.36-.5.05-1.13.07-1.82-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.37-.14-.2-1.18-1.57-1.18-2.99 0-1.42.74-2.12 1.01-2.41.26-.29.57-.36.76-.36l.55.01c.18.01.42-.07.65.5.24.57.81 1.99.88 2.13.07.14.12.31.02.5-.09.2-.14.31-.28.48-.14.17-.29.37-.42.5-.14.14-.28.29-.12.57.16.28.72 1.18 1.54 1.91 1.06.95 1.95 1.24 2.23 1.38.28.14.44.12.6-.07.16-.2.69-.81.88-1.08.18-.28.37-.23.62-.14.25.09 1.6.76 1.87.9.28.14.46.2.53.32.07.11.07.66-.17 1.34z"/></svg></a>
  <script>var b=document.getElementById('burger'), m=document.getElementById('mobileMenu');if(b)b.addEventListener('click', function(){m.style.display=m.style.display==='flex'?'none':'flex';});function track(a){try{if(typeof gtag==='function')gtag('event', a);}catch(e){}}
  // Fire a Lead event (GA4 + Meta Pixel) on any WhatsApp click, real conversion signal.
  document.addEventListener('click', function(e){var a=e.target.closest('a[href*="wa.me"]');if(!a)return;try{if(typeof gtag==='function')gtag('event','generate_lead',{method:'whatsapp'});}catch(x){}try{if(typeof fbq==='function')fbq('track','Lead',{content_name:'whatsapp_click'});}catch(x){}});
  var fl=document.getElementById('faqList');if(fl)fl.addEventListener('click', function(e){var q=e.target.closest('.faq-q');if(!q)return;var o=q.getAttribute('aria-expanded')==='true';var a=q.nextElementSibling;q.setAttribute('aria-expanded',!o);a.style.maxHeight=o?'0':(a.scrollHeight+40)+'px';});</script>
</body></html>'''


# ----------------------------- PER-PAGE CONTENT ------------------------------
PAGES = []

# 1) BEST FAMILY PLAN
PAGES.append(dict(
    slug="best-etisalat-plan-for-family",
    ctx=" for my family",
    title="Best Etisalat Plan for a Family in the UAE 2026 | From AED 188",
    meta_desc="Find the best Etisalat (e&) postpaid plan for a family in the UAE, unlimited data, shared lines and a free VIP number from AED 188/mo. Official e& partner, same-day SIM delivery.",
    keywords="best etisalat plan for family, family mobile plan uae, etisalat family postpaid plan, best family postpaid plan uae, etisalat plan for family of four, cheapest postpaid family plan",
    breadcrumb="Best Etisalat Plan for Family",
    lb_name="Postpaid Plans UAE, Best Etisalat Family Plans",
    lb_desc="Compare and order the best Etisalat (e&) postpaid plans for UAE families, an unlimited-data anchor line plus affordable add-on lines from AED 188/month, each with a free VIP number and same-day SIM delivery.",
    itemlist_name="Best Etisalat Postpaid Plans for Families",
    h1='Best Etisalat Plan for a <span class="hl">Family</span> in the UAE',
    lead="One bill, the whole household connected. We compare every Etisalat (e&amp;) postpaid plan side by side so you can put a heavy-data line on the parent who works from home, an unlimited-local line on the one who is always on the phone, and a budget Freedom line on the kids, each with a free VIP number, all delivered the same day.",
    quick_answer="For most UAE families the smart setup is an <strong>unlimited-data anchor line</strong>, the Freedom Unlimited Data 500 (AED 300/month) or the Gold Plan 500, paired with one or more <strong>Freedom Plan 250 lines at AED 188</strong> for teenagers and second phones. Parents who call home abroad should look at the Unlimited 1 Country 325 or the Unlimited Calls 600 Flexi. Every line includes a free VIP number and same-day delivery.",
    prose='''<h2>How to choose an Etisalat plan for a family</h2>
      <p>A family rarely needs five identical plans. The cheapest, smartest setup is to match each line to the person who uses it. Start with one <strong>anchor line</strong> for whoever consumes the most data, usually the parent working from home or the teenager streaming, and give the lighter users an affordable Freedom line. Because every plan here is billed and activated by Etisalat directly, you can mix and match tiers across the household and still keep one simple relationship with us as your authorized dealer.</p>
      <p>The other decision that actually matters for families is <strong>calling</strong>. If a parent calls relatives in India, Pakistan, the Philippines or Egypt every week, an unlimited-data plan alone will not help, you want the Unlimited 1 Country 325 (unlimited calls to one country) or the Unlimited Calls 600 Flexi, whose minutes work both locally and internationally. UAE nationals get the best deal of all with the Emirati Freedom plan.</p>''',
    table_heading="Compare Etisalat plans for a family",
    which_heading="Which plan suits which family member?",
    which_list='''<li><strong>Kids &amp; teenagers / second line:</strong> Freedom Plan 250, AED 188 with non-stop data and a free Silver number.</li>
        <li><strong>The heavy-data parent</strong> (work-from-home, streaming): Freedom Unlimited Data 500, unlimited high-speed at AED 300.</li>
        <li><strong>The one always on calls:</strong> Unlimited Local Calls 325 for local-only, or Unlimited Calls 600 Flexi for local + international.</li>
        <li><strong>Calling family abroad:</strong> Unlimited 1 Country 325 for one country unlimited.</li>
        <li><strong>The whole household, no compromises:</strong> Gold Plan 500, unlimited data and calls with a free Gold number.</li>
        <li><strong>UAE nationals:</strong> Emirati Freedom, unlimited data and local calls at AED 250 with a valid Emirati ID.</li>''',
    faq_heading="Best Etisalat Family Plan, FAQ",
    faqs=[
        ("What is the cheapest Etisalat plan for a family?",
         "The most economical family setup pairs one anchor line, typically the Freedom Unlimited Data 500 at AED 300/month, with Freedom Plan 250 lines at AED 188/month for the lighter users. Each line includes non-stop or unlimited data and a free Silver VIP number, so a family of three can be fully connected from around AED 576/month."),
        ("Which Etisalat plan is best for a family of four?",
         "For a typical family of four, put the Gold Plan 500 or Freedom Unlimited Data 500 on the heaviest user, an Unlimited Local Calls or Unlimited Calls 600 Flexi line on the biggest caller, and Freedom Plan 250 lines on the two lightest users. Use the free Plan Finder on postpaidplans.com to match plans to each person's usage."),
        ("Can I get several Etisalat SIMs on one family account?",
         "Yes. We can set up multiple Etisalat postpaid lines for one household, each on the tier that fits that person, and deliver every SIM the same day with a free VIP number. Message us on WhatsApp +971 56 902 8087 and we will build the family setup for you."),
        ("Which family plan is best for calling relatives abroad?",
         "The Unlimited 1 Country 325 gives unlimited calls to one country (ideal if family is all in, say, India or Pakistan). If relatives are spread across several countries, the Unlimited Calls 600 Flexi at AED 360/month gives unlimited flexi minutes that work both locally and internationally."),
        ("Is each family line billed separately or on one account?",
         "Etisalat bills each line on its own plan, but we set the whole household up together so you only deal with one authorized dealer. You can mix tiers across lines, an unlimited anchor line plus AED 188 Freedom lines, and pay each bill through the My Etisalat app."),
        ("Is there a contract on Etisalat family plans?",
         "Etisalat postpaid plans carry a commitment of 12 to 24 months, depending on the plan and the VIP number you choose, which is what makes the discounted pricing and the free VIP number possible. We confirm the exact term for each plan you choose before you order."),
        ("Do I need a separate Emirates ID for each family line?",
         "Each postpaid line is registered to a valid Emirates ID. Adults register their own lines; a line for a child is registered under a parent's Emirates ID. Message us and we will map out exactly what each line needs."),
        ("Can I move my family's existing numbers to Etisalat?",
         "Yes. UAE number portability lets you bring existing numbers, including from du, onto Etisalat postpaid plans, and each line keeps working until its switch completes. We handle the official porting request for every line."),
        ("How fast can you deliver several family SIMs?",
         "Same day across the UAE. Order before the afternoon cut-off and a rider delivers all the family SIMs together, have each person's original Emirates ID and a payment card ready at the door."),
    ],
    cta_h2='Set up the right <span class="gold-text">family plan</span> today',
    cta_p="Tell us how many lines you need and how each person uses their phone, we will build the most cost-effective Etisalat family setup and deliver every SIM the same day with a free VIP number.",
    cta_ctx="Hi, please help me set up Etisalat postpaid plans for my family.",
    order=["unldata500","gold500","freedom250","newfreedom260","unllocal325","unl1country","unlcalls600","emirati","freedom325","local1200","platinum"],
))

# 2) PLANS UNDER AED 200
PAGES.append(dict(
    slug="etisalat-plans-under-200-aed",
    ctx="",
    title="Etisalat Postpaid Plans Under AED 200 (2026) | Best Value e& Plans",
    meta_desc="The best Etisalat (e&) postpaid plans under AED 200/month in the UAE, non-stop data, 1,000 local minutes and a free VIP number from AED 188. Official e& partner, same-day SIM delivery.",
    keywords="etisalat plans under 200 aed, best value postpaid plan uae under aed 200, etisalat 200 aed plan, cheap etisalat postpaid plan, postpaid plan under 200, affordable postpaid uae",
    breadcrumb="Etisalat Plans Under AED 200",
    lb_name="Postpaid Plans UAE, Etisalat Plans Under AED 200",
    lb_desc="Compare and order the best-value Etisalat (e&) postpaid plans under AED 200 per month, non-stop data, 1,000 local minutes and a free Silver VIP number from AED 188, with same-day SIM delivery across the UAE.",
    itemlist_name="Etisalat Postpaid Plans Under AED 200",
    h1='Etisalat Postpaid Plans <span class="hl">Under AED 200</span>',
    lead="You do not need to spend a fortune for a genuine Etisalat postpaid line. Two e&amp; plans land under AED 200 a month, both with non-stop data, 1,000 local minutes and a free Silver VIP number. Here is exactly what each gives you, who it suits, and when it is worth stretching a little further.",
    quick_answer="Two Etisalat postpaid plans come in under AED 200/month: the <strong>Freedom Plan 250 at AED 188</strong> (down from AED 250) and the <strong>New Freedom Plan 260 at AED 195</strong> (down from AED 260). Both include non-stop data, 1,000 local minutes, 2GB roaming and a free Silver VIP number. The Freedom Plan 250 is the better value and our most popular budget pick.",
    prose='''<h2>What you actually get under AED 200</h2>
      <p>Both sub-AED-200 plans are real Etisalat (e&amp;) products, not stripped-down prepaid SIMs. "Non-stop data" means you keep browsing, messaging and mapping at a steady speed with no hard cut-off once you pass a cap, which for most people is all they need day to day. You also get 1,000 local minutes, 2GB of roaming for travel, and a free Silver VIP number so your line looks the part from day one.</p>
      <p>The honest difference between the two is small: the Freedom Plan 250 at AED 188 is the value leader, and the New Freedom Plan 260 at AED 195 is essentially the same package a few dirhams higher. If you want genuinely <em>unlimited high-speed</em> data rather than non-stop, that starts at the Freedom Unlimited Data 500 (AED 300), worth knowing before you decide AED 188 is enough.</p>''',
    table_heading="Etisalat plans under AED 200 (and the next steps up)",
    which_heading="Is an under-AED-200 plan right for you?",
    which_list='''<li><strong>Yes, if</strong> you are a light-to-moderate user, a student, or want an affordable second line: Freedom Plan 250 at AED 188 is the pick.</li>
        <li><strong>Marginal call:</strong> New Freedom Plan 260 at AED 195, the same package for a few dirhams more.</li>
        <li><strong>Stretch a little</strong> if you hotspot or stream heavily: Freedom Unlimited Data 500 (AED 300) swaps non-stop for true unlimited high-speed.</li>
        <li><strong>Heavy caller:</strong> if you call abroad a lot, an under-200 plan will not cover it, look at Unlimited 1 Country 325.</li>''',
    faq_heading="Etisalat Plans Under AED 200, FAQ",
    faqs=[
        ("What is the best Etisalat postpaid plan under AED 200?",
         "The Freedom Plan 250 at AED 188/month is the best value under AED 200, non-stop data at 3Mbps, 1,000 local minutes, 2GB roaming and a free Silver VIP number, delivered same day across the UAE. The New Freedom Plan 260 at AED 195 is the only other plan under AED 200."),
        ("Do Etisalat plans under AED 200 include data?",
         "Yes. Both the Freedom Plan 250 (AED 188) and the New Freedom Plan 260 (AED 195) include non-stop data, you keep browsing at a steady speed with no hard cut-off, plus 1,000 local minutes and 2GB of roaming. For unlimited high-speed data you would step up to the Freedom Unlimited Data 500 at AED 300."),
        ("Is the AED 188 Etisalat plan a promotional price?",
         "The Freedom Plan 250 is offered at AED 188/month, discounted from its AED 250 list price. Etisalat sets and can change pricing, so we confirm the exact current price when you order. As an authorized dealer there is no extra dealer mark-up on top."),
        ("Can I get a free number with an under-AED-200 plan?",
         "Yes, both under-AED-200 plans include a free Silver VIP number. Browse the live inventory at postpaidplans.com/choose-number and lock a memorable line before you order, then we deliver the SIM the same day."),
        ("Does the AED 188 price include VAT?",
         "Listed prices are set by Etisalat and exclude 5% VAT, which UAE law adds to telecom services on your monthly bill. There is no dealer mark-up on top, you pay Etisalat's price plus the standard VAT."),
        ("Is the AED 188 plan a contract or month-to-month?",
         "Etisalat postpaid plans carry a commitment of 12 to 24 months, depending on the plan and the VIP number you choose, which is what allows the discounted AED 188 rate and the free VIP number. We confirm the exact term before you order."),
        ("Can I get an under-AED-200 plan on a tourist visa?",
         "A postpaid line requires a valid Emirates ID, so a tourist visa generally does not qualify. If your residency visa is being processed, message us and we will advise on timing, once your Emirates ID is issued we can deliver the same day."),
        ("Can I keep my current number on the AED 188 plan?",
         "Yes. You can port your existing mobile number, including from du, onto the Freedom Plan 250, and your line keeps working until the switch completes. We guide you through the official porting request."),
        ("Does the cheaper plan support eSIM?",
         "Yes, Etisalat supports eSIM on compatible devices. Tell us at order and we will set up an eSIM instead of a physical SIM where your phone supports it."),
    ],
    cta_h2='Get a great Etisalat line <span class="gold-text">under AED 200</span>',
    cta_p="Pick the Freedom Plan 250 at AED 188 with a free Silver number, and we will deliver the SIM the same day across the UAE, or message us and we will confirm the best current budget option.",
    cta_ctx="Hi, I'd like an Etisalat postpaid plan under AED 200.",
    order=["freedom250","newfreedom260","freedom325","emirati","unldata500","unl1country","unllocal325","unlcalls600","gold500","local1200","platinum"],
))

# 3) CHEAPEST POSTPAID PLAN
PAGES.append(dict(
    slug="cheapest-etisalat-postpaid-plan",
    ctx="",
    title="Cheapest Etisalat Postpaid Plan in the UAE 2026 | From AED 188/mo",
    meta_desc="The cheapest Etisalat (e&) postpaid plan in the UAE is the Freedom Plan 250 at AED 188/month, non-stop data, 1,000 minutes and a free VIP number. Official e& partner, same-day SIM delivery.",
    keywords="cheapest etisalat postpaid plan, cheapest postpaid plan uae, lowest etisalat plan, cheap postpaid sim uae, etisalat cheapest plan, affordable postpaid uae",
    breadcrumb="Cheapest Etisalat Postpaid Plan",
    lb_name="Postpaid Plans UAE, Cheapest Etisalat Postpaid Plan",
    lb_desc="The cheapest genuine Etisalat (e&) postpaid plan in the UAE, the Freedom Plan 250 at AED 188/month with non-stop data, 1,000 local minutes and a free Silver VIP number, delivered same day with no dealer mark-up.",
    itemlist_name="Cheapest Etisalat Postpaid Plans",
    h1='Cheapest Etisalat <span class="hl">Postpaid Plan</span> in the UAE',
    lead="If your only question is “what is the lowest I can pay for a real Etisalat postpaid line?”, the answer is AED 188 a month. Here is the cheapest plan, exactly what it includes, and the small print worth knowing before you decide the cheapest is also the right one.",
    quick_answer="The cheapest Etisalat postpaid plan in the UAE is the <strong>Freedom Plan 250 at AED 188/month</strong> (down from AED 250). It includes non-stop data at 3Mbps, 1,000 local minutes, 2GB roaming and a free Silver VIP number, with same-day SIM delivery. The next cheapest is the New Freedom Plan 260 at AED 195. As an authorized dealer we add no mark-up, you pay Etisalat's price.",
    prose='''<h2>The cheapest Etisalat postpaid plan, explained</h2>
      <p>The Freedom Plan 250 is the entry point to Etisalat (e&amp;) postpaid at AED 188/month. "Cheapest" here means the lowest monthly commitment for a genuine postpaid line, not a watered-down prepaid SIM. You still get non-stop data, a healthy 1,000 local minutes, roaming for travel, and a free Silver VIP number, all activated by Etisalat directly.</p>
      <p>One honest caveat: the cheapest plan uses <strong>non-stop</strong> data, which keeps you connected at a steady speed but is not the same as <em>unlimited high-speed</em>. If you tether a laptop, stream in HD or game, you may feel the difference, and stepping up to the Freedom Unlimited Data 500 (AED 300) is the better long-term value. For everyday browsing, messaging, maps and social media, AED 188 is genuinely all most people need.</p>''',
    table_heading="Cheapest Etisalat plans, lowest price first",
    which_heading="Should you pick the cheapest plan?",
    which_list='''<li><strong>Pick AED 188</strong> (Freedom Plan 250) if you are a light-to-moderate user who mostly browses, messages and maps, it is the best value floor.</li>
        <li><strong>Pick AED 195</strong> (New Freedom Plan 260) only if the Freedom Plan 250 is unavailable for your number choice.</li>
        <li><strong>Spend a bit more</strong> (Freedom Unlimited Data 500, AED 300) if you hotspot or stream a lot, cheapest is not always best value.</li>
        <li><strong>UAE nationals</strong> should compare the Emirati Freedom plan, which gives unlimited data and local calls at AED 250.</li>''',
    faq_heading="Cheapest Etisalat Postpaid Plan, FAQ",
    faqs=[
        ("What is the cheapest Etisalat postpaid plan right now?",
         "The cheapest is the Freedom Plan 250 at AED 188/month (down from AED 250), non-stop data at 3Mbps, 1,000 local minutes, 2GB roaming and a free Silver VIP number, with same-day SIM delivery across the UAE."),
        ("Is AED 188 really the lowest Etisalat postpaid price?",
         "Yes, AED 188/month for the Freedom Plan 250 is the lowest genuine Etisalat postpaid price. Cheaper options are prepaid (pay-as-you-go) SIMs rather than postpaid plans. As an authorized e& dealer we charge Etisalat's price with no added mark-up."),
        ("What is the catch with the cheapest plan?",
         "There is no hidden catch, but the cheapest plan uses non-stop data (steady speed) rather than unlimited high-speed. For everyday use that is fine; for heavy hotspot, HD streaming or gaming, the Freedom Unlimited Data 500 at AED 300 is better value over time."),
        ("Does the cheapest Etisalat plan include a free number?",
         "Yes. The Freedom Plan 250 includes a free Silver VIP number. You can browse the live number inventory at postpaidplans.com/choose-number, pick a memorable line, and we deliver the SIM the same day."),
        ("Is there anything cheaper than AED 188 at Etisalat?",
         "Not for a postpaid plan. AED 188/month is the lowest genuine Etisalat postpaid price. Anything cheaper is prepaid (pay-as-you-go), which has no fixed monthly bill, no bundled minutes and no free VIP number."),
        ("Does the cheapest plan have a contract?",
         "Etisalat postpaid plans carry a commitment of 12 to 24 months, depending on the plan and the VIP number you choose, which is part of what makes the AED 188 rate and the free VIP number possible. We confirm the exact term before you order."),
        ("Is VAT included in the AED 188 price?",
         "No, prices are set by Etisalat and exclude 5% VAT, which UAE law adds to telecom services on your bill. As an authorized dealer we add no mark-up beyond Etisalat's own price."),
        ("Can I upgrade later if the cheapest plan is too small?",
         "Yes. You can move up to a higher Etisalat plan at any time if AED 188 turns out to be too little data or too few minutes, and your number stays the same. Message us and we will arrange the upgrade."),
        ("What do I need for the cheapest plan, and how fast is delivery?",
         "Just your original Emirates ID and a payment card. Choose the plan and a free Silver number, confirm on WhatsApp, and we deliver and activate the SIM the same day across the UAE, the rider carries a card machine, so no cash is needed."),
    ],
    cta_h2='Get the cheapest Etisalat line at <span class="gold-text">AED 188</span>',
    cta_p="Lock the Freedom Plan 250 with a free Silver number and we will deliver the SIM the same day across the UAE, Etisalat's price, no dealer mark-up.",
    cta_ctx="Hi, I'd like the cheapest Etisalat postpaid plan (Freedom Plan 250).",
    order=["freedom250","newfreedom260","emirati","freedom325","unldata500","unl1country","unllocal325","unlcalls600","gold500","local1200","platinum"],
))

# 4) BUSINESS PLANS
PAGES.append(dict(
    slug="etisalat-business-postpaid-plans",
    ctx=" for my business",
    title="Etisalat Business Postpaid Plans for UAE Companies & SMBs 2026",
    meta_desc="Etisalat (e&) business postpaid plans for UAE companies and SMBs, unlimited data, local + international minutes and multi-line setups with a free VIP number. Official e& partner, same-day SIM delivery.",
    keywords="etisalat business postpaid plans, uae postpaid plans for smb, etisalat postpaid plans for companies, business mobile plan uae, etisalat business sim, etisalat business mobile postpaid plans",
    breadcrumb="Etisalat Business Postpaid Plans",
    lb_name="Postpaid Plans UAE, Etisalat Business Postpaid Plans",
    lb_desc="Compare and order Etisalat (e&) business postpaid plans for UAE companies and SMBs, unlimited data, unlimited local and international minutes, and multi-line setups with a free VIP number and same-day SIM delivery.",
    itemlist_name="Etisalat Business Postpaid Plans for UAE Companies",
    h1='Etisalat <span class="hl">Business</span> Postpaid Plans for UAE Companies',
    lead="Whether you are a solo founder, a trading company in Deira or a growing SMB, the right mobile plan keeps your team reachable, your international suppliers a tap away, and your costs predictable. We compare every Etisalat (e&amp;) plan for business use, unlimited data, two-way flexi minutes and multi-line setups, and deliver SIMs the same day.",
    quick_answer="For most UAE businesses the best value is the <strong>Unlimited Calls 600 Flexi at AED 360/month</strong>,50GB data plus unlimited flexi minutes that work both locally and internationally, ideal for owners dealing with overseas suppliers. For directors who want no limits, the <strong>Gold Plan 500</strong> and <strong>Platinum Plan</strong> give unlimited everything. We can set up multiple lines on one relationship and deliver every SIM the same day.",
    prose='''<h2>What businesses should look for in a postpaid plan</h2>
      <p>Business phone usage has three demands a personal plan often ignores: <strong>reliable data</strong> on the move, <strong>international calling</strong> to suppliers and clients, and the ability to run <strong>several lines</strong> under one simple arrangement. Etisalat (e&amp;) covers all three, the trick is matching the tier to the role. A field salesperson needs unlimited data; an owner sourcing from China or India needs flexi minutes that work abroad; an accounts line might only need a budget Freedom plan.</p>
      <p>Because we are an authorized e&amp; dealer, you get Etisalat's genuine business-grade network and pricing without the wait, pick the tiers for each role, add a memorable VIP number for the lines that face customers, and we deliver every SIM the same day across the UAE. For teams that call one country constantly, the Unlimited 1 Country 325 is a quiet money-saver.</p>''',
    table_heading="Compare Etisalat plans for business use",
    which_heading="Which Etisalat plan suits which role?",
    which_list='''<li><strong>Owner / director dealing with overseas suppliers:</strong> Unlimited Calls 600 Flexi, unlimited two-way flexi minutes + 50GB.</li>
        <li><strong>No-limits executive line:</strong> Gold Plan 500 or Platinum Plan, unlimited data and local + international calls.</li>
        <li><strong>Field / sales team (heavy data):</strong> Freedom Unlimited Data 500, unlimited high-speed at AED 300.</li>
        <li><strong>Calls to one country only</strong> (e.g. India or Pakistan suppliers): Unlimited 1 Country 325.</li>
        <li><strong>Back-office / accounts line:</strong> Freedom Plan 250 at AED 188, keep costs lean where data is light.</li>''',
    faq_heading="Etisalat Business Postpaid Plans, FAQ",
    faqs=[
        ("What is the best Etisalat plan for a small business?",
         "For most SMBs the Unlimited Calls 600 Flexi at AED 360/month is the best all-rounder,50GB data and unlimited flexi minutes that work both locally and internationally, which suits owners who call overseas suppliers. Lighter back-office lines can sit on the Freedom Plan 250 at AED 188 to keep costs down."),
        ("Can I set up multiple Etisalat business lines on one account?",
         "Yes. We can arrange several Etisalat postpaid lines for one company, each on the tier that fits the role, with a free VIP number on customer-facing lines, and deliver every SIM the same day. Message us on WhatsApp +971 56 902 8087 with how many lines you need."),
        ("Which Etisalat plan is best for calling international suppliers?",
         "If you call one country constantly, the Unlimited 1 Country 325 gives unlimited calls to that country. If suppliers are spread across several countries, the Unlimited Calls 600 Flexi (AED 360) gives unlimited flexi minutes that work internationally as well as locally."),
        ("Do business plans come with a VIP number?",
         "Yes, eligible plans include a free VIP number (Silver, Gold or Platinum depending on tier), which is useful for customer-facing business lines. Browse the live inventory at postpaidplans.com/choose-number and we will deliver the SIMs the same day."),
        ("Can I register Etisalat business lines under a trade licence?",
         "Yes. Etisalat supports business registrations with trade-licence documentation. Tell us your company details on WhatsApp +971 56 902 8087 and we will handle the business paperwork alongside same-day SIM delivery."),
        ("Is there a contract on Etisalat business plans?",
         "Etisalat postpaid plans carry a commitment of 12 to 24 months, depending on the plan and the VIP number you choose, which underpins the pricing and any bundled VIP number. We confirm the exact term for each line before your company orders."),
        ("Are business plan prices inclusive of VAT?",
         "Listed prices are set by Etisalat and exclude 5% VAT, which is added to telecom services on your bill. VAT-registered companies account for that VAT in the normal way, we simply pass on Etisalat's price with no dealer mark-up."),
        ("Can we port our company's existing numbers to Etisalat?",
         "Yes. Business number portability lets you move existing company numbers, including from du, onto Etisalat postpaid plans, with each line staying active until its switch completes. We coordinate the paperwork with you."),
        ("Do Etisalat business plans support eSIM for our team?",
         "Yes, Etisalat supports eSIM on compatible devices, which is handy for quickly provisioning a new team member. Tell us at order which lines should be eSIM and we will set them up accordingly."),
    ],
    cta_h2='Equip your team with the right <span class="gold-text">Etisalat business plans</span>',
    cta_p="Tell us how many lines you need and how your team uses data and calls, we will build a cost-effective Etisalat setup with VIP numbers and deliver every SIM the same day.",
    cta_ctx="Hi, please help me set up Etisalat business postpaid plans for my company.",
    order=["unlcalls600","gold500","unldata500","unl1country","local1200","platinum","freedom250","newfreedom260","unllocal325","freedom325","emirati"],
))

# 5) BEST UNLIMITED DATA PLAN
PAGES.append(dict(
    slug="best-etisalat-unlimited-data-plan",
    ctx="",
    title="Best Etisalat Unlimited Data Plan in the UAE 2026 | From AED 300",
    meta_desc="The best Etisalat (e&) unlimited data plan in the UAE, unlimited high-speed data from AED 300/month with flexi minutes and a free VIP number. Official e& partner, same-day SIM delivery.",
    keywords="etisalat unlimited data, etisalat unlimited data plan, best etisalat unlimited data plan, etisalat uae unlimited data plans 2026, unlimited data plan uae, etisalat unlimited data package",
    breadcrumb="Best Etisalat Unlimited Data Plan",
    lb_name="Postpaid Plans UAE, Best Etisalat Unlimited Data Plan",
    lb_desc="Compare and order the best Etisalat (e&) unlimited data postpaid plans in the UAE, unlimited high-speed data from AED 300/month with flexi minutes and a free VIP number, delivered same day with no dealer mark-up.",
    itemlist_name="Best Etisalat Unlimited Data Plans",
    h1='Best Etisalat <span class="hl">Unlimited Data</span> Plan in the UAE',
    lead="If you tether a laptop, stream in HD or simply never want to think about a data cap again, you want true unlimited high-speed data, not just “non-stop.” Here is the difference, the three Etisalat (e&amp;) plans that give genuinely unlimited data, and which one is the best value for how you actually use your phone.",
    quick_answer="The best-value Etisalat unlimited data plan is the <strong>Freedom Unlimited Data 500 at AED 300/month</strong> (down from AED 600), unlimited high-speed data, 1,000 flexi minutes, 5GB roaming and a free Silver VIP number. For unlimited data <em>plus</em> unlimited local and international calls, step up to the <strong>Gold Plan 500</strong> or the <strong>Platinum Plan</strong>. All include a free VIP number and same-day delivery.",
    prose='''<h2>“Non-stop” vs genuinely unlimited high-speed data</h2>
      <p>This is the one distinction that decides the plan. Etisalat's cheaper Freedom plans give <strong>non-stop</strong> data, you stay connected at a steady speed with no hard cut-off, which is perfect for browsing, messaging, maps and social media. The plans on this page give <strong>unlimited high-speed</strong> data, which holds full speed for heavy use: HD/4K streaming, video calls all day, tethering a laptop, large downloads and gaming.</p>
      <p>The value pick is clear. The Freedom Unlimited Data 500 dropped from AED 600 to AED 300, which makes unlimited high-speed data genuinely affordable and is why it is our most recommended plan for power users. You only need to go higher, to the Gold Plan 500 or Platinum, if you also want unlimited <em>calling</em>, local and international, bundled in. Every one of these comes with a free VIP number, so you can secure a memorable line at the same time.</p>''',
    table_heading="Etisalat unlimited data plans compared",
    which_heading="Which unlimited data plan is right for you?",
    which_list='''<li><strong>Best value, heavy data user:</strong> Freedom Unlimited Data 500, unlimited high-speed at AED 300 with a free Silver number.</li>
        <li><strong>Unlimited data + unlimited calls:</strong> Gold Plan 500, everything unlimited, local and international, with a free Gold number.</li>
        <li><strong>The absolute top tier:</strong> Platinum Plan, unlimited everything, 20GB roaming and a free Platinum number.</li>
        <li><strong>Do not actually need unlimited?</strong> Non-stop data on the Freedom Plan 250 (AED 188) may be all you need, see our cheapest plan guide.</li>''',
    faq_heading="Best Etisalat Unlimited Data Plan, FAQ",
    faqs=[
        ("Which Etisalat plan has the best unlimited data?",
         "The Freedom Unlimited Data 500 at AED 300/month (down from AED 600) is the best-value unlimited high-speed data plan, unlimited data, 1,000 flexi minutes, 5GB roaming and a free Silver VIP number. The Gold Plan 500 and Platinum Plan also include unlimited data plus unlimited local and international calls."),
        ("What is the difference between non-stop and unlimited data on Etisalat?",
         "Non-stop data (on the cheaper Freedom plans) keeps you connected at a steady speed with no hard cut-off, fine for browsing, messaging and maps. Unlimited high-speed data (Freedom Unlimited Data 500 and above) holds full speed for heavy use like HD streaming, video calls, tethering and gaming."),
        ("How much is Etisalat unlimited data per month?",
         "Unlimited high-speed data starts at AED 300/month on the Freedom Unlimited Data 500 (reduced from AED 600). Plans that add unlimited local and international calling on top, the Gold Plan 500 and Platinum Plan, are AED 500 and AED 1,000/month respectively."),
        ("Does the unlimited data plan include a free number?",
         "Yes. The Freedom Unlimited Data 500 includes a free Silver VIP number, the Gold Plan 500 includes a Gold number, and the Platinum Plan includes a Platinum number. Browse the live inventory at postpaidplans.com/choose-number and we deliver the SIM the same day."),
        ("Is Etisalat unlimited data truly unlimited, or does it slow down?",
         "These plans give unlimited high-speed data with no fixed monthly cap, built for HD streaming, video calls, tethering and gaming. As on any network, Etisalat applies a fair-usage policy to protect the network, but for normal heavy personal use you will not hit the hard cut-off you would on a capped plan."),
        ("Is there a contract on the Etisalat unlimited data plan?",
         "Etisalat postpaid plans carry a commitment of 12 to 24 months, depending on the plan and the VIP number you choose, which is what makes the discounted AED 300 rate and the free VIP number possible. We confirm the exact term before you order."),
        ("Does the AED 300 unlimited data price include VAT?",
         "No, the AED 300 price is set by Etisalat and excludes 5% VAT, which UAE law adds to telecom services on your monthly bill. There is no dealer mark-up on top."),
        ("What happens to the AED 300 price after the promotion?",
         "AED 300 is a promotional rate discounted from the AED 600 list price. After the promo period the plan continues at its regular price. Etisalat sets and can change pricing, so we confirm the current rate and promo terms when you order."),
        ("Can I keep my current number on an unlimited data plan?",
         "Yes. You can port your existing mobile number, including from du, onto any of these unlimited data plans, and your line keeps working until the switch completes. We guide you through the official porting request."),
        ("Does the unlimited data plan support eSIM?",
         "Yes, Etisalat supports eSIM on compatible devices. Tell us at order and we will set up an eSIM instead of a physical SIM where your phone supports it."),
    ],
    cta_h2='Get unlimited Etisalat data from <span class="gold-text">AED 300</span>',
    cta_p="Lock the Freedom Unlimited Data 500 with a free Silver number and we will deliver the SIM the same day, or message us and we will match the right unlimited plan to how you use your phone.",
    cta_ctx="Hi, I'd like the best Etisalat unlimited data plan.",
    order=["unldata500","gold500","platinum","local1200","unlcalls600","unllocal325","unl1country","freedom250","newfreedom260","freedom325","emirati"],
))


def build(page):
    html = HEAD
    rows = render_rows(page["order"], page["ctx"])
    itemlist = render_itemlist(page["order"], page["itemlist_name"])
    faq_schema = render_faq_schema(page["faqs"])
    faq_html = render_faq_html(page["faqs"])
    repl = {
        "@@SLUG@@": page["slug"],
        "@@TITLE@@": page["title"],
        "@@META_DESC@@": page["meta_desc"],
        "@@KEYWORDS@@": page["keywords"],
        "@@BREADCRUMB@@": page["breadcrumb"],
        "@@LB_NAME@@": page["lb_name"],
        "@@LB_DESC@@": page["lb_desc"],
        "@@ITEMLIST_NAME@@": page["itemlist_name"],
        "@@H1@@": page["h1"],
        "@@LEAD@@": page["lead"],
        "@@HERO_WA@@": wa(page["cta_ctx"]),
        "@@QUICK_ANSWER@@": page["quick_answer"],
        "@@PROSE@@": page["prose"],
        "@@TABLE_HEADING@@": page["table_heading"],
        "@@PLAN_ROWS@@": rows,
        "@@PLAN_ITEMLIST@@": itemlist,
        "@@WHICH_HEADING@@": page["which_heading"],
        "@@WHICH_LIST@@": page["which_list"],
        "@@FAQ_HEADING@@": page["faq_heading"],
        "@@FAQ_SCHEMA@@": faq_schema,
        "@@FAQ_HTML@@": faq_html,
        "@@CTA_H2@@": page["cta_h2"],
        "@@CTA_P@@": page["cta_p"],
        "@@CTA_WA@@": wa(page["cta_ctx"]),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html


def main():
    for page in PAGES:
        d = os.path.join(ROOT, page["slug"])
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, "index.html")
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(build(page))
        print("wrote", out)
    # sanity: no unreplaced tokens
    for page in PAGES:
        h = build(page)
        if "@@" in h:
            import re
            print("WARNING unreplaced tokens in", page["slug"], set(re.findall(r"@@[A-Z_]+@@", h)))
    print("done:", len(PAGES), "pages")


if __name__ == "__main__":
    main()
