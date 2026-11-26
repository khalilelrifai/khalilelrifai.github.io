#!/usr/bin/env python3
"""Static site generator for abrprotowing.com.

Usage:  python3 _src/build.py
Reads _src/site.json and writes every .html page, sitemap.xml, robots.txt and llms.txt
into the repo root. No dependencies beyond the Python standard library.
GitHub Pages (Jekyll) ignores folders that start with "_", so _src/ is never published.
"""
import datetime
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.load(open(os.path.join(ROOT, "_src", "site.json"), encoding="utf-8"))
TODAY = S.get("content_updated", "2026-11-26")

NAME = S["name"]
DOMAIN = S["domain"].rstrip("/")
TEL = "tel:" + S["phone_e164"]
SMS = "sms:" + S["phone_e164"]
PHONE = S["phone_display"]
EMAIL = S["email"]
CITY = S["city"]
AREAS = S["service_areas"]
OTHER_AREAS = [a for a in AREAS if a != CITY]
WA = "https://wa.me/" + S["phone_e164"].lstrip("+")
GBP = S.get("gbp_url", "")
GBP_SHARE = S.get("gbp_owner_share_url", "")
GBP_REVIEW = S.get("gbp_review_url", "")
HAS_OG = False  # legacy preview retired
HAS_TOUCH = False  # legacy icon retired
LOGO_URL = DOMAIN + "/img/abr-pro-logo.webp"
OG_URL = DOMAIN + "/img/og-image.jpg"

e = html.escape


# ------------------------------------------------------------------ icons
def icon(name, cls="icon"):
    p = {
        "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
        "sms": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
        "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
        "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
        "truck": '<path d="M1 4h14v12H1z"/><path d="M15 8h4l3 3v5h-7z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>',
        "bolt": '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
        "crash": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
        "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
        "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
        "check": '<polyline points="20 6 9 17 4 12"/>',
        "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
        "arrow": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
        "menu": '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
        "dollar": '<line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
        "hand": '<path d="M20 12V8a2 2 0 0 0-4 0v3"/><path d="M16 11V5a2 2 0 0 0-4 0v6"/><path d="M12 10V4a2 2 0 0 0-4 0v9"/><path d="M8 13v-2a2 2 0 0 0-4 0v3a8 8 0 0 0 8 8h1a7 7 0 0 0 7-7v-3"/>',
        "key": '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>',
        "tire": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="8"/><line x1="12" y1="16" x2="12" y2="22"/><line x1="2" y1="12" x2="8" y2="12"/><line x1="16" y1="12" x2="22" y2="12"/>',
        "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
        "whatsapp": '<path d="M3 21l1.65-3.8A9 9 0 1 1 7.6 20z"/><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"/>',
        "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
        "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>',
        "tiktok": '<path d="M9 12a4 4 0 1 0 4 4V2a5 5 0 0 0 5 5"/>',
    }[name]
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{p}</svg>'


LOGO_SVG = '<img class="brand-logo" src="/img/abr-pro-logo.webp" width="56" height="56" alt="">'

GOOGLE_G = (
    '<svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/>'
    '<path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
    '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
    '<path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>'
)

HERO_ART = """<svg class="hero-art" viewBox="0 0 600 320" role="img" aria-label="Illustration of a flatbed tow truck carrying a car">
  <defs><linearGradient id="road" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#2a2e35"/><stop offset="1" stop-color="#15171a"/></linearGradient></defs>
  <rect x="0" y="262" width="600" height="58" fill="url(#road)"/>
  <g fill="#ffc21a" opacity=".9"><rect x="20" y="288" width="60" height="6" rx="3"/><rect x="140" y="288" width="60" height="6" rx="3"/><rect x="260" y="288" width="60" height="6" rx="3"/><rect x="380" y="288" width="60" height="6" rx="3"/><rect x="500" y="288" width="60" height="6" rx="3"/></g>
  <!-- chassis + deck -->
  <rect x="58" y="214" width="492" height="16" rx="3" fill="#30343a"/>
  <rect x="50" y="198" width="380" height="16" rx="3" fill="#ffc21a"/>
  <g fill="#15171a"><rect x="58" y="202" width="14" height="8"/><rect x="86" y="202" width="14" height="8"/><rect x="114" y="202" width="14" height="8"/></g>
  <!-- car on deck -->
  <path d="M86 197v-24c4-11 16-14 30-15l52-3 34-27c9-7 18-8 30-8h76c14 0 24 4 34 13l29 25 30 4c12 2 19 9 19 21v14z" fill="#eef1f5" stroke="#9aa3ad" stroke-width="3"/>
  <path d="M184 155l30-23c6-4 11-5 19-5h34v28zm93 0v-28h33c10 0 16 3 23 9l21 19z" fill="#5b6b80"/>
  <rect x="98" y="170" width="18" height="7" rx="3" fill="#ffc21a"/>
  <circle cx="148" cy="190" r="20" fill="#15171a"/><circle cx="148" cy="190" r="8" fill="#9aa3ad"/>
  <circle cx="356" cy="190" r="20" fill="#15171a"/><circle cx="356" cy="190" r="8" fill="#9aa3ad"/>
  <!-- cab -->
  <path d="M432 214V116c0-8 6-14 14-14h58c7 0 12 3 16 9l32 48c3 4 4 8 4 13v42z" fill="#ffc21a"/>
  <path d="M450 120h50c4 0 7 2 9 5l24 36h-83z" fill="#2a2e35"/>
  <rect x="438" y="92" width="62" height="12" rx="4" fill="#ff7a1a"/><rect x="446" y="94" width="14" height="8" rx="2" fill="#ffe08a"/><rect x="478" y="94" width="14" height="8" rx="2" fill="#ffe08a"/>
  <rect x="540" y="182" width="16" height="10" rx="2" fill="#fff4c2"/>
  <rect x="456" y="178" width="22" height="5" rx="2" fill="#15171a"/>
  <g fill="#15171a"><circle cx="112" cy="240" r="28"/><circle cx="180" cy="240" r="28"/><circle cx="500" cy="240" r="28"/></g>
  <g fill="#9aa3ad"><circle cx="112" cy="240" r="11"/><circle cx="180" cy="240" r="11"/><circle cx="500" cy="240" r="11"/></g>
  <g stroke="#ffc21a" stroke-width="4" stroke-linecap="round" opacity=".55"><line x1="0" y1="150" x2="30" y2="150"/><line x1="8" y1="176" x2="34" y2="176"/><line x1="0" y1="124" x2="20" y2="124"/></g>
</svg>"""


# ------------------------------------------------------------------ content data
SERVICES = [
    {
        "slug": "emergency-towing",
        "name": "24/7 Emergency Towing",
        "short": "Breakdowns, cars that won't start, local roadside stops — we tow you to your home, mechanic, dealer or body shop.",
        "icon": "truck",
        "bullets": ["Cars, SUVs, minivans and light trucks", "Local roadside, driveway and parking-lot pickups", "Delivered to the shop or address you choose"],
    },
    {
        "slug": "roadside-assistance",
        "name": "Roadside Assistance",
        "short": "Dead battery, flat tire or keys locked inside? Often we can fix it on the spot so you can drive away.",
        "icon": "bolt",
        "bullets": ["Battery boosts (jump starts)", "Flat tire changes with your spare", "Car lockout service"],
    },
    {
        "slug": "accident-recovery",
        "name": "Accident Recovery",
        "short": "After a collision we clear and secure your vehicle and tow it to a collision centre, body shop or storage you choose.",
        "icon": "crash",
        "bullets": ["Careful loading of damaged vehicles", "Tow to a Collision Reporting Centre or body shop", "Photos and paperwork for your insurance claim"],
    },
    {
        "slug": "vehicle-transport",
        "name": "Vehicle Transport & Long-Distance Towing",
        "short": "Moving a car across the GTA or across Ontario? We transport non-running and running vehicles safely.",
        "icon": "route",
        "bullets": ["Dealer, auction and private-sale pickups", "Non-running and project cars", "Local and long-distance trips"],
    },
]

MISSISSAUGA_HOODS = [
    "City Centre &amp; Square One", "Port Credit", "Streetsville", "Meadowvale", "Meadowvale Village", "Erin Mills",
    "Churchill Meadows", "Lisgar", "Malton", "Cooksville", "Clarkson", "Lorne Park", "Lakeview", "Mineola",
    "Applewood", "Rathwood", "Hurontario", "Mississauga Valleys", "Heartland", "East Credit", "Sheridan", "Fairview",
]
MISSISSAUGA_ROADS = [
    "Hurontario Street", "Dundas Street", "Eglinton Avenue", "Mavis Road", "Erin Mills Parkway",
    "Winston Churchill Boulevard", "Lakeshore Road", "Airport Road (Pearson area)",
]

AREA_BLURBS = {
    "Brampton": "Local breakdown assistance and vehicle transport in Brampton, including Bramalea and Mount Pleasant, subject to availability.",
    "Oakville": "Local service in Oakville, from Bronte to Glen Abbey, subject to availability.",
    "Etobicoke": "Local service in Etobicoke, including commercial areas and hotels, subject to availability.",
    "Milton": "Local service in Milton for breakdowns, dealer pickups and long-distance vehicle moves.",
    "Toronto": "We travel into Toronto for tows to and from Mississauga, dealer transfers and planned vehicle transport.",
}


# ------------------------------------------------------------------ fragments
def call_btn(cls="btn btn-call", label=None):
    label = label or f"Call {PHONE}"
    return f'<a class="{cls}" href="{TEL}">{icon("phone")}<span>{label}</span></a>'


def text_btn(cls="btn btn-ghost", label="Text us"):
    return f'<a class="{cls}" href="{SMS}">{icon("sms")}<span>{label}</span></a>'


def faq_block(faqs):
    items = "".join(
        f'<details><summary>{e(q)}</summary><div><p>{a}</p></div></details>' for q, a in faqs
    )
    return f'<div class="faq">{items}</div>'


def faq_schema(faqs):
    import re
    def strip(t):
        return html.unescape(re.sub(r"<[^>]+>", "", t))
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
            for q, a in faqs
        ],
    }


def cta_band(title="Need a tow right now?", sub=f"Open 24/7 across {CITY} and nearby cities. A real person answers."):
    return f"""
<section class="cta-band" aria-label="Call us">
  <div class="wrap">
    <div><h2>{title}</h2><p>{sub}</p></div>
    <div class="btn-row">{call_btn("btn btn-dark btn-lg")}<a class="btn btn-outline btn-lg" href="{SMS}">{icon("sms")}<span>Text us</span></a></div>
  </div>
</section>"""


def tow_form(heading="Request a tow", intro="For non-urgent bookings and quotes. <strong>If you're stranded, call — it's faster.</strong>"):
    opts = "".join(f"<option>{e(s['name'])}</option>" for s in SERVICES)
    return f"""
<div class="form-card" id="request">
  <h2 class="h3" style="font-size:1.5rem">{heading}</h2>
  <p class="muted">{intro}</p>
  <form class="tow-form" action="https://formsubmit.co/{EMAIL}" method="POST">
    <input type="hidden" name="_subject" value="New tow request — {e(NAME)} website">
    <input type="hidden" name="_next" value="{DOMAIN}/thank-you.html">
    <input type="hidden" name="_template" value="table">
    <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <div class="form-grid">
      <div><label for="f-name">Your name</label><input id="f-name" name="name" autocomplete="name" required></div>
      <div><label for="f-phone">Phone number</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>
      <div class="full"><label for="f-email">Email <span class="muted">(optional)</span></label><input id="f-email" name="email" type="email" autocomplete="email"></div>
      <div><label for="f-service">Service</label><select id="f-service" name="service">{opts}<option>Other / not sure</option></select></div>
      <div><label for="f-where">Pickup location</label><input id="f-where" name="pickup_location" placeholder="Local street address or intersection"></div>
      <div class="full"><label for="f-to">Drop-off (if towing)</label><input id="f-to" name="dropoff_location" placeholder="Home, mechanic, dealer, body shop…"></div>
      <div class="full"><label for="f-msg">Vehicle &amp; details</label><textarea id="f-msg" name="message" placeholder="Year, make, model — and what happened"></textarea></div>
      <div class="full"><button class="btn btn-call btn-lg" type="submit" style="width:100%">Send request</button>
      <p class="form-note">We reply by phone or text. See our <a href="/privacy.html">privacy note</a>.</p></div>
    </div>
  </form>
</div>"""


def contact_list(dark=False):
    hours = "Open 24 hours, 7 days a week"
    area = f"{CITY}, {S['region']} — mobile service area"
    return f"""
<ul class="contact-list">
  <li><span class="card-icon">{icon("phone")}</span><div><strong>Call 24/7</strong><a href="{TEL}">{PHONE}</a></div></li>
  <li><span class="card-icon">{icon("sms")}</span><div><strong>Text us</strong><a href="{SMS}">{PHONE}</a></div></li>
  <li><span class="card-icon">{icon("mail")}</span><div><strong>Email</strong><a href="mailto:{EMAIL}">{EMAIL}</a></div></li>
  <li><span class="card-icon">{icon("clock")}</span><div><strong>Hours</strong>{hours}</div></li>
  <li><span class="card-icon">{icon("pin")}</span><div><strong>Based in</strong>{area}</div></li>
</ul>"""


def stars(n):
    n = max(0, min(5, int(n)))
    return f'<span class="stars" aria-label="{n} out of 5 stars">{"★" * n}{"☆" * (5 - n)}</span>'


def fmt_date(d):
    try:
        if len(d) == 7:
            return datetime.datetime.strptime(d, "%Y-%m").strftime("%B %Y")
        return datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%B %-d, %Y")
    except Exception:
        return e(d)


def review_cards(limit=None, all_layout=False):
    return ""  # Do not store Google review content.


def google_buttons():
    out = []
    if GBP or GBP_SHARE:
        out.append(f'<a class="btn btn-outline" href="{e(GBP or GBP_SHARE)}" target="_blank" rel="noopener">View our Google profile</a>')
    if GBP_REVIEW:
        out.append(f'<a class="btn btn-dark" href="{e(GBP_REVIEW)}" target="_blank" rel="noopener">{icon("star")}<span>Leave us a review</span></a>')
    review = S.get("google_reviews", {})
    key, pid = review.get("browser_key", ""), review.get("place_id", "")
    panel = (f'<div class="live-reviews" data-key="{e(key)}" data-place="{e(pid)}"><button class="btn btn-outline" type="button">Load Google reviews</button><p role="status" aria-live="polite"></p><div class="google-results"></div></div>' if key and pid and review.get("enabled") else "")
    return panel + (f'<div class="btn-row" style="justify-content:center;margin-top:1.5rem">{"".join(out)}</div>' if out else "")


def reviews_section(soft=True):
    cards = review_cards(limit=9)
    if cards:
        body = cards + google_buttons()
    else:
        body = f"""<div class="review-cta card"><p class="g-badge" style="justify-content:center">{GOOGLE_G}Reviews on Google</p>
<p class="muted">Read what {CITY} drivers say about us on our Google Business Profile — and if we've helped you, a quick review helps other drivers find us.</p>{google_buttons()}</div>"""
    return f"""
<section class="section{' soft' if soft else ''}" id="reviews">
  <div class="wrap">
    <div class="section-head center"><span class="kicker">Google reviews</span><h2>What {CITY} drivers say</h2></div>
    {body}
  </div>
</section>"""


def gallery_section():
    g = S.get("gallery", [])
    if not g:
        return ""
    imgs = "".join(
        f'<img src="{e(i["src"])}" alt="{e(i["alt"])}" width="{i.get("w", 1200)}" height="{i.get("h", 900)}" loading="lazy" decoding="async">'
        for i in g
    )
    return f"""
<section class="section" id="photos">
  <div class="wrap">
    <div class="section-head center"><span class="kicker">On the job</span><h2>Our trucks &amp; recent tows</h2></div>
    <div class="gallery">{imgs}</div>
  </div>
</section>"""


def posts_section():
    posts = S.get("posts", [])
    if not posts:
        return ""
    cards = ""
    for p in posts[:3]:
        img = f'<img src="{e(p["image"])}" alt="{e(p["title"])}" loading="lazy" decoding="async" width="800" height="500">' if p.get("image") else ""
        cards += f'<article class="card post">{img}<time datetime="{e(p.get("date", ""))}">{fmt_date(p.get("date", ""))}</time><h3>{e(p["title"])}</h3><p>{e(p["text"])}</p></article>'
    return f"""
<section class="section soft" id="updates">
  <div class="wrap">
    <div class="section-head center"><span class="kicker">Latest updates</span><h2>News from ABR Pro Towing & Recovery</h2></div>
    <div class="grid grid-3">{cards}</div>
  </div>
</section>"""


def service_cards(exclude=None):
    out = ""
    for s in SERVICES:
        if s["slug"] == exclude:
            continue
        lis = "".join(f"<li>{b}</li>" for b in s["bullets"])
        out += f"""<a class="card" href="/services/{s['slug']}.html"><span class="card-icon">{icon(s['icon'])}</span>
<h3>{s['name']}</h3><p class="muted">{s['short']}</p><ul>{lis}</ul><span class="more">Learn more {icon('arrow')}</span></a>"""
    cols = "grid-4" if exclude is None else "grid-3"
    return f'<div class="grid {cols}">{out}</div>'


def area_chips(link=True):
    items = ""
    for a in AREAS:
        if link and a == CITY:
            items += f'<li><a href="/towing-mississauga.html">{e(a)}</a></li>'
        elif link:
            items += f'<li><a href="/service-areas.html#{a.lower()}">{e(a)}</a></li>'
        else:
            items += f"<li>{e(a)}</li>"
    return f'<ul class="chips">{items}</ul>'


def crumbs(trail):
    lis = ""
    for i, (label, href) in enumerate(trail):
        if i == len(trail) - 1:
            lis += f'<li aria-current="page">{label}</li>'
        else:
            lis += f'<li><a href="{href}">{label}</a></li>'
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}</ol></nav>'


def breadcrumb_schema(trail):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": html.unescape(label), "item": DOMAIN + href}
            for i, (label, href) in enumerate(trail)
        ],
    }


def page_hero(trail, h1, lead, buttons=True):
    btns = f'<div class="btn-row">{call_btn("btn btn-call btn-lg")}{text_btn()}</div>' if buttons else ""
    return f"""
<section class="page-hero">
  <div class="wrap">
    {crumbs(trail)}
    <h1>{h1}</h1>
    <p class="lead">{lead}</p>
    {btns}
  </div>
</section>"""


# ------------------------------------------------------------------ business schema
def business_entity():
    same = [u for u in [GBP] + list(S.get("social", {}).values()) if u]
    ent = {
        "@type": "AutomotiveBusiness",
        "@id": DOMAIN + "/#business",
        "name": NAME,
        "url": DOMAIN + "/",
        "telephone": S["phone_schema"],
        "email": EMAIL,
        "description": f"24/7 towing and roadside assistance in {CITY}, Ontario: emergency towing, battery boosts, lockouts, flat tires, accident recovery and vehicle transport.",
        "logo": LOGO_URL,
        "image": OG_URL if HAS_OG else LOGO_URL,
        "address": {"@type": "PostalAddress", "addressLocality": CITY, "addressRegion": S["region"], "addressCountry": S["country"]},
        "areaServed": [{"@type": "City", "name": f"{a}, {S['region']}"} for a in AREAS],
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        }],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Towing services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": f"{DOMAIN}/services/{s['slug']}.html"}}
                for s in SERVICES
            ],
        },
    }
    if GBP:
        ent["hasMap"] = GBP
    if same:
        ent["sameAs"] = same
    return ent


# ------------------------------------------------------------------ layout
NAV = [
    ("/services/", "Services"),
    ("/towing-mississauga.html", "Mississauga"),
    ("/service-areas.html", "Service Areas"),
    ("/reviews.html", "Reviews"),
    ("/about.html", "About"),
    ("/contact.html", "Contact"),
]


def layout(path, title, desc, body, schema=None, noindex=False, active=None):
    url = DOMAIN + path
    graph = [
        business_entity(),
        {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": NAME, "publisher": {"@id": DOMAIN + "/#business"}, "inLanguage": "en-CA"},
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "isPartOf": {"@id": DOMAIN + "/#website"}, "about": {"@id": DOMAIN + "/#business"}, "inLanguage": "en-CA"},
    ] + (schema or [])
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1).replace("</", "<\\/")

    nav = "".join(
        f'<a href="{h}"{" aria-current=\"page\"" if active == h else ""}>{l}</a>' for h, l in NAV
    )
    social_links = "".join(
        f'<a href="{e(u)}" target="_blank" rel="noopener" aria-label="{k.title()}">{icon(k)}</a>'
        for k, u in S.get("social", {}).items() if u
    )
    if GBP or GBP_SHARE:
        social_links += f'<a href="{e(GBP or GBP_SHARE)}" target="_blank" rel="noopener" aria-label="Google Business Profile">{GOOGLE_G}</a>'
    socials = f'<div class="socials">{social_links}</div>' if social_links else ""
    svc_links = "".join(f'<li><a href="/services/{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)
    area_links = "".join(
        f'<li><a href="{"/towing-mississauga.html" if a == CITY else "/service-areas.html#" + a.lower()}">Towing {e(a)}</a></li>'
        for a in AREAS
    )
    wa_bar = f'<a class="cb-text" href="{WA}">{icon("whatsapp")}WhatsApp</a>' if S.get("whatsapp") else ""
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large"
    og_img = f'<meta property="og:image" content="{OG_URL}">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n' if HAS_OG else ""
    touch = '<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">\n' if HAS_TOUCH else ""
    year = int(TODAY[:4])

    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#15171a">
<meta name="geo.region" content="CA-ON">
<meta name="geo.placename" content="{CITY}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(NAME)}">
<meta property="og:locale" content="en_CA">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{LOGO_URL}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="/img/abr-pro-logo.webp" type="image/webp">
{touch}<link rel="stylesheet" href="/css/site.css?v={TODAY.replace('-', '')}">
<script type="application/ld+json">
{ld}
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topline"><div class="wrap"><span>Open 24/7 · Towing<span class="hide-s"> &amp; roadside help</span> in {CITY}</span><a class="hide-s" href="{TEL}">Call {PHONE}</a></div></div>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="{e(NAME)} — home">{LOGO_SVG}<span>ABR <b>Pro Towing</b><small>&amp; Recovery</small></span></a>
    <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
    <a class="btn btn-call header-call" href="{TEL}">{icon("phone")}<span class="num">{PHONE}</span><span class="sr-only">Call us</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Open menu">{icon("menu")}</button>
  </div>
</header>
<main id="main">
{body}
<div class="wrap"><p class="coverage-notice">Services are available within our authorized operating areas. Restricted towing zones are excluded. <a href="https://www.ontario.ca/page/tow-zone-program">Ontario Tow Zone Program</a>.</p></div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="/">{LOGO_SVG}<span>ABR <b>Pro Towing</b><small>&amp; Recovery</small></span></a>
        <p style="margin-top:1rem">24/7 towing and roadside assistance based in {CITY}, {S['region_full']}, serving surrounding GTA communities.</p>
        <a class="footer-phone" href="{TEL}">{PHONE}</a>
        <ul>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li>Open 24 hours, 7 days a week</li>
          <li>{CITY}, {S['region']}, Canada</li>
        </ul>
        {socials}
      </div>
      <div><h2>Services</h2><ul>{svc_links}</ul></div>
      <div><h2>Service areas</h2><ul>{area_links}</ul></div>
      <div><h2>Company</h2><ul>
        <li><a href="/about.html">About us</a></li>
        <li><a href="/reviews.html">Reviews</a></li>
        <li><a href="/contact.html">Contact</a></li>
        <li><a href="/contact.html#request">Request a tow</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <span>&copy; {year} {e(NAME)}. All rights reserved.</span>
      <nav aria-label="Legal"><a href="/privacy.html">Privacy</a><a href="/sitemap.xml">Sitemap</a></nav>
    </div>
  </div>
</footer>
<div class="callbar{' has-wa' if wa_bar else ''}">
  <a class="cb-call" href="{TEL}">{icon("phone")}Call now</a>
  <a class="cb-text" href="{SMS}">{icon("sms")}Text</a>{wa_bar}
</div>
<script src="/js/site.js" defer></script>
<script src="/js/google-reviews.js" defer></script>
</body>
</html>
"""


# ------------------------------------------------------------------ pages
PAGES = []  # (path, file, html, include_in_sitemap, priority)


def add(path, filename, html_out, sitemap=True, priority="0.7"):
    PAGES.append((path, filename, html_out, sitemap, priority))


# ---------- Home
HOME_FAQ = [
    ("How fast can a tow truck get to me in Mississauga?",
     "We dispatch as soon as you call and give you an honest arrival time on the phone based on where you are, traffic and the time of day. Restricted towing zones are excluded. Call 911 if there is immediate danger."),
    ("How much does a tow cost in Mississauga?",
     "The price depends on the distance, your vehicle and the situation (for example a simple breakdown versus an accident or a car stuck in a ditch). Call or text us with your location and destination and we'll quote you <strong>before</strong> we send a truck — no surprises."),
    ("Are you really open 24 hours?",
     f"Yes. {NAME} answers calls 24 hours a day, 7 days a week, including nights, weekends and holidays."),
    ("Can you tow my car to my own mechanic or body shop?",
     "Yes. In Ontario you have the right to choose where your vehicle is towed (unless police direct otherwise). We'll take it to your home, your mechanic, your dealership or the body shop your insurer recommends."),
    ("Do you help if I just need a boost, a tire change or a lockout?",
     "Yes. Our <a href=\"/services/roadside-assistance.html\">roadside assistance</a> covers battery boosts, flat tire changes using your spare, and car lockouts — often no tow is needed."),
    ("Which areas do you cover?",
     f"We're based in {CITY} and cover Mississauga neighbourhoods plus {', '.join(OTHER_AREAS[:-1])} and {OTHER_AREAS[-1]}. See our <a href=\"/service-areas.html\">service areas</a>." if len(OTHER_AREAS) > 1 else f"We cover all of {CITY}."),
]

home_body = f"""
<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Open now · 24 hours, 7 days</p>
      <h1>24/7 Towing &amp; Roadside Assistance in <em>Mississauga</em></h1>
      <p class="lead">Need a tow on a local street or in a parking lot near Square One? {NAME} sends a tow truck to you — day or night. One call gets you a clear price and an honest arrival time.</p>
      <div class="btn-row">{call_btn("btn btn-call btn-lg")}{text_btn("btn btn-ghost btn-lg", "Text your location")}</div>
      <ul class="ticks">
        <li>{icon("clock")}Open 24/7, including holidays</li>
        <li>{icon("pin")}Local {CITY} towing company</li>
        <li>{icon("dollar")}Price quoted before we dispatch</li>
        <li>{icon("shield")}Your vehicle handled with care</li>
      </ul>
    </div>
    {HERO_ART}
  </div>
</section>

<section class="section" id="services">
  <div class="wrap">
    <div class="section-head"><span class="kicker">Our services</span><h2>Towing and roadside help for every situation</h2>
    <p class="muted">From a dead battery in your driveway to a breakdown on a local street — one number, any time.</p></div>
    {service_cards()}
  </div>
</section>

{reviews_section()}

<section class="section dark">
  <div class="wrap">
    <div class="section-head"><span class="kicker">How it works</span><h2>Help on the way in four steps</h2></div>
    <ol class="steps">
      <li><h3>Call or text</h3><p>Reach us 24/7 at <a href="{TEL}" style="color:#ffc21a">{PHONE}</a>.</p></li>
      <li><h3>Share your location</h3><p>Tell us where you are — or text a map pin — and where the car needs to go.</p></li>
      <li><h3>Get a price &amp; ETA</h3><p>We quote you up front and give you a realistic arrival time.</p></li>
      <li><h3>We tow or fix it</h3><p>We secure your vehicle and deliver it, or get you running on the spot.</p></li>
    </ol>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div>
      <span class="kicker">Why {CITY} drivers call us</span>
      <h2>A local tow company that picks up the phone</h2>
      <p>We're based in {CITY}, so we know the roads — Hurontario, Dundas, Eglinton and the busy plazas and condo garages around City Centre. Call to confirm access and availability.</p>
      <div class="grid grid-2" style="margin-top:1.5rem">
        <div class="feature"><span class="card-icon">{icon("clock")}</span><div><h3>Always open</h3><p class="muted">Nights, weekends, holidays and bad-weather days.</p></div></div>
        <div class="feature"><span class="card-icon">{icon("dollar")}</span><div><h3>Upfront pricing</h3><p class="muted">You know the price before we roll.</p></div></div>
        <div class="feature"><span class="card-icon">{icon("hand")}</span><div><h3>Careful handling</h3><p class="muted">Properly secured and delivered where you choose.</p></div></div>
        <div class="feature"><span class="card-icon">{icon("pin")}</span><div><h3>Truly local</h3><p class="muted">{CITY} and nearby communities including {", ".join(OTHER_AREAS[:3])} and more.</p></div></div>
      </div>
      <p style="margin-top:1.5rem"><a class="btn btn-outline" href="/towing-mississauga.html">Towing in {CITY} {icon("arrow")}</a></p>
    </div>
    <div class="card">
      <h3>Areas we serve</h3>
      <p class="muted">{CITY} neighbourhoods, including:</p>
      <ul class="chips" style="margin-bottom:1.2rem">{"".join(f"<li>{h}</li>" for h in MISSISSAUGA_HOODS[:12])}</ul>
      <p class="muted">And nearby cities:</p>
      {area_chips()}
    </div>
  </div>
</section>

{gallery_section()}
{posts_section()}

<section class="section soft" id="faq">
  <div class="wrap narrow">
    <div class="section-head center"><span class="kicker">FAQ</span><h2>Towing questions, answered</h2></div>
    {faq_block(HOME_FAQ)}
  </div>
</section>

<section class="section dark" id="contact">
  <div class="wrap split">
    <div>
      <span class="kicker">Contact</span>
      <h2>Stranded? Call now — we answer 24/7</h2>
      <p>The fastest way to get help is a phone call. For planned transports or quotes, send the form and we'll get back to you quickly.</p>
      <div class="btn-row" style="margin:1.25rem 0 2rem">{call_btn("btn btn-call btn-lg")}{text_btn("btn btn-ghost btn-lg")}</div>
      {contact_list(dark=True)}
    </div>
    {tow_form()}
  </div>
</section>
"""
add("/", "index.html", layout(
    "/", f"24/7 Towing Mississauga | {NAME} | {PHONE}",
    f"24/7 towing & roadside assistance in Mississauga, ON. Emergency towing, battery boosts, lockouts, flat tires, accident recovery & vehicle transport. Call {PHONE}.",
    home_body, schema=[faq_schema(HOME_FAQ)], active=None), priority="1.0")


# ---------- Mississauga page
MISS_FAQ = [
    ("Do you provide towing in restricted zones?",
     "No. Restricted towing zones are excluded. If you are safe and need assistance in a restricted zone, call Ontario 511 and select the Tow Zone Program. Call 911 in an emergency."),
    ("Can you get a car out of an underground condo or plaza garage?",
     "Often yes. Tell us the garage name or address and, if you know it, the clearance height. We'll tell you on the phone what equipment we'll bring."),
    ("Do you tow near Pearson Airport and Malton?",
     "Yes. Toronto Pearson is inside Mississauga, and we regularly work the Airport Road, Malton and Northeast industrial area."),
    ("Where can you take my vehicle?",
     "Anywhere you choose — your home, a mechanic, a dealership, a body shop, a scrapyard or a Collision Reporting Centre. In Ontario you have the right to choose where your vehicle is towed unless police direct otherwise."),
    ("How do I pay?",
     "Ask when you call and we'll confirm the payment options for your tow before we dispatch."),
]
hoods = "".join(f"<li>{h}</li>" for h in MISSISSAUGA_HOODS)
roads = "".join(f"<li>{r}</li>" for r in MISSISSAUGA_ROADS)
trail = [("Home", "/"), ("Towing Mississauga", "/towing-mississauga.html")]
miss_body = page_hero(
    trail, "Towing in Mississauga, ON — 24 Hours a Day",
    f"{NAME} is a local Mississauga towing company. We tow cars, SUVs, minivans and light trucks in authorized locations in the city — and help with boosts, lockouts and flat tires — any time, day or night."
) + f"""
<section class="section">
  <div class="wrap split">
    <div class="prose">
      <h2>Local towing across Mississauga</h2>
      <p>When your car won't start in a Square One parking lot, gets a flat on Mavis Road, or is involved in a fender-bender on Hurontario, you want a tow truck that's close by and a company that answers the phone. That's us. We're based right here in {CITY} and serve local neighbourhoods from Port Credit on the lake to Meadowvale and Malton in the north.</p>
      <p>Call <a href="{TEL}"><strong>{PHONE}</strong></a>, tell us where you are and where the vehicle needs to go, and we'll give you a price and an honest arrival time before we dispatch.</p>

      <h2>Towing services we provide in Mississauga</h2>
      <ul>
        <li><a href="/services/emergency-towing.html">24/7 emergency towing</a> — breakdowns, no-starts and stalled vehicles</li>
        <li><a href="/services/roadside-assistance.html">Roadside assistance</a> — battery boosts, flat tire changes and lockouts</li>
        <li><a href="/services/accident-recovery.html">Accident recovery</a> — towing after a collision, to a body shop or Collision Reporting Centre</li>
        <li><a href="/services/vehicle-transport.html">Vehicle transport</a> — dealer, auction and private-sale pickups, local and long-distance</li>
      </ul>

      <h2>Mississauga neighbourhoods we cover</h2>
      <ul class="chips">{hoods}</ul>

      <h2>Local streets and main roads</h2>
      <p>Examples of local roads we serve, subject to safe access and availability:</p>
      <ul class="chips">{roads}</ul>

      <h2>Stuck on the side of the road? Do this while you wait</h2>
      <ol>
        <li><strong>Get safe first.</strong> If possible, move to a safe location and turn on your hazard lights. Call 911 if there is immediate danger.</li>
        <li><strong>If anyone is hurt, call 911.</strong> Then call us.</li>
        <li><strong>Note your location.</strong> The nearest local intersection or a landmark helps — or text us a map pin from your phone.</li>
        <li><strong>Know your rights.</strong> In Ontario you choose where your vehicle goes. Always confirm the price before a tow, and ask for an itemized invoice.</li>
      </ol>
      <div class="callout"><p><strong>Minor collision, no injuries?</strong> Peel Regional Police may ask you to report it at a Collision Reporting Centre. We can tow your vehicle there, and then on to the body shop of your choice.</p></div>

      <h2>Frequently asked questions</h2>
      {faq_block(MISS_FAQ)}
    </div>
    <aside class="aside-stack">
      <div class="card"><h3>Need a tow in Mississauga?</h3><p class="muted">Open 24/7. Call or text to confirm availability.</p>
        <div class="btn-row">{call_btn("btn btn-call")}{text_btn("btn btn-outline", "Text us")}</div></div>
      <div class="card"><h3>Also serving</h3>{area_chips()}</div>
    </aside>
  </div>
</section>
{reviews_section()}
<section class="section">
  <div class="wrap">
    <div class="section-head"><h2>Mississauga service area</h2><p class="muted">We're a mobile, service-area business — we come to you within authorized areas in {CITY}.</p></div>
    <iframe class="map" title="General map of Mississauga, not a business address" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      src="https://maps.google.com/maps?q=Mississauga%2C%20ON%2C%20Canada&amp;z=11&amp;output=embed"></iframe>
  </div>
</section>
{cta_band(f"Broken down in {CITY}?")}
"""
add("/towing-mississauga.html", "towing-mississauga.html", layout(
    "/towing-mississauga.html", f"Towing Mississauga 24/7 | Tow Truck Near You | {NAME}",
    f"Local 24/7 tow truck in Mississauga, ON. Local towing, boosts, lockouts and accident recovery. Port Credit to Malton. Call {PHONE}.",
    miss_body, schema=[breadcrumb_schema(trail), faq_schema(MISS_FAQ)], active="/towing-mississauga.html"), priority="0.9")


# ---------- Service pages
SERVICE_PAGES = {
    "emergency-towing": {
        "title": f"24/7 Emergency Towing Mississauga | {NAME}",
        "desc": f"Emergency tow truck in Mississauga, open 24/7. Breakdowns, no-starts and local towing to your home, mechanic or dealer. Price upfront. Call {PHONE}.",
        "h1": "24/7 Emergency Towing in Mississauga",
        "lead": "Car broke down, won't start, or isn't safe to drive? We'll tow it wherever you need — any hour of the day or night.",
        "body": f"""
<h2>When to call for an emergency tow</h2>
<p>Breakdowns never happen at a convenient time. We take calls around the clock for:</p>
<ul>
  <li>Engines that stall, overheat or won't start</li>
  <li>Transmission, brake or steering problems that make the car unsafe to drive</li>
  <li>Warning lights and strange noises you don't want to risk driving on</li>
  <li>Vehicles stuck in accessible local areas, in a ditch or in a snowbank</li>
  <li>Cars that need to get to a mechanic first thing in the morning</li>
</ul>
<h2>What's included</h2>
<p>Every emergency tow includes a phone quote before we dispatch, an arrival estimate, proper securing of your vehicle, and delivery to the address you choose — your home, your mechanic, a dealership or a body shop. We tow cars, SUVs, minivans and light-duty trucks.</p>
<h2>Local roadside towing</h2>
<p>We assist with breakdowns on authorized local streets and accessible private property. Restricted towing zones are excluded. In a restricted zone, call Ontario 511 if safe, or 911 in an emergency.</p>
<h2>Where we'll take your car</h2>
<p>You decide. In Ontario you have the right to choose where your vehicle is towed (unless police direct otherwise). If you don't have a mechanic, we can suggest some nearby options — the choice is always yours.</p>
""",
        "faq": [
            ("Can you tow my car at night or on a holiday?", "Yes — we operate 24 hours a day, 7 days a week, including holidays."),
            ("Can I ride in the tow truck?", "Ask when you call. When there's room and it's safe, we can usually take one passenger with the vehicle."),
            ("My car is in a parking garage. Can you still tow it?", "Often yes. Tell us the location and, if you know it, the garage clearance height, and we'll confirm on the phone."),
        ],
    },
    "roadside-assistance": {
        "title": f"Roadside Assistance Mississauga: Boost & Lockout | {NAME}",
        "desc": f"24/7 roadside assistance in Mississauga: battery boosts, car lockouts and flat tire changes. Often no tow needed. Call or text {PHONE}.",
        "h1": "Roadside Assistance in Mississauga",
        "lead": "Dead battery, flat tire or keys locked in the car? We'll come to you and, in many cases, get you back on the road without a tow.",
        "body": f"""
<h2>Battery boost (jump start)</h2>
<p>Cold Ontario mornings are hard on batteries. If your car clicks but won't crank, we'll come to your driveway, office lot or roadside location and give you a boost. If the battery won't hold a charge, we can tow you to a shop for a replacement.</p>
<h2>Flat tire change</h2>
<p>Blown or flat tire? We'll safely put on your spare so you can drive to a tire shop. No usable spare, or a damaged wheel? We'll tow you to the tire shop or mechanic of your choice.</p>
<h2>Car lockout service</h2>
<p>Keys locked inside, or locked in the trunk? We'll help you get back in. For your protection we'll ask you to show proof that the vehicle is yours.</p>
<h2>Where we provide roadside help</h2>
<p>Authorized locations in {CITY} — home driveways, condo and office parking, plazas, and authorized local streets — plus {", ".join(OTHER_AREAS)}.</p>
""",
        "faq": [
            ("Is roadside assistance cheaper than a tow?", "Usually yes. If a boost, tire change or lockout solves the problem, you avoid a tow entirely. Call and we'll quote both options."),
            ("What if the boost doesn't work?", "We can tow your vehicle straight to a mechanic or battery shop on the same call."),
            ("Do you need anything from me for a lockout?", "Yes — we'll ask for ID and proof of ownership (for example the registration, once the car is open) before we hand the vehicle over."),
        ],
    },
    "accident-recovery": {
        "title": f"Accident Towing & Recovery Mississauga | {NAME}",
        "desc": f"Accident towing in Mississauga, 24/7. Careful recovery of damaged vehicles, tow to a body shop or Collision Reporting Centre of your choice. Call {PHONE}.",
        "h1": "Accident Towing &amp; Recovery in Mississauga",
        "lead": "After a collision, the last thing you need is more stress. We recover and tow your vehicle carefully — to the place you choose.",
        "body": f"""
<h2>After an accident: what to do</h2>
<ol>
  <li><strong>Make sure everyone is safe.</strong> If anyone is injured, call 911 first.</li>
  <li><strong>Move to safety if you can.</strong> Turn on your hazard lights.</li>
  <li><strong>Exchange information</strong> with the other driver and take photos of the scene and damage.</li>
  <li><strong>Call us at <a href="{TEL}">{PHONE}</a></strong> — we'll tell you the price and when we'll arrive.</li>
</ol>
<div class="callout"><p><strong>Your rights in Ontario:</strong> you choose who tows your vehicle and where it goes, unless police direct otherwise. You should get the price before the tow and an itemized invoice after. If someone at the scene pressures you to sign, take your time.</p></div>
<h2>Where we can take your vehicle</h2>
<ul>
  <li>A <strong>Collision Reporting Centre</strong> — for minor collisions with no injuries, Peel Regional Police may ask you to report there</li>
  <li>The <strong>body shop</strong> you or your insurer choose</li>
  <li>Your <strong>dealership</strong> or <strong>home</strong></li>
</ul>
<h2>Careful recovery of damaged vehicles</h2>
<p>Damaged vehicles need extra care — locked wheels, leaking fluids, broken glass and loose parts. We secure everything properly and clean up debris from the vehicle before we leave.</p>
<h2>Help with your insurance claim</h2>
<p>We'll give you a clear receipt for the tow and can take photos of the vehicle at pickup, which can help your insurance claim.</p>
""",
        "faq": [
            ("Do I have to use the tow truck that shows up at the accident?", "No. In Ontario you have the right to choose your tow company and where your vehicle goes, unless police direct otherwise. You can call us directly."),
            ("Can you tow to a Collision Reporting Centre and then to the body shop?", "Yes — tell us when you call and we'll plan the route and quote it up front."),
            ("Will my insurance cover the tow?", "Many policies do. Keep your receipt and check with your insurer; we'll give you everything you need for the claim."),
        ],
    },
    "vehicle-transport": {
        "title": f"Car Transport & Long-Distance Towing | {NAME}",
        "desc": f"Car transport from Mississauga across the GTA and Ontario. Dealer, auction and private-sale pickups, non-running vehicles. Quote: {PHONE}.",
        "h1": "Vehicle Transport &amp; Long-Distance Towing",
        "lead": "Bought a car out of town? Moving a project car or a vehicle that doesn't run? We move vehicles safely across the GTA and Ontario.",
        "body": f"""
<h2>What we transport</h2>
<ul>
  <li>Cars bought from a <strong>dealer, auction or private seller</strong></li>
  <li><strong>Non-running</strong> and project vehicles</li>
  <li>Vehicles going to or from a <strong>mechanic, body shop or storage</strong></li>
  <li>Cars for people <strong>moving</strong> to or from {CITY}</li>
</ul>
<h2>Local and long-distance</h2>
<p>We handle short moves inside {CITY} and Peel, trips across the GTA — {", ".join(OTHER_AREAS)} — and longer runs across Ontario. Tell us the pickup and drop-off addresses and we'll quote the trip before we book.</p>
<h2>How booking works</h2>
<ol>
  <li>Call, text or <a href="/contact.html#request">send the request form</a> with the pickup, drop-off and vehicle details.</li>
  <li>We confirm the price and a pickup time that works for you.</li>
  <li>We load and secure the vehicle and deliver it to the destination.</li>
</ol>
""",
        "faq": [
            ("Can you pick up a car I bought from a private seller?", "Yes. We'll coordinate the pickup time with you and the seller."),
            ("Does the car need to run?", "No. We transport non-running vehicles too — just tell us when you book so we bring the right equipment."),
            ("How far will you go?", "Across the GTA and throughout Ontario. Call with the route and we'll give you a quote."),
        ],
    },
}

for s in SERVICES:
    sp = SERVICE_PAGES[s["slug"]]
    path = f"/services/{s['slug']}.html"
    trail = [("Home", "/"), ("Services", "/services/"), (sp["h1"].replace(" in Mississauga", ""), path)]
    svc_schema = {
        "@type": "Service",
        "@id": DOMAIN + path + "#service",
        "name": html.unescape(sp["h1"]),
        "serviceType": s["name"],
        "provider": {"@id": DOMAIN + "/#business"},
        "areaServed": [{"@type": "City", "name": f"{a}, {S['region']}"} for a in AREAS],
        "url": DOMAIN + path,
        "description": sp["desc"],
        "hoursAvailable": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"},
    }
    body = page_hero(trail, sp["h1"], sp["lead"]) + f"""
<section class="section">
  <div class="wrap split">
    <div class="prose">
      {sp["body"]}
      <h2>Frequently asked questions</h2>
      {faq_block(sp["faq"])}
    </div>
    <aside class="aside-stack">
      <div class="card"><h3>{s["name"]}</h3><ul class="checks">{"".join(f"<li>{icon('check')}<span>{b}</span></li>" for b in s["bullets"])}</ul>
        <div class="btn-row">{call_btn("btn btn-call")}{text_btn("btn btn-outline", "Text us")}</div></div>
      <div class="card"><h3>Serving</h3><p class="muted">Based in <a href="/towing-mississauga.html">{CITY}</a>, also covering:</p>{area_chips()}</div>
    </aside>
  </div>
</section>
<section class="section soft">
  <div class="wrap">
    <div class="section-head"><h2>Other services</h2></div>
    {service_cards(exclude=s["slug"])}
  </div>
</section>
{cta_band()}
"""
    add(path, f"services/{s['slug']}.html", layout(
        path, sp["title"], sp["desc"], body,
        schema=[svc_schema, breadcrumb_schema(trail), faq_schema(sp["faq"])], active="/services/"), priority="0.8")

# ---------- Services index
trail = [("Home", "/"), ("Services", "/services/")]
svc_index = page_hero(trail, "Towing &amp; Roadside Services in Mississauga",
                      "One call for every towing and roadside problem — 24 hours a day, 7 days a week.") + f"""
<section class="section">
  <div class="wrap">{service_cards()}</div>
</section>
{reviews_section()}
{cta_band()}
"""
add("/services/", "services/index.html", layout(
    "/services/", f"Towing Services Mississauga | {NAME}",
    f"Emergency towing, roadside assistance, accident recovery and vehicle transport in Mississauga and nearby. Open 24/7. Call {PHONE}.",
    svc_index, schema=[breadcrumb_schema(trail)], active="/services/"), priority="0.8")


# ---------- Service areas
trail = [("Home", "/"), ("Service Areas", "/service-areas.html")]
blocks = f"""<article class="card" id="{CITY.lower()}"><span class="kicker">Home base</span><h3>{CITY}</h3>
<p class="muted">Local streets and accessible properties from Port Credit to Malton, subject to availability.</p>
<a class="more" href="/towing-mississauga.html">Towing in {CITY} {icon('arrow')}</a></article>"""
for a in OTHER_AREAS:
    blocks += f"""<article class="card" id="{a.lower()}"><h3>Towing in {e(a)}</h3><p class="muted">{AREA_BLURBS.get(a, f"Towing, roadside assistance and vehicle transport in {e(a)}.")}</p>
<a class="more" href="{TEL}">Call {PHONE} {icon('arrow')}</a></article>"""
areas_body = page_hero(trail, "Service Areas",
                       f"Based in {CITY}, we tow and help drivers across Peel, Halton and the west GTA — 24/7.") + f"""
<section class="section">
  <div class="wrap"><div class="grid grid-3">{blocks}</div>
  <p class="muted" style="margin-top:2rem">Not sure if we cover your location? Call or text <a href="{TEL}">{PHONE}</a> — if we can get to you, we will.</p></div>
</section>
{cta_band()}
"""
add("/service-areas.html", "service-areas.html", layout(
    "/service-areas.html", f"Service Areas: Mississauga, {', '.join(OTHER_AREAS[:2])} | {NAME}",
    f"{NAME} provides 24/7 towing and roadside assistance in {', '.join(AREAS)}. Call {PHONE}.",
    areas_body, schema=[breadcrumb_schema(trail)], active="/service-areas.html"), priority="0.7")


# ---------- Reviews
trail = [("Home", "/"), ("Reviews", "/reviews.html")]
all_reviews = review_cards(all_layout=True)
if all_reviews:
    rev_inner = all_reviews + google_buttons()
else:
    rev_inner = f"""<div class="review-cta card"><p class="g-badge" style="justify-content:center">{GOOGLE_G}Reviews on Google</p>
<p class="muted">Our customer reviews live on our Google Business Profile.</p>{google_buttons()}</div>"""
reviews_body = page_hero(trail, "Customer Reviews",
                         f"Real reviews from drivers we've helped in {CITY} and nearby, from our Google Business Profile.", buttons=False) + f"""
<section class="section">
  <div class="wrap">{rev_inner}
  <div class="callout" style="max-width:720px;margin:2.5rem auto 0"><p><strong>Did we help you?</strong> A short Google review takes a minute and helps other drivers find a tow company they can trust. Thank you!</p></div></div>
</section>
{cta_band()}
"""
add("/reviews.html", "reviews.html", layout(
    "/reviews.html", f"Reviews | {NAME} — Mississauga Towing",
    f"Read Google reviews from customers of {NAME}, a 24/7 towing and roadside assistance company in Mississauga, ON.",
    reviews_body, schema=[breadcrumb_schema(trail)], active="/reviews.html"), priority="0.6")


# ---------- About
trail = [("Home", "/"), ("About", "/about.html")]
since = f" since {S['founded_year']}" if S.get("founded_year") else ""
licensed = "<li>Licensed and insured for towing in Ontario</li>" if S.get("licensed_insured") else ""
about_body = page_hero(trail, f"About {NAME}",
                       f"A local {CITY} towing and roadside assistance company{since}, built on answering the phone and treating every car like our own.", buttons=False) + f"""
<section class="section">
  <div class="wrap split">
    <div class="prose">
      <h2>Who we are</h2>
      <p>{NAME} is a towing and roadside assistance company based in {CITY}, Ontario. We help drivers who are stuck — broken down on a local street, locked out at the mall, dealing with a dead battery on a cold morning, or shaken up after a collision — and we move vehicles for people and businesses across the GTA.</p>
      <p>We keep it simple: answer the phone 24/7, give a clear price before we dispatch, provide an arrival estimate, and handle every vehicle carefully.</p>
      <h2>What we stand for</h2>
      <ul>
        <li><strong>Honest pricing.</strong> You get the price before we send a truck — no surprises on the invoice.</li>
        <li><strong>Respect for your choice.</strong> Your vehicle goes where you want it to go.</li>
        <li><strong>Safety.</strong> For you on the roadside, and for your vehicle on our truck.</li>
        <li><strong>Local service.</strong> We live and work in {CITY} and the surrounding communities.</li>
        {licensed}
      </ul>
      <h2>What we do</h2>
      <ul>{"".join(f'<li><a href="/services/{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)}</ul>
    </div>
    <aside class="aside-stack">
      <div class="card"><h3>Contact</h3>{contact_list()}</div>
    </aside>
  </div>
</section>
{gallery_section()}
{reviews_section()}
{cta_band()}
"""
add("/about.html", "about.html", layout(
    "/about.html", f"About {NAME} | Local Mississauga Towing Company",
    f"{NAME} is a local 24/7 towing and roadside assistance company in Mississauga, ON. Honest pricing, careful handling, always open.",
    about_body, schema=[breadcrumb_schema(trail)], active="/about.html"), priority="0.6")


# ---------- Contact
trail = [("Home", "/"), ("Contact", "/contact.html")]
contact_body = page_hero(trail, "Contact ABR Pro Towing & Recovery",
                         f"Need a tow right now? Call — we answer 24/7. For quotes and planned transports, use the form.") + f"""
<section class="section">
  <div class="wrap split">
    <div>
      <h2>Get in touch</h2>
      {contact_list()}
      <h3 style="margin-top:2rem">Service areas</h3>
      {area_chips()}
    </div>
    {tow_form("Request a tow or a quote")}
  </div>
</section>
<section class="section soft">
  <div class="wrap">
    <div class="section-head"><h2>Where we work</h2><p class="muted">We're a mobile service — we come to you within authorized areas in {CITY} and nearby cities.</p></div>
    <iframe class="map" title="Map of Mississauga, Ontario service area" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
      src="https://maps.google.com/maps?q=Mississauga%2C%20ON%2C%20Canada&amp;z=11&amp;output=embed"></iframe>
  </div>
</section>
"""
add("/contact.html", "contact.html", layout(
    "/contact.html", f"Contact Us | 24/7 Tow Truck Mississauga | {PHONE}",
    f"Call or text {PHONE} for 24/7 towing in Mississauga, or email {EMAIL}. Request a tow or a vehicle transport quote online.",
    contact_body, schema=[breadcrumb_schema(trail)], active="/contact.html"), priority="0.8")


# ---------- Thank you / privacy / 404
ty_body = f"""
<section class="section"><div class="wrap narrow" style="text-align:center">
  <h1>Thanks — we got your request</h1>
  <p class="lead" style="color:var(--muted);margin-inline:auto">We'll call or text you back shortly. If you're stranded or it's urgent, please call us now.</p>
  <div class="btn-row" style="justify-content:center;margin-top:1.5rem">{call_btn("btn btn-call btn-lg")}<a class="btn btn-outline btn-lg" href="/">Back to home</a></div>
</div></section>"""
add("/thank-you.html", "thank-you.html", layout("/thank-you.html", f"Request received | {NAME}",
    "Thanks for contacting ABR Pro Towing & Recovery.", ty_body, noindex=True), sitemap=False)

privacy_body = page_hero([("Home", "/"), ("Privacy", "/privacy.html")], "Privacy note", "How we handle the information you send us.", buttons=False) + f"""
<section class="section"><div class="wrap narrow prose">
  <p>When you send our request form, we receive your name, phone number, optional email, locations and the details you type. We use this only to respond to your request, arrange your tow or service, and keep a record of the job.</p>
  <p>Form messages are delivered to our email through the FormSubmit service. We don't sell or share your information for marketing.</p>
  <p>Google Maps and optional Google review requests may transmit data to Google under its privacy policy and terms of service. We do not store Google review content.</p>
  <p>To ask about or delete your information, email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  <p class="muted">Last updated {fmt_date(TODAY)}.</p>
</div></section>"""
add("/privacy.html", "privacy.html", layout("/privacy.html", f"Privacy | {NAME}",
    f"Privacy note for {NAME}.", privacy_body), priority="0.2")

nf_body = f"""
<section class="section"><div class="wrap narrow" style="text-align:center">
  <p class="kicker">404</p>
  <h1>This page broke down</h1>
  <p class="lead" style="color:var(--muted);margin-inline:auto">The page you're looking for doesn't exist. If you need a tow, we're one tap away.</p>
  <div class="btn-row" style="justify-content:center;margin-top:1.5rem">{call_btn("btn btn-call btn-lg")}<a class="btn btn-outline btn-lg" href="/">Go to home page</a></div>
</div></section>"""
add("/404.html", "404.html", layout("/404.html", f"Page not found | {NAME}",
    "Page not found.", nf_body, noindex=True), sitemap=False)


# ---------- redirect stubs for old template URLs
def redirect_stub(target):
    return f"""<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><title>Moved — {e(NAME)}</title>
<link rel="canonical" href="{DOMAIN}{target}"><meta name="robots" content="noindex, follow">
<meta http-equiv="refresh" content="0; url={target}"><script>location.replace("{target}")</script></head>
<body><p>This page has moved: <a href="{target}">{DOMAIN}{target}</a></p></body></html>
"""


REDIRECTS = {"service.html": "/services/", "booking.html": "/contact.html", "team.html": "/about.html", "testimonial.html": "/reviews.html"}


# ------------------------------------------------------------------ write
def write(rel, content):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)


for path, filename, out, _, _ in PAGES:
    write(filename, out)
for f, t in REDIRECTS.items():
    write(f, redirect_stub(t))

urls = "".join(
    f"  <url><loc>{DOMAIN}{path}</loc><lastmod>{TODAY}</lastmod></url>\n"
    for path, _, _, inc, prio in PAGES if inc
)
write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')

write("robots.txt", f"""# {NAME} — all search engines and AI assistants are welcome.
User-agent: *
Allow: /

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: GPTBot
Disallow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Applebot
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
""")

svc_lines = "\n".join(f"- [{s['name']}]({DOMAIN}/services/{s['slug']}.html): {html.unescape(s['short'])}" for s in SERVICES)
write("llms.txt", f"""# {NAME}

> {NAME} is a 24/7 towing and roadside assistance company based in {CITY}, {S['region_full']}, Canada. Phone: {PHONE}. Email: {EMAIL}. Open 24 hours, 7 days a week. Service area: {', '.join(AREAS)}. Services are available within our authorized operating areas. Restricted towing zones are excluded.

## Services
{svc_lines}

## Key pages
- [Towing in Mississauga]({DOMAIN}/towing-mississauga.html): neighbourhoods, local roads, FAQs
- [Service areas]({DOMAIN}/service-areas.html)
- [Reviews]({DOMAIN}/reviews.html)
- [About]({DOMAIN}/about.html)
- [Contact]({DOMAIN}/contact.html)
""")

print(f"Built {len(PAGES)} pages + {len(REDIRECTS)} redirects, sitemap.xml, robots.txt, llms.txt")
