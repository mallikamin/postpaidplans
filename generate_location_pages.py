# -*- coding: utf-8 -*-
"""
generate_location_pages.py — localized Etisalat postpaid-plan landing pages per
UAE emirate. Reuses the proven template + helpers from generate_plan_pages.py so
schema, GA4, Meta Pixel, the WhatsApp Lead event and the "Talk to a LIVE Etisalat
Specialist" CTAs are identical site-wide. Only per-emirate copy is authored here.

Dubai already exists as a hand-built page (/etisalat-postpaid-plans-dubai/); this
script builds the remaining emirates.

Run:  python generate_location_pages.py
"""
import os
from generate_plan_pages import build, DEFAULT_ORDER, ROOT

# Per-emirate data — each page gets genuinely distinct copy (areas, communities, coverage angle).
LOCATIONS = [
    dict(
        name="Abu Dhabi", slug="etisalat-postpaid-plans-abu-dhabi",
        hl="Abu Dhabi",
        areas="Khalifa City, Al Reem Island, the Corniche, Mussafah, Al Bateen, Yas Island and Mohammed Bin Zayed City",
        intro="Abu Dhabi runs on reliable connectivity — government and corporate offices, long Corniche commutes, and a large professional community that lives across Khalifa City, Reem Island and MBZ. As the capital and Etisalat's home ground, the network here is among the strongest in the country, which is why most residents pair a solid data plan with a memorable VIP number.",
        coverage="Etisalat's coverage across Abu Dhabi island, the mainland suburbs and the islands is excellent, so even the unlimited high-speed plans deliver consistent speeds for hotspotting and video calls.",
        ctx=" in Abu Dhabi",
        q_cheapest="The cheapest Etisalat postpaid plan in Abu Dhabi is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, delivered the same day across Abu Dhabi, Khalifa City, Reem Island and Mussafah.",
    ),
    dict(
        name="Sharjah", slug="etisalat-postpaid-plans-sharjah",
        hl="Sharjah",
        areas="Al Nahda, Al Majaz, Al Khan, Muweilah, Al Taawun, University City and Al Qasimia",
        intro="Sharjah is a city of families and commuters — many residents work in Dubai but live in Al Nahda, Al Majaz or Muweilah for value. That mix means two needs dominate: enough data for the daily commute and unlimited or international minutes to stay in touch with family at home and abroad.",
        coverage="Etisalat gives Sharjah strong coverage across the Dubai–Sharjah corridor and the residential districts, so your data holds up on the daily commute through Al Ittihad Road and Maliha Road.",
        ctx=" in Sharjah",
        q_cheapest="The cheapest Etisalat postpaid plan in Sharjah is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, with same-day delivery across Al Nahda, Al Majaz, Muweilah and Al Taawun.",
    ),
    dict(
        name="Ajman", slug="etisalat-postpaid-plans-ajman",
        hl="Ajman",
        areas="Al Nuaimiya, Al Rashidiya, Ajman Corniche, Al Jurf and Mushairef",
        intro="Ajman is the value emirate — a tight-knit community where many residents commute to Sharjah and Dubai and keep a close eye on the monthly bill. That makes the budget Freedom plans especially popular here, paired with international options for staying in touch with family overseas.",
        coverage="Etisalat covers Ajman's residential districts and the Corniche well, and its wider footprint helps on the inter-emirate commute when you cross into Sharjah and Dubai.",
        ctx=" in Ajman",
        q_cheapest="The cheapest Etisalat postpaid plan in Ajman is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, delivered the same day across Al Nuaimiya, Al Rashidiya and the Ajman Corniche.",
    ),
    dict(
        name="Al Ain", slug="etisalat-postpaid-plans-al-ain",
        hl="Al Ain",
        areas="Al Jimi, Al Mutawaa, Al Towayya, Al Muwaiji, Hili and the Town Centre",
        intro="Al Ain — the Garden City — is quieter and more spread out than the coastal cities, with established Emirati and expat communities across Al Jimi, Al Muwaiji and Hili. Coverage that reaches the outer districts and the desert roads matters more here than in the dense cities, which plays to Etisalat's strengths.",
        coverage="Etisalat's wider network reaches Al Ain's spread-out neighbourhoods and the routes out toward the Oman border and Jebel Hafeet more consistently than the alternatives — useful if you drive beyond the town centre.",
        ctx=" in Al Ain",
        q_cheapest="The cheapest Etisalat postpaid plan in Al Ain is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, with same-day delivery across Al Jimi, Al Muwaiji, Hili and the Town Centre.",
    ),
    dict(
        name="Ras Al Khaimah", slug="etisalat-postpaid-plans-ras-al-khaimah",
        hl="Ras Al Khaimah",
        areas="Al Nakheel, Al Hamra, Mina Al Arab, Al Dhait and Khuzam",
        intro="Ras Al Khaimah stretches from the coast at Al Hamra and Mina Al Arab up into the Hajar mountains — exactly the kind of varied terrain where network footprint decides everything. Residents here weigh coverage heavily, and Etisalat's reach into the northern emirates and mountain roads is its clearest advantage.",
        coverage="This is where Etisalat's wider coverage pays off most — strong signal across RAK's coastal developments and noticeably better reach on the mountain and highway routes toward Jebel Jais and the northern villages.",
        ctx=" in Ras Al Khaimah",
        q_cheapest="The cheapest Etisalat postpaid plan in Ras Al Khaimah is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, delivered same day across Al Nakheel, Al Hamra and Mina Al Arab.",
    ),
    dict(
        name="Fujairah", slug="etisalat-postpaid-plans-fujairah",
        hl="Fujairah",
        areas="Fujairah City, Dibba, Al Faseel, Sakamkam and Mirbah",
        intro="On the east coast, Fujairah sits between the Hajar mountains and the Gulf of Oman, with communities strung along the coast from Dibba down to Kalba. The mountains and the long coastal highway make coverage the single biggest practical concern — and the area where Etisalat is hardest to beat.",
        coverage="Etisalat's network handles Fujairah's coastal towns and the winding mountain roads between Fujairah and Dibba far more reliably than patchier alternatives, so you stay connected on the east-coast drive.",
        ctx=" in Fujairah",
        q_cheapest="The cheapest Etisalat postpaid plan in Fujairah is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, with same-day delivery across Fujairah City, Dibba and Al Faseel.",
    ),
    dict(
        name="Umm Al Quwain", slug="etisalat-postpaid-plans-umm-al-quwain",
        hl="Umm Al Quwain",
        areas="Al Salama, Al Raas, Al Ramlah, King Faisal Road and the Old Town",
        intro="Umm Al Quwain is the quietest of the seven emirates — a small, close community along the lagoon and the King Faisal Road corridor. With fewer dense urban cells around, the breadth of the network matters, and residents tend to want a dependable plan plus international minutes to stay close to family abroad.",
        coverage="Etisalat's broad footprint keeps Umm Al Quwain's lagoon-side neighbourhoods and the inter-emirate road toward Ras Al Khaimah and Ajman well covered.",
        ctx=" in Umm Al Quwain",
        q_cheapest="The cheapest Etisalat postpaid plan in Umm Al Quwain is the Freedom Plan 250 at AED 188/month — non-stop data, 1,000 local minutes and a free Silver VIP number, delivered same day across Al Salama, Al Raas and Al Ramlah.",
    ),
]


def make_page(d):
    name = d["name"]
    return dict(
        slug=d["slug"], ctx=d["ctx"],
        title=f"Etisalat Postpaid Plans {name} 2026 | e& Plans From AED 188",
        meta_desc=f"Compare Etisalat (e&) postpaid plans in {name} — unlimited data from AED 188/mo with a free VIP number. Official e& partner, same-day SIM delivery across {name}.",
        keywords=f"Etisalat postpaid plans {name}, e& plans {name}, Etisalat plans {name}, best postpaid plan {name}, Etisalat unlimited data {name}, Etisalat SIM {name}",
        breadcrumb=f"Etisalat Postpaid Plans {name}",
        lb_name=f"Postpaid Plans UAE — Etisalat Postpaid Plans {name}",
        lb_desc=f"Compare and order Etisalat (e&) postpaid plans in {name} — from AED 188/month with non-stop or unlimited data, local and international minutes, roaming and a free VIP number on select plans. Same-day SIM delivery across {name}.",
        itemlist_name=f"Etisalat Postpaid Plans in {name}",
        h1=f'Etisalat Postpaid Plans <span class="hl">{d["hl"]}</span> — from AED 188',
        lead=f"Compare every Etisalat (e&amp;) postpaid plan available in {name} in one place — non-stop and unlimited data, local and international minutes, roaming, and a free VIP number on select plans. Confirm on WhatsApp and get your SIM the same day across {name}.",
        quick_answer=f"The best Etisalat postpaid plan in {name} depends on your usage. For value, the <strong>Freedom Plan 250 (AED 188/mo)</strong> is the cheapest; for heavy data, the <strong>Freedom Unlimited Data 500 (AED 300/mo)</strong>; for local and international calling, the <strong>Unlimited Calls 600 Flexi (AED 360/mo)</strong>. Every plan includes a free VIP number and same-day delivery across {name}.",
        prose=f'''<h2>Choosing an Etisalat plan in {name}</h2>
      <p>{d["intro"]}</p>
      <p>{d["coverage"]} Every plan below is the genuine Etisalat (e&amp;) product at the price Etisalat sets — as an authorized dealer we add no mark-up, we just make picking and ordering simple and deliver the SIM the same day to your address in {d["areas"]}. Most plans also include a free VIP number, so you can lock a memorable line at the same time. Not sure which fits? Run the free <a href="/#finder">Plan Finder</a>.</p>''',
        table_heading=f"Compare Etisalat postpaid plans in {name}",
        which_heading=f"Which Etisalat plan suits which {name} resident?",
        which_list=f'''<li><strong>Budget &amp; light use:</strong> Freedom Plan 250 — AED 188 with non-stop data and a free Silver number.</li>
        <li><strong>Heavy data &amp; hotspot:</strong> Freedom Unlimited Data 500 — unlimited high-speed at AED 300.</li>
        <li><strong>International callers:</strong> Unlimited 1 Country 325 for one country, or Unlimited Calls 600 Flexi for several.</li>
        <li><strong>Everything unlimited:</strong> Gold Plan 500 — unlimited data and calls with a free Gold number.</li>
        <li><strong>UAE nationals:</strong> Emirati Freedom — unlimited data and local calls at AED 250 with a valid Emirati ID.</li>''',
        faq_heading=f"Etisalat Postpaid Plans {name} — FAQ",
        faqs=[
            (f"What is the cheapest Etisalat postpaid plan in {name}?", d["q_cheapest"]),
            (f"Do you deliver Etisalat SIMs the same day in {name}?",
             f"Yes. As an Official e&amp; Partner and Authorized Etisalat Dealer we deliver across {name} — {d['areas']}. Pick your plan and a free VIP number, confirm on WhatsApp +971 56 902 8087 before the afternoon cut-off, and the SIM arrives the same day."),
            (f"Which Etisalat plan in {name} has unlimited data?",
             "The Freedom Unlimited Data 500 (AED 300/month, down from AED 600) gives unlimited high-speed data plus 1,000 flexi minutes and a free Silver number. The Gold Plan 500 and the Platinum Plan also include unlimited data with unlimited local and international calls."),
            (f"Can I get a free VIP number with an Etisalat plan in {name}?",
             "Yes — most plans include a free VIP number: Silver on standard plans, Gold on the Gold Plan, Platinum on the top tier. Browse the live inventory at postpaidplans.com/choose-number and lock a memorable line before you order."),
        ],
        cta_h2=f'Get your <span class="gold-text">Etisalat plan in {name}</span> today',
        cta_p=f"Tell us how you use your phone and we'll recommend the right Etisalat plan — then deliver the SIM with a free VIP number the same day across {name}.",
        cta_ctx=f"Hi, I'm in {name} and want help choosing an Etisalat postpaid plan.",
        order=DEFAULT_ORDER,
    )


def main():
    for d in LOCATIONS:
        page = make_page(d)
        out_dir = os.path.join(ROOT, page["slug"])
        os.makedirs(out_dir, exist_ok=True)
        html = build(page)
        if "@@" in html:
            import re
            print("WARNING unreplaced tokens in", page["slug"], set(re.findall(r"@@[A-Z_]+@@", html)))
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("wrote", page["slug"])
    print("done:", len(LOCATIONS), "location pages")


if __name__ == "__main__":
    main()
