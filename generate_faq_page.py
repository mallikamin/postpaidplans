# -*- coding: utf-8 -*-
"""
generate_faq_page.py — builds the consolidated /faq/ hub for postpaidplans.com.

A POSTPAID-ONLY FAQ hub (deliberately NOT the sisters' VIP-number-pattern FAQ):
plans & pricing, data/calls/roaming, the free bundled number, eligibility,
porting & eSIM, billing/contract, ordering/delivery, and the authorized-dealer
story. Every category funnels internal links to the money pages (the 5 plan
landing pages + /choose-number/ + the du-vs-e& comparison blog) so the hub acts
as an internal-link/AEO asset, not a doorway.

Schema (FAQPage) answer text is auto-stripped of the inline <a>/<strong> tags so
the JSON-LD stays clean while the visible answers keep their links.

Run:  python generate_faq_page.py   -> writes faq/index.html
Excluded from public serving via .assetsignore (*.py).
"""
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
WA = "971569028087"


def wa(text):
    return "https://wa.me/%s?text=%s" % (WA, quote(text))


def strip_tags(html):
    """Plain text for the JSON-LD answer (drop <a>/<strong>, collapse spaces)."""
    txt = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\s+", " ", txt).strip()


def esc_json(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


# ----------------------------- FAQ CONTENT -----------------------------------
# (category_id, category_title, intro_html, [ (question, html_answer), ... ])
CATEGORIES = [
    ("plans", "Etisalat postpaid plans &amp; pricing",
     "Genuine Etisalat (e&amp;) postpaid plans from AED 188 to AED 1,000 a month, at Etisalat's own price with no dealer mark-up.",
     [
        ("How many Etisalat postpaid plans are there, and what do they cost?",
         "There are 11 Etisalat (e&amp;) postpaid plans, from the Freedom Plan 250 at <strong>AED 188/month</strong> up to the Platinum Plan at AED 1,000/month. Compare them all side by side on the <a href=\"/#compare\">homepage comparison table</a>, or run the <a href=\"/#finder\">Plan Finder</a> to get a recommendation in 60 seconds."),
        ("What is the cheapest Etisalat postpaid plan?",
         "The cheapest is the <strong>Freedom Plan 250 at AED 188/month</strong> (discounted from AED 250). It includes non-stop data, 1,000 local minutes, 2GB roaming and a free Silver VIP number. See the full breakdown on our <a href=\"/cheapest-etisalat-postpaid-plan/\">cheapest Etisalat plan</a> guide."),
        ("Is there an Etisalat plan under AED 200 per month?",
         "Yes, two: the Freedom Plan 250 at AED 188 and the New Freedom Plan 260 at AED 195. Both include non-stop data, 1,000 local minutes and a free Silver number. Details on our <a href=\"/etisalat-plans-under-200-aed/\">plans under AED 200</a> guide."),
        ("Why are your prices the same as Etisalat's official prices?",
         "Because we are an <strong>authorized Etisalat dealer</strong>, plans cost exactly what they cost buying direct. You pay nothing extra, and you get a free VIP number, same-day delivery and WhatsApp support on top."),
        ("Do the prices include VAT?",
         "Listed prices are set by Etisalat and <strong>exclude 5% VAT</strong>, which UAE law adds to telecom services on your monthly bill. There is no dealer mark-up beyond Etisalat's own price."),
        ("Is the AED 188 price permanent?",
         "AED 188 is a promotional discount on the Freedom Plan 250 (regular AED 250). After the promotional period the plan continues at its regular price. Etisalat sets and can change pricing, so we confirm the current rate and promo terms when you order."),
     ]),

    ("data-calls", "Data, calls &amp; roaming",
     "Unlimited high-speed data, flexi minutes that work abroad, and roaming bundled by tier.",
     [
        ("Which Etisalat plan has the best unlimited data?",
         "The <strong>Freedom Unlimited Data 500 at AED 300/month</strong> (down from AED 600) is the best-value unlimited high-speed data plan. The Gold Plan 500 and Platinum Plan add unlimited local and international calls on top. See our <a href=\"/best-etisalat-unlimited-data-plan/\">best unlimited data plan</a> guide."),
        ("What is the difference between non-stop and unlimited high-speed data?",
         "Non-stop data (on the cheaper Freedom plans) keeps you connected at a steady speed with no hard cut-off, which is fine for browsing, messaging and maps. <strong>Unlimited high-speed</strong> data holds full speed for heavy use such as HD streaming, video calls, tethering a laptop and gaming."),
        ("Is the data really unlimited, or does it slow down?",
         "The unlimited high-speed plans have no fixed monthly cap. As on any network, Etisalat applies a fair-usage policy to protect the network, but for normal heavy personal use you will not hit the hard cut-off you would on a capped plan."),
        ("Which plan is best for international calls to India, Pakistan or the Philippines?",
         "The Unlimited 1 Country 325 gives <strong>unlimited calls to one chosen country</strong>; the Unlimited Calls 600 Flexi (AED 360) gives unlimited flexi minutes that work locally and internationally. See our <a href=\"/international-calling-plans/\">international calling plans</a> or the <a href=\"/best-etisalat-plan-calling-india/\">calling India</a> guide."),
        ("Do Etisalat postpaid plans include roaming?",
         "Most Freedom plans include a roaming data allowance that scales with the tier (commonly 2GB to 5GB, and 20GB on Platinum). Confirm the exact roaming bundle for your chosen plan when you order."),
        ("What does ‘Flexi’ mean in an Etisalat plan name?",
         "Flexi plans let you use your bundled minutes flexibly for local or international calls, while Local plans dedicate the minutes to UAE calls only."),
     ]),

    ("free-number", "Your free VIP number",
     "Every eligible plan comes with a free Etisalat VIP number, Silver, Gold or Platinum by tier.",
     [
        ("Do Etisalat postpaid plans come with a free number?",
         "Yes. Most plans include a <strong>free VIP number</strong>: a Silver on standard plans, a Gold on the Gold Plan 500, and a Platinum on the top tier. The number is bundled with the plan, with no separate number fee."),
        ("Is the VIP number really free?",
         "Yes. You never pay a separate one-time fee for the number. It is included with the postpaid plan you choose."),
        ("How do I pick my number?",
         "Browse the live inventory of 2,500+ numbers at <a href=\"/choose-number/\">Choose Number</a>, filter by the digits or pattern you want, and lock a memorable line before you order."),
        ("Can I keep my existing number and still get a VIP number?",
         "Yes. A popular setup is to port your current number onto a plan and add a new VIP number as a second line. Tell us on WhatsApp +971 56 902 8087 and we will arrange both."),
     ]),

    ("eligibility", "Eligibility &amp; documents",
     "Postpaid is for Emirates ID holders. Here is exactly what qualifies.",
     [
        ("What documents do I need for an Etisalat postpaid plan?",
         "Just your <strong>valid original Emirates ID</strong>, plus a payment card for the first bill on delivery. We handle the rest."),
        ("Can I get a postpaid plan on a tourist visa?",
         "A postpaid line requires a valid Emirates ID, so a tourist visa generally does not qualify. If you are mid-residency-process, message us and we will advise on timing."),
        ("Can I get a plan while my residency visa is still processing?",
         "You will need the Emirates ID issued first. As soon as you have it, we can deliver the same day."),
        ("Is there a minimum age for an Etisalat postpaid line?",
         "Yes. You must be 18 or over with your own Emirates ID to register a postpaid line. A line for a child is registered under a parent's Emirates ID."),
        ("Can I register a line under my company?",
         "Yes. Business registrations are possible with trade-licence documentation. See our <a href=\"/etisalat-business-postpaid-plans/\">business postpaid plans</a> guide or message us for the company process."),
     ]),

    ("porting-esim", "Porting &amp; eSIM",
     "Bring your number across (including from du) and go physical or eSIM.",
     [
        ("Can I keep my current number and move it to Etisalat?",
         "Yes. UAE number portability lets you bring your existing mobile number onto an Etisalat postpaid plan. Your line keeps working until the switch completes."),
        ("How do I port from du to Etisalat?",
         "Message us on WhatsApp and we will guide you through the official porting request. Your <strong>du</strong> number keeps working until the switch completes. See our honest <a href=\"/blog/etisalat-vs-du-postpaid-plans-uae/\">Etisalat vs du comparison</a> if you are still deciding."),
        ("Does porting cost anything?",
         "There is no fee from us for assisting your port. You simply take up your new Etisalat postpaid plan."),
        ("Do Etisalat postpaid plans support eSIM?",
         "Yes. Etisalat supports <strong>eSIM</strong> on compatible devices. Tell us at order and we will set up an eSIM instead of a physical SIM where your phone supports it."),
        ("Can I switch my physical SIM to eSIM later?",
         "Yes. SIM-to-eSIM conversion is available through Etisalat channels once your line is active."),
     ]),

    ("billing-contract", "Billing, contract &amp; promo",
     "What you commit to, how you pay, and what happens after the discount.",
     [
        ("Is there a contract or commitment on Etisalat postpaid plans?",
         "Etisalat postpaid plans carry a <strong>commitment of 12 to 24 months, depending on the plan and the VIP number you choose</strong>. That commitment is what makes the discounted pricing and the free VIP number possible, and we confirm the exact term for your plan before you order."),
        ("What happens if I cancel before the term ends?",
         "Early exit triggers Etisalat's standard early-termination terms. Message us before deciding, because sometimes a downgrade or transfer solves it better."),
        ("How do I pay my monthly bill?",
         "Through the My Etisalat UAE app, autopay, online banking, or any Etisalat payment channel. Etisalat bills you directly each month."),
        ("What happens after the 6-month promotional price ends?",
         "Your plan continues at its regular price (for example, AED 250 on the entry plan after the AED 188 promo). We confirm the current promo terms at order."),
        ("Can I upgrade or downgrade my plan later?",
         "You can move up to a higher plan at any time and keep your number. Downgrades during the commitment period are restricted by Etisalat's terms, so message us with your situation and we will tell you what is possible."),
     ]),

    ("ordering", "Ordering, delivery &amp; activation",
     "From choosing a plan to a live SIM at your door, usually the same day.",
     [
        ("How do I order an Etisalat plan from you?",
         "Run the <a href=\"/#finder\">Plan Finder</a> or <a href=\"/#compare\">compare plans</a>, pick a free number at <a href=\"/choose-number/\">Choose Number</a>, then confirm on WhatsApp +971 56 902 8087. It takes a couple of minutes."),
        ("Do I pay anything online?",
         "No. There is no online payment. You pay your plan's first bill <strong>by card on delivery</strong>; the rider carries a card machine, so no cash is needed."),
        ("How fast is delivery?",
         "Same-day delivery is available across the UAE, typically within 24 hours of your order and verification."),
        ("What should I have ready at delivery?",
         "Your <strong>original Emirates ID</strong> and your payment card. That is it."),
        ("Which areas do you deliver to?",
         "All seven emirates: Dubai, Abu Dhabi, Sharjah, Ajman, Ras Al Khaimah, Fujairah and Umm Al Quwain. See, for example, our <a href=\"/etisalat-postpaid-plans-dubai/\">plans in Dubai</a> page."),
     ]),

    ("about", "Why order through us",
     "Who we are, and why ordering through us is safe.",
     [
        ("Are you an official Etisalat dealer?",
         "Yes. We are an <strong>Official e&amp; Partner and Authorized Etisalat Dealer</strong> based in Dubai. Plans are identical to Etisalat's official pricing, and our service layer of plan advice, number curation, WhatsApp support and free delivery sits on top."),
        ("Is postpaidplans.com legitimate?",
         "Yes. Authorized dealer, genuine 5.0-star Google reviews, no online payment ever requested (card on delivery only), and verification handled by Etisalat's own department. Read our <a href=\"/reviews/\">customer reviews</a>."),
        ("How are you different from buying at an Etisalat store?",
         "Same plans and prices, but you compare every plan with our free <a href=\"/#finder\">Plan Finder</a>, pick a VIP number from your phone, and the SIM comes to your door the same day, free."),
        ("Do you sell du plans?",
         "No. We are an Etisalat-focused dealer, so everything we set up runs on the Etisalat network. We do publish an honest <a href=\"/blog/etisalat-vs-du-postpaid-plans-uae/\">Etisalat vs du comparison</a> to help you decide, and it concludes from our authorized-Etisalat-dealer point of view."),
        ("How do I contact you fastest?",
         "WhatsApp is fastest: <strong>+971 56 902 8087</strong>, 9am to 9pm UAE time, seven days. We reply within minutes during support hours."),
     ]),
]


def all_pairs():
    for _cid, _ct, _intro, items in CATEGORIES:
        for q, a in items:
            yield q, a


def render_chipbar():
    chips = []
    for cid, ct, _intro, _items in CATEGORIES:
        chips.append('<a href="#%s">%s</a>' % (cid, ct))
    return "\n        ".join(chips)


def render_sections():
    out = []
    for cid, ct, intro, items in CATEGORIES:
        acc = []
        for q, a in items:
            acc.append(
                '<div class="faq-item"><button class="faq-q" aria-expanded="false">%s'
                '<span class="pm">+</span></button><div class="faq-a"><p>%s</p></div></div>' % (q, a))
        out.append(
            '<section class="faq-cat" id="%s" style="scroll-margin-top:84px;margin-bottom:2.4rem">\n'
            '      <h2 style="font-size:clamp(1.3rem,2.4vw,1.7rem);margin-bottom:.4rem">%s</h2>\n'
            '      <p style="color:var(--muted);margin-bottom:1rem">%s</p>\n'
            '      %s\n'
            '    </section>' % (cid, ct, intro, "\n      ".join(acc)))
    return "\n\n    ".join(out)


def render_faq_schema():
    out = []
    for q, a in all_pairs():
        out.append('{ "@type": "Question", "name": "%s", "acceptedAnswer": { "@type": "Answer", "text": "%s" } }'
                   % (esc_json(strip_tags(q)), esc_json(strip_tags(a))))
    return ",\n      ".join(out)


TOTAL = sum(len(items) for _c, _t, _i, items in CATEGORIES)

PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js): GA4 (postpaidplans dedicated property). -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-B4813N8J6J"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-B4813N8J6J');
  </script>
  <!-- Meta Pixel (postpaidplans dedicated dataset 3266474320203798). -->
  <script>
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', '3266474320203798');
    fbq('track', 'PageView');
  </script>

  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Etisalat Postpaid Plans FAQ (@@TOTAL@@ Questions) | Postpaid Plans UAE</title>
  <meta name="description" content="Every question about Etisalat postpaid plans answered by an authorized e& dealer: pricing, unlimited data, contracts, VAT, eligibility, porting from du, eSIM, delivery and billing. @@TOTAL@@ FAQs.">
  <meta name="keywords" content="etisalat postpaid plans faq, etisalat plan questions, etisalat postpaid contract, etisalat plan vat, port du to etisalat, etisalat esim, etisalat plan eligibility uae">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#E30613">
  <link rel="canonical" href="https://postpaidplans.com/faq/">
  <link rel="alternate" hreflang="en" href="https://postpaidplans.com/faq/">
  <link rel="alternate" hreflang="x-default" href="https://postpaidplans.com/faq/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Etisalat Postpaid Plans FAQ (@@TOTAL@@ Questions) | Postpaid Plans UAE">
  <meta property="og:description" content="Pricing, unlimited data, contracts, VAT, eligibility, porting from du, eSIM, delivery and billing, answered by an authorized Etisalat dealer.">
  <meta property="og:url" content="https://postpaidplans.com/faq/">
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

  <!-- Structured Data: BreadcrumbList -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://postpaidplans.com/" },
      { "@type": "ListItem", "position": 2, "name": "FAQ", "item": "https://postpaidplans.com/faq/" }
    ]
  }
  </script>
</head>
<body>
  <header><div class="wrap nav"><a href="/" class="brand"><span class="dot"></span>Postpaid<b>Plans</b>&nbsp;UAE</a><nav class="nav-links"><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a><a href="/premium-numbers-uae/">VIP Numbers</a><a href="/blog/">Blog</a><a href="/choose-number/">Choose Number</a><a href="/about/">About</a></nav><div class="nav-cta"><a href="https://wa.me/971569028087" target="_blank" rel="noopener noreferrer" class="btn btn-wa">WhatsApp</a></div><button class="burger" id="burger" aria-label="Open menu">&#9776;</button></div><div class="mobile-menu" id="mobileMenu"><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a><a href="/premium-numbers-uae/">VIP Numbers</a><a href="/blog/">Blog</a><a href="/choose-number/">Choose Number</a><a href="/about/">About Us</a></div></header>

  <div class="wrap"><div class="crumb"><a href="/">Home</a> › <span>FAQ</span></div></div>

  <section class="hero"><div class="wrap hero-inner"><span class="eyebrow">⚡ Official e&amp; Partner · Authorized Etisalat Dealer</span><h1>Etisalat Postpaid Plans <span class="hl">FAQ</span></h1><p class="lead">@@TOTAL@@ real questions about Etisalat (e&amp;) postpaid plans, answered plainly by an authorized Etisalat dealer: pricing, unlimited data, contracts, VAT, eligibility, porting from du, eSIM, delivery and billing.</p><div class="hero-cta"><a href="/#finder" class="btn btn-red btn-lg">Find my plan in 60s →</a><a href="@@HERO_WA@@" target="_blank" rel="noopener noreferrer" class="btn btn-ghost btn-lg">Talk to a LIVE Etisalat Specialist</a></div><div class="trust-row"><span>✓ Same-day delivery</span><span>✓ Free VIP number</span><span>✓ All UAE</span></div></div></section>

  <section class="block"><div class="wrap" style="max-width:60rem">
    <div class="answer"><h3>Jump to a topic</h3><p>Everything below is about Etisalat <strong>postpaid</strong> plans. Pick a category or scroll through, and when you are ready the <a href="/#finder">Plan Finder</a> recommends a plan in 60 seconds.</p></div>
    <div class="link-chips" style="margin-bottom:2rem">
        @@CHIPBAR@@
    </div>

    @@SECTIONS@@

    <h2 style="font-size:clamp(1.3rem,2.4vw,1.7rem);margin:2.4rem 0 .6rem">Still deciding? Start here</h2>
    <div class="link-chips">
        <a href="/#finder">Plan Finder</a>
        <a href="/#compare">Compare Plans</a>
        <a href="/best-etisalat-unlimited-data-plan/">Unlimited Data Plans</a>
        <a href="/best-etisalat-plan-for-family/">Best Family Plan</a>
        <a href="/etisalat-plans-under-200-aed/">Plans Under AED 200</a>
        <a href="/cheapest-etisalat-postpaid-plan/">Cheapest Plan</a>
        <a href="/etisalat-business-postpaid-plans/">Business Plans</a>
        <a href="/international-calling-plans/">International Calling</a>
        <a href="/blog/etisalat-vs-du-postpaid-plans-uae/">Etisalat vs Du</a>
        <a href="/reviews/">Reviews</a>
        <a href="/choose-number/">Browse live numbers</a>
    </div>
  </div></section>

  <section class="block bg-soft"><div class="wrap"><div class="cta-band"><h2>Got a question we did not cover?</h2><p>Message a live Etisalat specialist on WhatsApp. We answer plan, pricing, porting and eligibility questions in minutes, 9am to 9pm UAE time.</p><a href="@@HERO_WA@@" class="btn btn-wa btn-lg" target="_blank" rel="noopener noreferrer">Talk to a LIVE Etisalat Specialist now</a></div></div></section>

  <footer><div class="wrap"><div class="foot-grid"><div><div class="foot-brand">Postpaid<b>Plans</b> UAE</div><p style="max-width:24rem">Official e&amp; Partner &amp; Authorized Etisalat Dealer helping UAE residents pick the right Etisalat postpaid plan and a premium VIP number, fast. Same-day SIM delivery in Dubai, Abu Dhabi &amp; Sharjah.</p><a href="https://wa.me/971569028087" target="_blank" rel="noopener noreferrer" class="btn btn-wa" style="margin-top:1rem">Talk to a LIVE Etisalat Specialist</a><div style="display:inline-flex;align-items:center;gap:.45rem;margin-top:.9rem;font-size:.8rem;color:rgba(255,255,255,.72);background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:.4rem .7rem">\U0001f512 SSL secured · Official e&amp; Partner</div><div style="font-size:.82rem;color:rgba(255,255,255,.62);margin-top:.85rem;line-height:1.55">&#128205; Al Zarooni Building, Office 1904, Ayal Nasir, Deira, Dubai, UAE<br><a href="https://www.google.com/maps?cid=11719519233119757422" target="_blank" rel="noopener noreferrer" style="color:var(--gold)">&#9733; 5.0 Read our Google reviews &rarr;</a></div></div><div><h4>Plan guides</h4><a href="/best-etisalat-unlimited-data-plan/">Unlimited Data Plan</a><a href="/best-etisalat-plan-for-family/">Best Family Plan</a><a href="/etisalat-plans-under-200-aed/">Plans Under AED 200</a><a href="/cheapest-etisalat-postpaid-plan/">Cheapest Plan</a><a href="/etisalat-business-postpaid-plans/">Business Plans</a><a href="/etisalat-postpaid-plans-dubai/">Plans in Dubai</a></div><div><h4>Explore</h4><a href="/#finder">Plan Finder</a><a href="/#compare">Compare Plans</a><a href="/choose-number/">Choose Your Number</a><a href="/faq/">FAQ</a><a href="/blog/">Blog</a></div><div><h4>Company</h4><a href="/about/">About Us</a><a href="/reviews/">Reviews</a><a href="/privacy/">Privacy Policy</a><a href="/refund-policy/">Refund &amp; Contact</a><a href="/ar/">العربية</a></div></div><p class="disclaimer">© 2026 postpaidplans.com. Postpaid Plans UAE is an Official e&amp; Partner and Authorized Etisalat Dealer, operated independently; we are not Emirates Telecommunications Group Company (e&amp;) PJSC itself. "Etisalat" and "e&amp;" are trademarks of their respective owners. Prices are set by Etisalat and may change; final pricing confirmed at order.</p></div></footer>

  <a class="wa-fab" href="https://wa.me/971569028087" target="_blank" rel="noopener noreferrer" aria-label="Talk to a live Etisalat specialist on WhatsApp"><svg viewBox="0 0 24 24"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38c1.45.79 3.08 1.21 4.79 1.21h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0012.04 2zm5.8 14.13c-.24.68-1.42 1.31-1.95 1.36-.5.05-1.13.07-1.82-.11-.42-.13-.96-.31-1.65-.61-2.9-1.25-4.79-4.17-4.94-4.37-.14-.2-1.18-1.57-1.18-2.99 0-1.42.74-2.12 1.01-2.41.26-.29.57-.36.76-.36l.55.01c.18.01.42-.07.65.5.24.57.81 1.99.88 2.13.07.14.12.31.02.5-.09.2-.14.31-.28.48-.14.17-.29.37-.42.5-.14.14-.28.29-.12.57.16.28.72 1.18 1.54 1.91 1.06.95 1.95 1.24 2.23 1.38.28.14.44.12.6-.07.16-.2.69-.81.88-1.08.18-.28.37-.23.62-.14.25.09 1.6.76 1.87.9.28.14.46.2.53.32.07.11.07.66-.17 1.34z"/></svg></a>
  <script>var b=document.getElementById('burger'),m=document.getElementById('mobileMenu');if(b)b.addEventListener('click',function(){m.style.display=m.style.display==='flex'?'none':'flex';});
  // Fire a Lead event (GA4 + Meta Pixel) on any WhatsApp click (real conversion signal).
  document.addEventListener('click',function(e){var a=e.target.closest('a[href*="wa.me"]');if(a){try{if(typeof gtag==='function')gtag('event','generate_lead',{method:'whatsapp'});}catch(x){}try{if(typeof fbq==='function')fbq('track','Lead',{content_name:'whatsapp_click'});}catch(x){}return;}
  var q=e.target.closest('.faq-q');if(!q)return;var o=q.getAttribute('aria-expanded')==='true';var ans=q.nextElementSibling;q.setAttribute('aria-expanded',!o);ans.style.maxHeight=o?'0':(ans.scrollHeight+40)+'px';});</script>
</body></html>'''


def build():
    html = PAGE
    repl = {
        "@@TOTAL@@": str(TOTAL),
        "@@HERO_WA@@": wa("Hi, I have a question about Etisalat postpaid plans."),
        "@@CHIPBAR@@": render_chipbar(),
        "@@SECTIONS@@": render_sections(),
        "@@FAQ_SCHEMA@@": render_faq_schema(),
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html


def main():
    d = os.path.join(ROOT, "faq")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "index.html")
    h = build()
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(h)
    print("wrote", out, "(%d FAQs)" % TOTAL)
    if "@@" in h:
        print("WARNING unreplaced tokens:", set(re.findall(r"@@[A-Z_]+@@", h)))


if __name__ == "__main__":
    main()
