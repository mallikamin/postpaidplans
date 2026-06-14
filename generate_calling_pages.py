# -*- coding: utf-8 -*-
"""
generate_calling_pages.py — international-calling intent pages targeting the UAE's
expat communities (Indian, Filipino, Pakistani). Anchored on the genuine Etisalat
"Unlimited 1 Country" plan (unlimited calls to one whole country) + "Unlimited Calls
600 Flexi" — NO invented per-minute rates. Reuses the template from generate_plan_pages.

Country hubs: /best-etisalat-plan-calling-<country>/
City pages:   /dubai-to-<city>-calling-plan/   (intent: "Dubai to Mumbai", etc.)

Run:  python generate_calling_pages.py
"""
import os
from generate_plan_pages import build, ROOT

# Calling plans lead the table; the rest follow.
CALL_ORDER = ["unl1country", "unlcalls600", "gold500", "platinum", "unldata500",
              "unllocal325", "freedom250", "newfreedom260", "freedom325", "local1200", "emirati"]


def calling_prose(country, scope_line, community_para):
    return f'''<h2>The plan that actually beats app calling and add-on packs</h2>
      <p>{community_para}</p>
      <p>The honest answer for calling {country} is one plan: the <strong>Unlimited 1 Country plan at AED 325/month</strong>. It gives <strong>unlimited calls to one country of your choice — {scope_line}</strong> — over Etisalat's full network, so the line stays clear even where Wi-Fi is weak and you never watch a balance or buy another add-on. It also includes 30GB of data and 300 local minutes. If you also make a lot of local UAE calls, the <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> is the better fit — its unlimited flexi minutes work both locally and internationally from one allowance. Every plan here includes a free VIP number and same-day SIM delivery across the UAE.</p>'''


def calling_which(country):
    return f'''<li><strong>You mainly call {country}:</strong> Unlimited 1 Country 325 — unlimited calls to {country}, plus 30GB data, for AED 325/month.</li>
        <li><strong>You call {country} <em>and</em> make lots of UAE calls:</strong> Unlimited Calls 600 Flexi — 50GB and unlimited flexi minutes (local + international) at AED 360/month.</li>
        <li><strong>You want everything unlimited:</strong> Gold Plan 500 — unlimited data and unlimited local + international calls with a free Gold number.</li>
        <li><strong>You're on a tight budget:</strong> start with the Freedom Plan 250 (AED 188) and add an international option when you need it.</li>'''


def calling_faqs(country, place, scope_line):
    return [
        (f"What is the best Etisalat plan for calling {place} from the UAE?",
         f"The Unlimited 1 Country plan at AED 325/month is the best pick — unlimited calls to {country} ({scope_line}), plus 30GB of data and 300 local minutes, over Etisalat's full network. If you also make many local UAE calls, the Unlimited Calls 600 Flexi (AED 360/month) gives unlimited flexi minutes that work both ways."),
        (f"Does the Etisalat Unlimited 1 Country plan cover all of {country}?",
         f"Yes — it gives unlimited calls to one country you choose, covering {scope_line}. You select {country} when you activate, and all your calls to {country} are then unlimited for the flat monthly price."),
        (f"Is an Etisalat plan cheaper than calling {place} on WhatsApp or with add-on packs?",
         f"For regular callers, usually yes. App calls depend on a good data connection at both ends and drop on weak Wi-Fi, while add-on packs give you a fixed bundle of minutes that runs out. The Unlimited 1 Country plan is a flat AED 325/month with no per-minute charge and full network call quality — simpler and often cheaper than topping up packs every month."),
        (f"Can I get a free VIP number with my {place} calling plan?",
         "Yes — eligible plans include a free VIP number (Silver, Gold or Platinum depending on tier). Browse the live inventory at postpaidplans.com/choose-number and we'll deliver the SIM the same day across the UAE."),
    ]


def hub(slug, country, place, scope_line, community_para, keywords_extra=""):
    return dict(
        slug=slug, ctx=f" for calling {country}",
        title=f"Best Etisalat Plan for Calling {country} from the UAE 2026 | Unlimited",
        meta_desc=f"The best Etisalat (e&) plan for calling {country} from the UAE — unlimited calls to {country} for AED 325/month with 30GB data and a free VIP number. No add-on packs. Same-day SIM delivery.",
        keywords=f"best Etisalat plan calling {country}, unlimited calls {country} from UAE, cheap calls UAE to {country}, Etisalat {country} calling plan, call {country} from Dubai{keywords_extra}",
        breadcrumb=f"Etisalat Plan for Calling {country}",
        lb_name=f"Postpaid Plans UAE — Etisalat Plan for Calling {country}",
        lb_desc=f"Etisalat (e&) postpaid plans for calling {country} from the UAE — unlimited calls to {country} for AED 325/month with 30GB data and a free VIP number, delivered same day across the UAE.",
        itemlist_name=f"Best Etisalat Plans for Calling {country}",
        h1=f'Best Etisalat Plan for Calling <span class="hl">{country}</span> from the UAE',
        lead=f"Calling {country} every week shouldn't mean watching a balance or buying another add-on pack. We set out the Etisalat (e&amp;) plans that give <strong>unlimited calls to {country}</strong> over the full network — clear, flat-rate, and bundled with data and a free VIP number, delivered the same day across the UAE.",
        quick_answer=f"The best Etisalat plan for calling {country} from the UAE is the <strong>Unlimited 1 Country plan at AED 325/month</strong> — unlimited calls to {country} ({scope_line}), 30GB data, 300 local minutes and a free Silver VIP number. If you also make lots of local UAE calls, the <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> gives unlimited flexi minutes that work both locally and internationally.",
        prose=calling_prose(country, scope_line, community_para),
        table_heading=f"Etisalat plans for calling {country}, best first",
        which_heading=f"Which plan is right for calling {country}?",
        which_list=calling_which(country),
        faq_heading=f"Calling {country} from the UAE — FAQ",
        faqs=calling_faqs(country, place, scope_line),
        cta_h2=f'Get unlimited calls to <span class="gold-text">{country}</span>',
        cta_p=f"Tell us how you call {country} and we'll set up the right Etisalat plan with unlimited calls and a free VIP number — delivered the same day across the UAE.",
        cta_ctx=f"Hi, I want an Etisalat plan with unlimited calls to {country}.",
        order=CALL_ORDER,
    )


def city(slug, city_name, country, scope_line, community_para):
    return dict(
        slug=slug, ctx=f" for calling {city_name}",
        title=f"Dubai to {city_name} Calls — Best Etisalat Plan 2026 | Unlimited to {country}",
        meta_desc=f"Calling {city_name} from Dubai or the UAE? The Etisalat (e&) Unlimited 1 Country plan gives unlimited calls to {country} — including {city_name} — for AED 325/month with data and a free VIP number.",
        keywords=f"Dubai to {city_name} calls, cheap calls Dubai to {city_name}, call {city_name} from UAE, best Etisalat plan calling {city_name}, unlimited calls {country} from Dubai, UAE to {city_name}",
        breadcrumb=f"Dubai to {city_name} Calling Plan",
        lb_name=f"Postpaid Plans UAE — Dubai to {city_name} Calling Plan",
        lb_desc=f"Etisalat (e&) plans for calling {city_name} ({country}) from Dubai and the UAE — unlimited calls to {country} for AED 325/month with 30GB data and a free VIP number, same-day delivery.",
        itemlist_name=f"Best Etisalat Plans for Calling {city_name}",
        h1=f'Dubai to <span class="hl">{city_name}</span> — Best Etisalat Calling Plan',
        lead=f"If you call {city_name} from Dubai or anywhere in the UAE, the smart move isn't another add-on pack — it's a plan with <strong>unlimited calls to {country}</strong>, {city_name} included. Here's the Etisalat (e&amp;) plan that does it, flat-rate, with data and a free VIP number, delivered the same day.",
        quick_answer=f"For Dubai-to-{city_name} calls the best plan is the Etisalat <strong>Unlimited 1 Country plan at AED 325/month</strong> — it gives unlimited calls to {country} (which includes {city_name}), plus 30GB data, 300 local minutes and a free Silver VIP number. Prefer unlimited local UAE calls too? The <strong>Unlimited Calls 600 Flexi (AED 360/month)</strong> covers both from one flexi allowance.",
        prose=calling_prose(country, scope_line, community_para),
        table_heading=f"Best Etisalat plans for Dubai-to-{city_name} calls",
        which_heading=f"Which plan is right for calling {city_name}?",
        which_list=calling_which(country),
        faq_heading=f"Dubai to {city_name} calls — FAQ",
        faqs=calling_faqs(country, city_name, scope_line),
        cta_h2=f'Unlimited calls from Dubai to <span class="gold-text">{city_name}</span>',
        cta_p=f"Tell us how often you call {city_name} and we'll set up the right Etisalat plan with unlimited calls to {country} and a free VIP number — same-day delivery across the UAE.",
        cta_ctx=f"Hi, I want an Etisalat plan for calling {city_name} ({country}) from the UAE.",
        order=CALL_ORDER,
    )


IN_SCOPE = "landlines and mobiles across the country"
IN_COMMUNITY = "The Indian community is the largest in the UAE, and for most families staying in touch means a call home several times a week — to parents, to children, to a spouse. That regular calling is exactly where a fixed unlimited plan beats topping up packs or relying on a patchy app connection."
PH_COMMUNITY = "To the Kabayan community across the UAE — the OFWs who keep two homes connected — calling home isn't a luxury, it's family. A weekly catch-up with parents, a video to the kids, a quick call to a sibling: a flat unlimited plan means you never cut a call short to save credit."
PK_COMMUNITY = "Pakistanis make up one of the UAE's largest communities, and for most that means regular calls home — to family in the city and to relatives in the village. A flat unlimited plan keeps every one of those calls clear and worry-free, without watching a balance or buying another pack."

PAGES = [
    # India
    hub("best-etisalat-plan-calling-india", "India", "India", IN_SCOPE, IN_COMMUNITY,
        keywords_extra=", Etisalat India calling offer, unlimited India calls"),
    city("dubai-to-mumbai-calling-plan", "Mumbai", "India", IN_SCOPE, IN_COMMUNITY),
    city("dubai-to-delhi-calling-plan", "Delhi", "India", IN_SCOPE, IN_COMMUNITY),
    city("dubai-to-karnataka-calling-plan", "Karnataka", "India", IN_SCOPE,
         "Karnataka's community in the UAE — from Bengaluru to Mangalore and the coastal districts — stays close to home with regular calls. A flat unlimited plan means those calls to family across Karnataka are clear and uncapped, with no per-minute worry."),
    city("dubai-to-kerala-calling-plan", "Kerala", "India", IN_SCOPE,
         "The Malayali community is one of the most established in the UAE, and a call home to Kerala — to Kochi, Thrissur, Kozhikode or the village — is part of the weekly rhythm. A flat unlimited plan keeps every one of those calls clear and uncapped."),
    # Philippines
    hub("best-etisalat-plan-calling-philippines", "the Philippines", "the Philippines",
        "landlines and mobiles nationwide", PH_COMMUNITY,
        keywords_extra=", call Philippines from UAE, Kabayan calling plan, OFW calling plan"),
    city("dubai-to-manila-calling-plan", "Manila", "the Philippines", "landlines and mobiles nationwide", PH_COMMUNITY),
    # Pakistan
    hub("best-etisalat-plan-calling-pakistan", "Pakistan", "Pakistan",
        "landlines and mobiles across the country", PK_COMMUNITY,
        keywords_extra=", call Pakistan from UAE, unlimited Pakistan calls"),
    city("dubai-to-karachi-calling-plan", "Karachi", "Pakistan", "landlines and mobiles across the country", PK_COMMUNITY),
    city("dubai-to-lahore-calling-plan", "Lahore", "Pakistan", "landlines and mobiles across the country", PK_COMMUNITY),
]


def main():
    for page in PAGES:
        out_dir = os.path.join(ROOT, page["slug"])
        os.makedirs(out_dir, exist_ok=True)
        html = build(page)
        if "@@" in html:
            import re
            print("WARNING unreplaced tokens in", page["slug"], set(re.findall(r"@@[A-Z_]+@@", html)))
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        print("wrote", page["slug"])
    print("done:", len(PAGES), "calling pages")


if __name__ == "__main__":
    main()
