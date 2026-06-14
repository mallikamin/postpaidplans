# -*- coding: utf-8 -*-
"""
generate_calling_pages.py — international-calling intent pages, ONE PER NATIONALITY,
targeting the UAE's expat communities. Anchored on the genuine Etisalat "Unlimited 1
Country" plan (unlimited calls to one whole country) — NO invented per-minute rates.

Anti-duplication: each country carries real, distinct data (languages, time difference
to the UAE, origin regions, festivals, a native greeting, community context). The
builder rotates between several prose/quick-answer/FAQ templates by index so pages are
genuinely different in wording and structure, not name-swapped clones. (Earlier city
pages were 88% identical — the number-pages mistake; this fixes it.)

Country hubs: /best-etisalat-plan-calling-<slug>/
Marquee cities: /dubai-to-<city>-calling-plan/   (kept, rewritten unique)
Directory hub:  /international-calling-plans/

Run:  python generate_calling_pages.py
"""
import os
from generate_plan_pages import build, ROOT, wa, HEAD

CALL_ORDER = ["unl1country", "unlcalls600", "gold500", "platinum", "unldata500",
              "unllocal325", "freedom250", "newfreedom260", "freedom325", "local1200", "emirati"]

# Real per-country data. tz = honest time offset vs the UAE (UTC+4). community = qualitative
# (no invented population numbers). greeting/occasions/regions/langs are well-known facts.
COUNTRIES = [
 dict(slug="india", name="India", demonym="Indian", langs="Hindi, Malayalam, Tamil, Telugu and more",
   tz="1½ hours ahead of the UAE", greeting="Namaste", community="the largest expat community in the UAE",
   regions="Kerala, Tamil Nadu, Andhra Pradesh, Maharashtra and Punjab", occasions="Diwali, Eid and Onam"),
 dict(slug="pakistan", name="Pakistan", demonym="Pakistani", langs="Urdu, Punjabi, Pashto and Sindhi",
   tz="1 hour ahead of the UAE", greeting="As-salamu alaikum", community="one of the largest communities in the UAE",
   regions="Punjab, Khyber Pakhtunkhwa, Sindh and Azad Kashmir", occasions="Eid"),
 dict(slug="philippines", name="the Philippines", demonym="Filipino", langs="Filipino (Tagalog), Cebuano and more",
   tz="4 hours ahead of the UAE", greeting="Kumusta", community="a large and close-knit community in the UAE",
   regions="Luzon, the Visayas and Mindanao", occasions="Christmas and town fiestas", kabayan=True),
 dict(slug="bangladesh", name="Bangladesh", demonym="Bangladeshi", langs="Bengali",
   tz="2 hours ahead of the UAE", greeting="Assalamu alaikum", community="one of the largest communities in the UAE",
   regions="Dhaka, Chittagong and Sylhet", occasions="Eid and Pohela Boishakh"),
 dict(slug="sri-lanka", name="Sri Lanka", demonym="Sri Lankan", langs="Sinhala and Tamil",
   tz="1½ hours ahead of the UAE", greeting="Ayubowan", community="a large community in the UAE",
   regions="Colombo, Kandy and Jaffna", occasions="the Sinhala and Tamil New Year"),
 dict(slug="nepal", name="Nepal", demonym="Nepali", langs="Nepali",
   tz="1¾ hours ahead of the UAE", greeting="Namaste", community="a growing community in the UAE",
   regions="Kathmandu and Pokhara", occasions="Dashain and Tihar"),
 dict(slug="egypt", name="Egypt", demonym="Egyptian", langs="Arabic",
   tz="about 2 hours behind the UAE", greeting="As-salamu alaikum", community="a large Arab community in the UAE",
   regions="Cairo, Alexandria and Upper Egypt", occasions="Eid and Ramadan"),
 dict(slug="jordan", name="Jordan", demonym="Jordanian", langs="Arabic",
   tz="1 hour behind the UAE", greeting="As-salamu alaikum", community="a close Arab community in the UAE",
   regions="Amman, Irbid and Zarqa", occasions="Eid"),
 dict(slug="sudan", name="Sudan", demonym="Sudanese", langs="Arabic",
   tz="2 hours behind the UAE", greeting="As-salamu alaikum", community="a close community in the UAE",
   regions="Khartoum and Omdurman", occasions="Eid"),
 dict(slug="syria", name="Syria", demonym="Syrian", langs="Arabic",
   tz="1 hour behind the UAE", greeting="As-salamu alaikum", community="a close Arab community in the UAE",
   regions="Damascus and Aleppo", occasions="Eid"),
 dict(slug="lebanon", name="Lebanon", demonym="Lebanese", langs="Arabic",
   tz="1 hour behind the UAE", greeting="Marhaba", community="a close Arab community in the UAE",
   regions="Beirut, Tripoli and Sidon", occasions="Eid and Christmas"),
 dict(slug="morocco", name="Morocco", demonym="Moroccan", langs="Arabic and Amazigh",
   tz="about 3 hours behind the UAE", greeting="As-salamu alaikum", community="a community in the UAE",
   regions="Casablanca, Rabat and Marrakech", occasions="Eid"),
 dict(slug="yemen", name="Yemen", demonym="Yemeni", langs="Arabic",
   tz="1 hour behind the UAE", greeting="As-salamu alaikum", community="a close community in the UAE",
   regions="Sana'a, Aden and Taiz", occasions="Eid"),
 dict(slug="nigeria", name="Nigeria", demonym="Nigerian", langs="English, Yoruba, Igbo and Hausa",
   tz="3 hours behind the UAE", greeting="a warm hello", community="a growing community in the UAE",
   regions="Lagos, Abuja and Port Harcourt", occasions="Christmas and Eid"),
 dict(slug="kenya", name="Kenya", demonym="Kenyan", langs="Swahili and English",
   tz="1 hour behind the UAE", greeting="Jambo", community="a growing community in the UAE",
   regions="Nairobi and Mombasa", occasions="Christmas"),
 dict(slug="ethiopia", name="Ethiopia", demonym="Ethiopian", langs="Amharic",
   tz="1 hour behind the UAE", greeting="Selam", community="a community in the UAE",
   regions="Addis Ababa", occasions="Timkat and Christmas"),
 dict(slug="ghana", name="Ghana", demonym="Ghanaian", langs="English and Twi",
   tz="4 hours behind the UAE", greeting="Akwaaba", community="a community in the UAE",
   regions="Accra and Kumasi", occasions="Christmas"),
 dict(slug="uganda", name="Uganda", demonym="Ugandan", langs="English, Luganda and Swahili",
   tz="1 hour behind the UAE", greeting="a warm hello", community="a community in the UAE",
   regions="Kampala", occasions="Christmas"),
 dict(slug="indonesia", name="Indonesia", demonym="Indonesian", langs="Bahasa Indonesia",
   tz="3 to 4 hours ahead of the UAE", greeting="Halo", community="a community in the UAE",
   regions="Jakarta, Java and Sumatra", occasions="Eid (Lebaran)"),
 dict(slug="uk", name="the United Kingdom", demonym="British", langs="English",
   tz="3 to 4 hours behind the UAE", greeting="Hello", community="a large expat and business community in the UAE",
   regions="London, Manchester and Birmingham", occasions="Christmas"),
 dict(slug="usa", name="the United States", demonym="American", langs="English",
   tz="8 to 11 hours behind the UAE", greeting="Hi", community="an expat and business community in the UAE",
   regions="New York, California and Texas", occasions="Thanksgiving and Christmas"),
 dict(slug="canada", name="Canada", demonym="Canadian", langs="English and French",
   tz="8 to 11 hours behind the UAE", greeting="Hello", community="a community in the UAE",
   regions="Toronto, Vancouver and Calgary", occasions="Christmas"),
 dict(slug="australia", name="Australia", demonym="Australian", langs="English",
   tz="5 to 7 hours ahead of the UAE", greeting="G'day", community="a community in the UAE",
   regions="Sydney, Melbourne and Perth", occasions="Christmas"),
 dict(slug="iran", name="Iran", demonym="Iranian", langs="Persian (Farsi)",
   tz="about half an hour behind the UAE", greeting="Salam", community="a long-established community in the UAE",
   regions="Tehran, Isfahan and Shiraz", occasions="Nowruz"),
 dict(slug="turkey", name="Turkey", demonym="Turkish", langs="Turkish",
   tz="1 hour behind the UAE", greeting="Merhaba", community="a community in the UAE",
   regions="Istanbul, Ankara and Izmir", occasions="Eid (Bayram)"),
 dict(slug="saudi-arabia", name="Saudi Arabia", demonym="Saudi", langs="Arabic",
   tz="1 hour behind the UAE", greeting="As-salamu alaikum", community="close GCC neighbours and family",
   regions="Riyadh, Jeddah and Dammam", occasions="Eid"),
 dict(slug="qatar", name="Qatar", demonym="Qatari", langs="Arabic",
   tz="1 hour behind the UAE", greeting="As-salamu alaikum", community="close GCC neighbours and family",
   regions="Doha and Al Rayyan", occasions="Eid"),
 dict(slug="oman", name="Oman", demonym="Omani", langs="Arabic",
   tz="in the same time zone as the UAE", greeting="As-salamu alaikum", community="close GCC neighbours and family",
   regions="Muscat, Salalah and Sohar", occasions="Eid"),
 dict(slug="south-africa", name="South Africa", demonym="South African", langs="English and more",
   tz="2 hours behind the UAE", greeting="Howzit", community="a community in the UAE",
   regions="Johannesburg, Cape Town and Durban", occasions="Christmas"),
]

# Marquee city pages (kept, rewritten unique). city_line = genuinely distinct framing.
CITIES = [
 dict(slug="dubai-to-mumbai-calling-plan", city="Mumbai", ckey="india",
   city_line="Mumbai — Maharashtra's coastal capital — sends one of the biggest contingents to the UAE, from finance and shipping professionals to families with roots in the city's suburbs."),
 dict(slug="dubai-to-delhi-calling-plan", city="Delhi", ckey="india",
   city_line="Delhi and the wider NCR — Noida, Gurugram and Faridabad — are well represented in the UAE's professional and business circles, and a call to the capital is part of many weekly routines."),
 dict(slug="dubai-to-karnataka-calling-plan", city="Karnataka", ckey="india",
   city_line="Karnataka's community in the UAE spans Bengaluru's tech and business set and the coastal districts around Mangaluru and Udupi, many of whom call family across the state regularly."),
 dict(slug="dubai-to-kerala-calling-plan", city="Kerala", ckey="india",
   city_line="The Malayali community is among the most established in the UAE, with deep roots from Kochi, Thrissur, Kozhikode and the villages — for many, the daily call home to Kerala is a fixed part of the day."),
 dict(slug="dubai-to-manila-calling-plan", city="Manila", ckey="philippines",
   city_line="Manila and the surrounding Luzon provinces are home for a large share of the UAE's Kabayan community — and a call to family back home is never a luxury, it is family."),
 dict(slug="dubai-to-karachi-calling-plan", city="Karachi", ckey="pakistan",
   city_line="Karachi — Pakistan's largest city and commercial heart — has a strong presence in the UAE, and calls home to Sindh's capital are a weekly constant for many families."),
 dict(slug="dubai-to-lahore-calling-plan", city="Lahore", ckey="pakistan",
   city_line="Lahore and the wider Punjab send a large community to the UAE, and a call back to the city or to family in the surrounding districts is part of staying close."),
]


# ---- rotating template fragments (keyed by index so pages differ in wording) ----
def lead_v(c, i):
    n, g = c["name"], c["greeting"]
    opts = [
        f"A weekly “{g}” to family in {n} shouldn't mean watching a balance or buying another add-on pack. We set out the Etisalat (e&amp;) plans that give <strong>unlimited calls to {n}</strong> over the full network — flat-rate, bundled with data and a free VIP number, delivered the same day across the UAE.",
        f"For the {c['demonym']} community in the UAE, calling home to {n} is part of the rhythm of the week. Here's the Etisalat (e&amp;) plan that makes those calls <strong>unlimited and flat-rate</strong> — no per-minute charge, no add-on packs — with data and a free VIP number on top.",
        f"If you call {n} regularly, the answer isn't another top-up — it's a plan with <strong>unlimited calls to {n}</strong> built in. We compare the Etisalat (e&amp;) options below, all flat-rate over the full network, with same-day SIM delivery across the UAE.",
    ]
    return opts[i % 3]


def qa_v(c, i):
    n = c["name"]
    base = (f"the Etisalat <strong>Unlimited 1 Country plan at AED 325/month</strong> — unlimited calls to {n}, "
            f"plus 30GB data, 300 local minutes and a free Silver VIP number")
    opts = [
        f"The best Etisalat plan for calling {n} from the UAE is {base}. If you also make plenty of local UAE calls, the <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> gives unlimited flexi minutes that work both ways.",
        f"For calling {n}, pick {base}. Prefer one plan that also covers heavy local UAE calling? The <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> bundles 50GB and unlimited flexi minutes (local + international).",
    ]
    return opts[i % 2]


def community_para(c, i):
    n, d, comm, reg, occ, tz, langs = c["name"], c["demonym"], c["community"], c["regions"], c["occasions"], c["tz"], c["langs"]
    opts = [
        f"The {d} community is {comm}, with roots across {reg}. For most, staying close to home means a call several times a week — and a spike every {occ}. {n} is {tz}, so an evening call lands at a sensible hour, and a flat unlimited plan means you never cut it short to save credit.",
        f"With {comm}, {d} families across the UAE keep in touch with home in {reg} constantly — and calls peak around {occ}. Because {n} is {tz}, timing a call is easy; what you don't want is a per-minute meter or an add-on that runs out mid-conversation.",
        f"From {reg}, the {d} community is {comm}. People speak {langs} at home and call back regularly — especially around {occ}. {n} being {tz} makes evening calls convenient, and a fixed unlimited plan keeps every one of them clear and worry-free.",
    ]
    return opts[i % 3]


def plan_para(c, i):
    n = c["name"]
    opts = [
        (f"The honest answer for calling {n} is one plan: the <strong>Unlimited 1 Country plan at AED 325/month</strong>. "
         f"It gives <strong>unlimited calls to {n}</strong> — landlines and mobiles nationwide — over Etisalat's full network, so the line stays clear "
         f"even where Wi-Fi is weak, and you never buy another add-on. It also includes 30GB of data and 300 local minutes. "
         f"If you also make a lot of local UAE calls, the <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> fits better — its unlimited flexi minutes work both locally and internationally from one allowance."),
        (f"There's really one plan built for this: the <strong>Unlimited 1 Country plan (AED 325/month)</strong>, which makes calls to {n} "
         f"<strong>unlimited and flat-rate</strong> — any number, nationwide, on Etisalat's network rather than a patchy app connection — alongside 30GB of data and 300 local minutes. "
         f"For households that also burn through local UAE calls, the <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> rolls 50GB and unlimited flexi minutes (local + international) into one.")
    ]
    return opts[i % 2] + " Every plan here includes a free VIP number and same-day SIM delivery across the UAE."


FAQ_POOL = lambda c: [
 (f"What is the best Etisalat plan for calling {c['name']}?",
  f"The Unlimited 1 Country plan at AED 325/month — unlimited calls to {c['name']} (landlines and mobiles nationwide), 30GB data and 300 local minutes. If you also make many local UAE calls, the Unlimited Calls 600 Flexi (AED 360/month) gives unlimited flexi minutes that work both ways."),
 (f"Does the Unlimited 1 Country plan cover all of {c['name']}?",
  f"Yes — you choose {c['name']} as your country, and all your calls there become unlimited for a flat monthly price, covering numbers nationwide across {c['regions']} and beyond."),
 (f"Is an Etisalat plan cheaper than calling {c['name']} on WhatsApp or with add-on packs?",
  f"For regular callers, usually yes. App calls drop on weak Wi-Fi and add-on packs run out; the Unlimited 1 Country plan is a flat AED 325/month with full network call quality and no per-minute charge."),
 (f"What time is it in {c['name']} compared to the UAE?",
  f"{c['name']} is {c['tz']}, so an evening call from the UAE generally reaches family at a comfortable hour."),
 (f"Can I get a free VIP number with my {c['name']} calling plan?",
  "Yes — eligible plans include a free VIP number (Silver, Gold or Platinum by tier). Browse the live inventory at postpaidplans.com/choose-number and we'll deliver the SIM the same day across the UAE."),
 (f"I make a lot of local UAE calls too — which plan?",
  f"Choose the Unlimited Calls 600 Flexi (AED 360/month): 50GB of data plus unlimited flexi minutes that cover both local UAE calls and international calls to {c['name']} from a single allowance."),
 (f"How do I get an Etisalat plan for calling {c['name']}?",
  "Message a live Etisalat specialist on WhatsApp +971 56 902 8087 with how you call home. We confirm the right plan, add a free VIP number and deliver the SIM the same day across the UAE — as an Authorized Etisalat Dealer."),
]


def pick_faqs(c, i):
    pool = FAQ_POOL(c)
    # always lead with the "best plan" Q; rotate a window of the rest so pages differ
    rest = pool[1:]
    start = i % len(rest)
    chosen = [pool[0]] + [rest[(start + k) % len(rest)] for k in range(3)]
    return chosen


def which_list(c):
    n = c["name"]
    return (f'''<li><strong>You mainly call {n}:</strong> Unlimited 1 Country 325 — unlimited calls to {n} plus 30GB data, AED 325/month.</li>
        <li><strong>You call {n} <em>and</em> make lots of UAE calls:</strong> Unlimited Calls 600 Flexi — 50GB and unlimited flexi minutes (local + international), AED 360/month.</li>
        <li><strong>You want everything unlimited:</strong> Gold Plan 500 — unlimited data and unlimited local + international calls with a free Gold number.</li>
        <li><strong>You're on a tight budget:</strong> start on the Freedom Plan 250 (AED 188) and add an international option when you need it.</li>''')


def make_country(c, i):
    n = c["name"]
    return dict(
        slug=f"best-etisalat-plan-calling-{c['slug']}", ctx=f" for calling {n}",
        title=f"Best Etisalat Plan for Calling {n} from the UAE 2026 | Unlimited",
        meta_desc=f"The best Etisalat (e&) plan for calling {n} from the UAE — unlimited calls to {n} for AED 325/month with 30GB data and a free VIP number. No add-on packs. Same-day SIM delivery.",
        keywords=f"best Etisalat plan calling {n}, unlimited calls {n} from UAE, cheap calls UAE to {n}, call {n} from Dubai, Etisalat {n} calling plan",
        breadcrumb=f"Etisalat Plan for Calling {n}",
        lb_name=f"Postpaid Plans UAE — Etisalat Plan for Calling {n}",
        lb_desc=f"Etisalat (e&) postpaid plans for calling {n} from the UAE — unlimited calls to {n} for AED 325/month with 30GB data and a free VIP number, delivered same day across the UAE.",
        itemlist_name=f"Best Etisalat Plans for Calling {n}",
        h1=f'Best Etisalat Plan for Calling <span class="hl">{n}</span> from the UAE',
        lead=lead_v(c, i),
        quick_answer=qa_v(c, i),
        prose=f'''<h2>The plan that beats app calling and add-on packs</h2>
      <p>{community_para(c, i)}</p>
      <p>{plan_para(c, i)}</p>''',
        table_heading=f"Etisalat plans for calling {n}, best first",
        which_heading=f"Which plan is right for calling {n}?",
        which_list=which_list(c),
        faq_heading=f"Calling {n} from the UAE — FAQ",
        faqs=pick_faqs(c, i),
        cta_h2=f'Get unlimited calls to <span class="gold-text">{n}</span>',
        cta_p=f"Tell us how you call {n} and we'll set up the right Etisalat plan with unlimited calls and a free VIP number — same-day delivery across the UAE.",
        cta_ctx=f"Hi, I want an Etisalat plan with unlimited calls to {n}.",
        order=CALL_ORDER,
    )


def make_city(cdef, i):
    c = next(x for x in COUNTRIES if x["slug"] == cdef["ckey"])
    n = c["name"]; city = cdef["city"]
    return dict(
        slug=cdef["slug"], ctx=f" for calling {city}",
        title=f"Dubai to {city} Calls — Best Etisalat Plan 2026 | Unlimited to {n}",
        meta_desc=f"Calling {city} from Dubai or the UAE? The Etisalat (e&) Unlimited 1 Country plan gives unlimited calls to {n} — including {city} — for AED 325/month with data and a free VIP number.",
        keywords=f"Dubai to {city} calls, cheap calls Dubai to {city}, call {city} from UAE, best Etisalat plan calling {city}, unlimited calls {n} from Dubai",
        breadcrumb=f"Dubai to {city} Calling Plan",
        lb_name=f"Postpaid Plans UAE — Dubai to {city} Calling Plan",
        lb_desc=f"Etisalat (e&) plans for calling {city} ({n}) from Dubai and the UAE — unlimited calls to {n} for AED 325/month with 30GB data and a free VIP number, same-day delivery.",
        itemlist_name=f"Best Etisalat Plans for Calling {city}",
        h1=f'Dubai to <span class="hl">{city}</span> — Best Etisalat Calling Plan',
        lead=f"If you call {city} from Dubai or anywhere in the UAE, the smart move isn't another add-on pack — it's a plan with <strong>unlimited calls to {n}</strong>, {city} included. {cdef['city_line']}",
        quick_answer=f"For Dubai-to-{city} calls, the best plan is the Etisalat <strong>Unlimited 1 Country plan at AED 325/month</strong> — unlimited calls to {n} (which includes {city}), plus 30GB data, 300 local minutes and a free Silver VIP number. Also make heavy local UAE calls? The <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> covers both from one flexi allowance.",
        prose=f'''<h2>One plan covers {city} — and all of {n}</h2>
      <p>{cdef['city_line']} {community_para(c, i)}</p>
      <p>{plan_para(c, i)} Because the plan covers {n} nationwide, calls to {city} are included automatically — there's nothing city-specific to add.</p>''',
        table_heading=f"Best Etisalat plans for Dubai-to-{city} calls",
        which_heading=f"Which plan is right for calling {city}?",
        which_list=which_list(c),
        faq_heading=f"Dubai to {city} calls — FAQ",
        faqs=[(f"What is the best Etisalat plan for calling {city} from the UAE?",
               f"The Unlimited 1 Country plan at AED 325/month — unlimited calls to {n} (which includes {city}), 30GB data and 300 local minutes. For heavy local UAE calling too, the Unlimited Calls 600 Flexi (AED 360/month) gives unlimited flexi minutes both ways.")] + pick_faqs(c, i + 2)[1:],
        cta_h2=f'Unlimited calls from Dubai to <span class="gold-text">{city}</span>',
        cta_p=f"Tell us how often you call {city} and we'll set up the right Etisalat plan with unlimited calls to {n} and a free VIP number — same-day delivery across the UAE.",
        cta_ctx=f"Hi, I want an Etisalat plan for calling {city} ({n}) from the UAE.",
        order=CALL_ORDER,
    )


def build_hub():
    """A directory hub linking every calling destination — strong internal linking."""
    groups = [
        ("South Asia", ["india", "pakistan", "bangladesh", "sri-lanka", "nepal"]),
        ("Southeast Asia & beyond", ["philippines", "indonesia"]),
        ("Arab world", ["egypt", "jordan", "syria", "lebanon", "sudan", "yemen", "morocco"]),
        ("Africa", ["nigeria", "kenya", "ethiopia", "ghana", "uganda", "south-africa"]),
        ("West & others", ["uk", "usa", "canada", "australia", "iran", "turkey"]),
        ("GCC neighbours", ["saudi-arabia", "qatar", "oman"]),
    ]
    bymap = {c["slug"]: c for c in COUNTRIES}
    chips = ""
    for title, slugs in groups:
        links = "".join(f'<a href="/best-etisalat-plan-calling-{s}/">{bymap[s]["name"]}</a>' for s in slugs if s in bymap)
        chips += f'<h3>{title}</h3><div class="link-chips">{links}</div>'
    return dict(
        slug="international-calling-plans", ctx="",
        title="International Calling Plans from the UAE 2026 | Etisalat Unlimited",
        meta_desc="Etisalat (e&) international calling plans from the UAE — unlimited calls to one country for AED 325/month with data and a free VIP number. Find your country: India, Philippines, Pakistan, Bangladesh and more.",
        keywords="international calling plans UAE, Etisalat international calling, unlimited international calls UAE, call home from Dubai, Etisalat Unlimited 1 Country plan",
        breadcrumb="International Calling Plans",
        lb_name="Postpaid Plans UAE — International Calling Plans",
        lb_desc="Etisalat (e&) international calling plans from the UAE — unlimited calls to one country of your choice for AED 325/month with 30GB data and a free VIP number, delivered same day.",
        itemlist_name="Etisalat International Calling Plans",
        h1='Etisalat <span class="hl">International Calling</span> Plans from the UAE',
        lead="Calling home from the UAE shouldn't mean another add-on pack. The Etisalat (e&amp;) Unlimited 1 Country plan gives <strong>unlimited calls to one country of your choice</strong> for a flat AED 325/month, with data and a free VIP number. Pick your country below.",
        quick_answer="The Etisalat <strong>Unlimited 1 Country plan (AED 325/month)</strong> gives unlimited calls to one country you choose — India, the Philippines, Pakistan, Bangladesh, Egypt or any of the destinations below — plus 30GB data and a free Silver VIP number. Calling several countries? The <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> has unlimited flexi minutes that work internationally.",
        prose=f'''<h2>Choose your country</h2>
      <p>One Etisalat plan, unlimited calls to the country you call most. Find your destination below — each guide covers the right plan, the timing, and how to order with same-day delivery across the UAE.</p>
      {chips}
      <h2>How the Unlimited 1 Country plan works</h2>
      <p>You pick one country when you activate, and every call to that country — landlines and mobiles, nationwide — becomes unlimited for a flat AED 325/month, over Etisalat's full network rather than a patchy app connection. It also includes 30GB of data, 300 local minutes and a free Silver VIP number. If you call several countries, the Unlimited Calls 600 Flexi (AED 360/month) bundles 50GB with unlimited flexi minutes that work both locally and internationally.</p>''',
        table_heading="Etisalat plans for international calling, best first",
        which_heading="Which international calling plan is right for you?",
        which_list='''<li><strong>You call one country most:</strong> Unlimited 1 Country 325 — unlimited to that country plus 30GB data, AED 325/month.</li>
        <li><strong>You call several countries:</strong> Unlimited Calls 600 Flexi — 50GB and unlimited flexi minutes (local + international), AED 360/month.</li>
        <li><strong>You want everything unlimited:</strong> Gold Plan 500 — unlimited data and unlimited local + international calls with a free Gold number.</li>''',
        faq_heading="International calling from the UAE — FAQ",
        faqs=[
            ("Which Etisalat plan is best for international calling from the UAE?",
             "The Unlimited 1 Country plan (AED 325/month) for one country, or the Unlimited Calls 600 Flexi (AED 360/month) if you call several countries — its flexi minutes work both locally and internationally. Both include data and a free VIP number."),
            ("Can I choose any country for the Unlimited 1 Country plan?",
             "Yes — you select one country when you activate (India, the Philippines, Pakistan, Bangladesh, Egypt and many more), and all your calls to that country become unlimited for a flat monthly price."),
            ("Is an unlimited calling plan cheaper than add-on packs?",
             "For regular callers, usually yes. Add-on packs give a fixed bundle that runs out; the Unlimited 1 Country plan is a flat AED 325/month with no per-minute charge and full network call quality."),
            ("How do I order an international calling plan?",
             "Message a live Etisalat specialist on WhatsApp +971 56 902 8087 with the country you call most. We confirm the right plan, add a free VIP number and deliver the SIM the same day across the UAE."),
        ],
        cta_h2='Call home, <span class="gold-text">unlimited</span>',
        cta_p="Tell us the country you call most and we'll set up the right Etisalat plan with unlimited calls and a free VIP number — same-day delivery across the UAE.",
        cta_ctx="Hi, I want an Etisalat international calling plan — I mostly call ",
        order=CALL_ORDER,
    )


def main():
    pages = [build_hub()]
    for i, c in enumerate(COUNTRIES):
        pages.append(make_country(c, i))
    for i, cd in enumerate(CITIES):
        pages.append(make_city(cd, i))
    for page in pages:
        d = os.path.join(ROOT, page["slug"])
        os.makedirs(d, exist_ok=True)
        html = build(page)
        if "@@" in html:
            import re
            print("WARNING unreplaced tokens in", page["slug"], set(re.findall(r"@@[A-Z_]+@@", html)))
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
    print("done:", len(pages), "calling pages (1 hub +", len(COUNTRIES), "countries +", len(CITIES), "cities)")


if __name__ == "__main__":
    main()
