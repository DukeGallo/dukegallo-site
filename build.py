#!/usr/bin/env python3
"""Builds dukegallo.com from src/ into dist/.

src/home.html        homepage template (contains {{LATEST_POSTS}})
src/duke.jpg.b64     portrait, base64
src/posts/*.json     one file per post:
  slug, title, description, date (YYYY-MM-DD), category, keywords [list],
  image (https URL), image_alt, image_credit, image_credit_url, body_html
Usage: python3 build.py <src_dir> <dist_dir>
"""
import json, os, sys, base64, html, re, glob, shutil, datetime

SITE = "https://dukegallo.com"
AUTHOR = "Duke Gallo"
NMLS = "2084855"
INSTAGRAM = "https://www.instagram.com/dukegallo/"
LINKEDIN = "https://www.linkedin.com/in/duke-gallo/"
# --- Company transition: Duke joins West Capital Lending on START_WCL ---
from zoneinfo import ZoneInfo
TODAY = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).date()
if os.environ.get("BUILD_DATE"):  # for previews: BUILD_DATE=2026-12-01 python3 build.py . /tmp/x
    TODAY = datetime.date.fromisoformat(os.environ["BUILD_DATE"])
START_WCL = datetime.date(2026, 12, 1)
AT_WCL = TODAY >= START_WCL
WCL_NMLS = "1566096"
if AT_WCL:
    PH = {
        "TITLE": "Duke Gallo | Mortgage Broker &amp; VP, West Capital Lending",
        "DESC": "Duke Gallo, Vice President at West Capital Lending, is a licensed mortgage broker in Southern California helping buyers, homeowners, and loan officers.",
        "INTRO": "Mortgage broker, team leader, and Vice President at West Capital Lending. I build teams that help people buy and keep their homes.",
        "WCL_WHEN": "Dec 2026 – Now",
        "WCL_DESC": "Leading and mentoring loan officers, building the team, and helping clients across Southern California find the right financing.",
        "ABOUT_NOW": "Today I'm a Vice President at West Capital Lending.",
        "LICENSE_LINE": f"Duke Gallo, NMLS #{NMLS}, licensed by the California Department of Financial Protection and Innovation · West Capital Lending, Inc., NMLS #{WCL_NMLS} · Equal Housing Opportunity.",
        "BYLINE": "Vice President, West Capital Lending",
        "JOIN_LEAD": "I'm a Vice President at West Capital Lending, building a team of loan officers who want to grow, serve clients well, and have a leader in their corner.",
    }
    OG_FILE = "og-image.jpg"
else:
    PH = {
        "TITLE": "Duke Gallo | Mortgage Broker &amp; Team Leader, Southern California",
        "DESC": "Duke Gallo is a licensed mortgage broker and team leader in Southern California, joining West Capital Lending as Vice President on December 1, 2026.",
        "INTRO": "Mortgage broker and team leader, joining West Capital Lending as Vice President on December 1. I build teams that help people buy and keep their homes.",
        "WCL_WHEN": "From Dec 2026",
        "WCL_DESC": "Joining West Capital Lending as Vice President on December 1, 2026, to lead and grow a team of loan officers serving clients across Southern California.",
        "ABOUT_NOW": "On December 1, 2026, I'm joining West Capital Lending as Vice President.",
        "LICENSE_LINE": f"Duke Gallo, NMLS #{NMLS}, licensed by the California Department of Financial Protection and Innovation · Joining West Capital Lending, Inc. (NMLS #{WCL_NMLS}) on December 1, 2026 · Equal Housing Opportunity.",
        "BYLINE": "Mortgage broker, NMLS #" + NMLS,
        "JOIN_LEAD": "On December 1, 2026, I'm joining West Capital Lending as Vice President, and I'm building a team of loan officers who want to grow, serve clients well, and have a leader in their corner.",
    }
    OG_FILE = "og-image-joining.jpg"
OG_DEFAULT = f"{SITE}/{OG_FILE}"
_site = json.load(open(os.path.join(sys.argv[1], "site.json")))
APPLY_URL = _site["apply_url"]
STATES = _site["states"]
STATE_NAMES = ", ".join(n for c, n in STATES)
APPLY_A = f'href="{APPLY_URL}" target="_blank" rel="noopener"'
ICONS = """<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#1d5b78">"""
PERSON = {"@type": "Person", "@id": SITE + "/#duke", "name": "Duke Gallo", "url": SITE + "/",
          "image": SITE + "/duke.jpg", "jobTitle": "Vice President, Mortgage Loan Originator",
          "alumniOf": {"@type": "CollegeOrUniversity", "name": "San Francisco State University"},
          "address": {"@type": "PostalAddress", "addressRegion": "CA", "addressCountry": "US"},
          "knowsAbout": ["Mortgages", "Home loans", "Refinancing", "FHA loans", "VA loans", "Jumbo loans", "Non-QM loans", "Real estate finance"],
          "identifier": {"@type": "PropertyValue", "propertyID": "NMLS", "value": NMLS},
          "sameAs": [LINKEDIN, INSTAGRAM]}
if AT_WCL:
    PERSON["worksFor"] = {"@type": "Organization", "name": "West Capital Lending, Inc.", "identifier": {"@type": "PropertyValue", "propertyID": "NMLS", "value": WCL_NMLS}}

src, dist = sys.argv[1], sys.argv[2]
shutil.rmtree(dist, ignore_errors=True)
os.makedirs(dist)

posts = []
for f in glob.glob(os.path.join(src, "posts", "*.json")):
    p = json.load(open(f))
    for k in ["slug", "title", "description", "date", "category", "image", "image_alt", "body_html"]:
        assert p.get(k), f"{f}: missing {k}"
    assert re.fullmatch(r"[a-z0-9-]+", p["slug"]), f"bad slug {p['slug']}"
    if datetime.date.fromisoformat(p["date"]) > TODAY:
        continue  # scheduled for later
    posts.append(p)
posts.sort(key=lambda p: p["date"], reverse=True)
slugs = [p["slug"] for p in posts]
assert len(slugs) == len(set(slugs)), "duplicate slug"

def esc(s): return html.escape(s, quote=True)
def nice_date(d): return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")
def read_min(body): return max(2, round(len(re.sub(r"<[^>]+>", " ", body).split()) / 225))

FONTS = ICONS + '\n<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Figtree:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">'

CSS = """
:root{--bg:#f7f8f9;--surface:#fff;--ink:#14202b;--muted:#5b6872;--line:#dfe3e7;--accent:#1d5b78;--accent-soft:#e6eff3;
--display:"Bricolage Grotesque","Helvetica Neue",Arial,sans-serif;--body:"Figtree","Helvetica Neue",Arial,sans-serif;--mono:"JetBrains Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#0f1519;--surface:#151d22;--ink:#e8edf0;--muted:#94a1aa;--line:#26323a;--accent:#7fbcd6;--accent-soft:#1a2c35;color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.7 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
img{max-width:100%;height:auto}a{color:var(--accent)}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.wrap{max-width:1040px;margin:0 auto}
.skip{position:absolute;left:-9999px;top:8px;background:var(--ink);color:var(--bg);padding:8px 14px;border-radius:8px;z-index:20}.skip:focus{left:16px}
h1,h2,h3{font-family:var(--display);font-weight:700;line-height:1.12;letter-spacing:-.015em;text-wrap:balance}
.label{font:500 12px/1.2 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
header.top{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-block:24px;flex-wrap:wrap}
.mark{font:700 18px/1 var(--display);color:var(--ink);text-decoration:none}
nav{display:flex;gap:24px;flex-wrap:wrap}nav a{color:var(--muted);text-decoration:none;font-weight:500;font-size:15px}
nav a:hover,nav a[aria-current]{color:var(--ink)}
.nav-apply{color:var(--accent)!important;font-weight:600;border:1px solid var(--accent);border-radius:999px;padding:3px 12px}
.blog-head{padding-block:48px 32px;border-bottom:1px solid var(--line)}
.blog-head h1{font-size:clamp(40px,7vw,72px);margin:12px 0 0}
.blog-head p{max-width:56ch;color:var(--muted);font-size:19px;margin:16px 0 0}
.filters{display:flex;flex-wrap:wrap;gap:8px;padding-top:28px}
.fchip{font:500 14px var(--body);min-height:40px;padding:8px 16px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer}
.fchip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.card[hidden]{display:none}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:40px 28px;padding-block:48px 72px}
.card{display:flex;flex-direction:column;gap:12px;text-decoration:none;color:inherit;min-width:0}
.card img{aspect-ratio:16/10;object-fit:cover;width:100%;border-radius:12px;background:var(--accent-soft)}
.card h2,.card h3{font-size:21px;margin:0}.card p{margin:0;color:var(--muted);font-size:15.5px}
.card:hover h2,.card:hover h3{color:var(--accent)}
.meta{font:500 12.5px var(--mono);color:var(--muted);display:flex;gap:12px;flex-wrap:wrap}
article{max-width:720px;margin:0 auto;padding-block:40px 24px}
article h1{font-size:clamp(34px,5.5vw,52px);margin:14px 0 18px}
article .dek{font-size:20px;color:var(--muted);margin:0 0 24px;line-height:1.5}
.hero-img{margin:32px 0 8px}.hero-img img{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:14px;background:var(--accent-soft)}
.credit{font-size:12.5px;color:var(--muted)}
.body h2{font-size:28px;margin:44px 0 10px}.body h3{font-size:21px;margin:32px 0 8px}
.body p,.body li{max-width:68ch}.body li{margin-bottom:6px}
.body blockquote{margin:28px 0;padding:4px 0 4px 20px;border-left:3px solid var(--accent);font-size:19px}
.body table{border-collapse:collapse;width:100%;font-size:15.5px}.tbl{overflow-x:auto;margin:24px 0}
.body th,.body td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}
.body th{font:500 12px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.byline{display:flex;align-items:center;gap:12px;margin-top:8px}
.byline img{width:44px;height:44px;border-radius:50%;object-fit:cover}
.byline b{display:block;font-weight:600}.byline span{font-size:14px;color:var(--muted)}
.cta{margin:48px 0;padding:28px;border-radius:14px;background:var(--accent-soft)}
.cta h2{font-size:24px;margin:0 0 8px}.cta p{margin:0 0 6px}
.more{border-top:1px solid var(--line);padding-block:40px}
.more .cards{padding-block:24px 0}
footer{padding-block:32px 48px;border-top:1px solid var(--line);font-size:12.5px;color:var(--muted)}
footer p{margin:0 0 8px;max-width:90ch}
.btn{display:inline-flex;align-items:center;min-height:44px;padding:10px 18px;border-radius:999px;font-weight:600;font-size:15px;text-decoration:none;border:1px solid var(--accent);color:var(--accent);background:none}
.btn.primary{background:var(--accent);color:var(--bg)}
.cta-inline{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 8px}
.form{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:20px 0}
.form .full{grid-column:1/-1}
.form label{display:flex;flex-direction:column;gap:6px;font-size:14px;font-weight:500;color:var(--muted)}
.form input,.form select,.form textarea{font:400 16px var(--body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;min-height:46px;width:100%}
.form textarea{min-height:110px;resize:vertical}
.form .check{flex-direction:row;align-items:flex-start;gap:10px;font-weight:400;font-size:13.5px;line-height:1.5}
.form .check input{width:20px;min-height:20px;margin-top:2px;flex:none}
.form button{justify-self:start;cursor:pointer;font-family:var(--body)}
.hp{position:absolute;left:-9999px}
@media (max-width:600px){.form{grid-template-columns:1fr}}
@media (max-width:820px){.cards{grid-template-columns:1fr 1fr}}
@media (max-width:520px){.cards{grid-template-columns:1fr}nav{gap:16px}}
"""

FOOTER = f"""<footer>
    <p>{PH["LICENSE_LINE"]} Verify licensing at <a href="https://www.nmlsconsumeraccess.org/" target="_blank" rel="noopener">nmlsconsumeraccess.org</a>.</p>
    <p>Blog content is for general education only and is not a commitment to lend, a rate quote, or financial, legal, or tax advice. All loans are subject to credit approval and underwriting. Not all applicants will qualify. Programs and guidelines change; contact me for current details.</p>
    <p><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram</a> · <a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a> · <a href="/blog/">Blog</a> · <a href="/join/">Join my team</a> · <a href="/privacy/">Privacy</a> · <a {APPLY_A}>Apply now</a></p>
    <p>Licensed mortgage loan originator in: {STATE_NAMES}.</p>
    <p>© {datetime.date.today().year} Duke Gallo</p>
  </footer>"""

def header(active):
    return f"""<header class="top">
    <a class="mark" href="/">DG</a>
    <nav aria-label="Primary">
      <a href="/#about">About</a><a href="/#career">Career</a><a href="/blog/"{' aria-current="page"' if active=='blog' else ''}>Blog</a><a href="/join/"{' aria-current="page"' if active=='join' else ''}>Join my team</a><a href="/#contact">Contact</a><a class="nav-apply" {APPLY_A}>Apply now</a>
    </nav>
  </header>"""

def page(title, desc, canonical, body, og_type="website", image=None, jsonld=None, extra_head="", noindex=False):
    img = image or OG_DEFAULT
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">{'\n<meta name="robots" content="noindex">' if noindex else ''}
<meta name="author" content="{AUTHOR}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{esc(img)}">
<meta property="og:site_name" content="Duke Gallo">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(img)}">
<meta property="og:locale" content="en_US">
<link rel="alternate" type="application/rss+xml" title="Duke Gallo Blog" href="{SITE}/blog/feed.xml">
{extra_head}{FONTS}
<style>{CSS}</style>
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="wrap">
  {body}
  {FOOTER}
</div>
</body>
</html>
"""

def small(u): return u.replace("w=1600", "w=720")
def card(p, h="h2"):
    return f"""<a class="card" data-cat="{esc(p['category'])}" href="/blog/{p['slug']}/">
        <img src="{esc(small(p['image']))}" alt="{esc(p['image_alt'])}" loading="lazy" decoding="async" width="720" height="450">
        <div class="meta"><span>{esc(p['category'])}</span><span>{nice_date(p['date'])}</span></div>
        <{h}>{esc(p['title'])}</{h}>
        <p>{esc(p['description'])}</p>
      </a>"""

# Post pages
for i, p in enumerate(posts):
    url = f"{SITE}/blog/{p['slug']}/"
    others = [q for q in posts if q["slug"] != p["slug"]][:3]
    more = ""
    if others:
        more = '<section class="more"><div class="label">Keep reading</div><div class="cards">' + "".join(card(q, "h3") for q in others) + "</div></section>"
    credit = ""
    if p.get("image_credit"):
        credit = f'<figcaption class="credit">Photo: <a href="{esc(p.get("image_credit_url",""))}" rel="noopener" target="_blank">{esc(p["image_credit"])}</a> on Unsplash</figcaption>'
    body = f"""{header('blog')}
  <main id="main"><article>
    <div class="meta"><a href="/blog/">Blog</a><span>{esc(p['category'])}</span><span>{read_min(p['body_html'])} min read</span></div>
    <h1>{esc(p['title'])}</h1>
    <p class="dek">{esc(p['description'])}</p>
    <div class="byline"><img src="/duke.jpg" alt="Duke Gallo" width="44" height="44"><div><b>Duke Gallo</b><span>{PH["BYLINE"]} · <time datetime="{p['date']}">{nice_date(p['date'])}</time></span></div></div>
    <figure class="hero-img" style="margin-inline:0"><img src="{esc(p['image'])}" alt="{esc(p['image_alt'])}" width="1440" height="810" fetchpriority="high">{credit}</figure>
    <div class="body">
{p['body_html']}
    </div>
    <aside class="cta">
      <h2>Have a question about your situation?</h2>
      <p>Call or text me at <a href="tel:+19496885959"><b>(949) 688-5959</b></a> or email <a href="mailto:dgallo@westcapitallending.com"><b>dgallo@westcapitallending.com</b></a>. Ready to get started? You can apply online in a few minutes.</p>
      <p class="cta-inline" style="margin-top:14px"><a class="btn primary" {APPLY_A}>Apply now</a><a class="btn" href="/join/">Loan officer? Join my team</a></p>
    </aside>
  </article>
  {more}</main>"""
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BlogPosting", "headline": p["title"], "description": p["description"],
             "image": p["image"], "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
             "mainEntityOfPage": url, "keywords": ", ".join(p.get("keywords", [])),
             "author": PERSON, "publisher": {"@id": SITE + "/#duke"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]}
    if p.get("faq"):
        ld["@graph"].append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in p["faq"]]})
    kw = f'<meta name="keywords" content="{esc(", ".join(p.get("keywords", [])))}">\n<meta property="article:published_time" content="{p["date"]}">\n'
    os.makedirs(os.path.join(dist, "blog", p["slug"]), exist_ok=True)
    open(os.path.join(dist, "blog", p["slug"], "index.html"), "w").write(
        page(f"{p['title']} | Duke Gallo", p["description"], url, body, "article", p["image"], ld, kw))

# Blog index
cards = "".join(card(p) for p in posts) or '<p>New posts are on the way.</p>'
cats = sorted({p["category"] for p in posts})
filters = '<div class="filters" role="group" aria-label="Filter posts by topic"><button type="button" class="fchip" aria-pressed="true" data-cat="">All</button>' + "".join(f'<button type="button" class="fchip" aria-pressed="false" data-cat="{esc(c)}">{esc(c)}</button>' for c in cats) + "</div>"
filter_js = """<script>(function(){var b=document.querySelectorAll('.fchip'),c=document.querySelectorAll('.cards .card');b.forEach(function(x){x.addEventListener('click',function(){b.forEach(function(y){y.setAttribute('aria-pressed',y===x)});var k=x.dataset.cat;c.forEach(function(d){d.hidden=!!k&&d.dataset.cat!==k})})})})();</script>"""
blog_body = f"""{header('blog')}
  <main id="main"><div class="blog-head">
    <div class="label">The Duke Gallo Blog</div>
    <h1>Mortgages, real estate, and building a team</h1>
    <p>Plain-English guides for homebuyers and homeowners, practical notes for real estate agents, and straight talk for loan officers thinking about their next move.</p>
  </div>
  {filters}
  <div class="cards">{cards}</div></main>{filter_js}"""
os.makedirs(os.path.join(dist, "blog"), exist_ok=True)
open(os.path.join(dist, "blog", "index.html"), "w").write(page(
    "Mortgage & Real Estate Blog | Duke Gallo",
    "Mortgage and real estate guides from Duke Gallo, a licensed Southern California mortgage broker: buying, refinancing, market insight, and loan officer careers.",
    f"{SITE}/blog/", blog_body,
    jsonld={"@context": "https://schema.org", "@type": "Blog", "name": "The Duke Gallo Blog", "url": f"{SITE}/blog/",
            "author": {"@id": SITE + "/#duke"}, "publisher": PERSON}))

# Standalone pages (src/pages/*.json)
extra_pages = []
for f in sorted(glob.glob(os.path.join(src, "pages", "*.json"))):
    pg = json.load(open(f))
    bodyh = pg["body_html"]
    for k, v in PH.items():
        bodyh = bodyh.replace("{{" + k + "}}", v)
    url = f"{SITE}/{pg['slug']}/"
    os.makedirs(os.path.join(dist, pg["slug"]), exist_ok=True)
    open(os.path.join(dist, pg["slug"], "index.html"), "w").write(page(
        pg["title"], pg["description"], url, header(pg["slug"]) + '\n  <main id="main"><article>' + bodyh + "</article></main>",
        noindex=pg.get("noindex", False)))
    if not pg.get("noindex"):
        extra_pages.append(url)

# Homepage
home = open(os.path.join(src, "home.html")).read()
for k, v in PH.items():
    home = home.replace("{{" + k + "}}", v)
latest = ""
if posts:
    latest = ('  <section id="blog">\n    <div class="split">\n      <div><div class="label">From the blog</div><h2>Latest writing</h2>'
              '<p style="margin-top:16px"><a href="/blog/">All posts →</a></p></div>\n      <div class="bloglist">'
              + "".join(f'<a class="bl" href="/blog/{p["slug"]}/"><span class="bl-d">{nice_date(p["date"])}</span><span class="bl-t">{esc(p["title"])}</span></a>' for p in posts[:3])
              + "</div>\n    </div>\n  </section>\n")
    home = home.replace("</style>", ".bloglist{display:grid}.bl{display:grid;grid-template-columns:150px 1fr;gap:16px;padding-block:18px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}.bl:first-child{padding-top:0}.bl-d{font:500 13px var(--mono);color:var(--muted);padding-top:4px}.bl-t{font:700 20px/1.25 var(--display)}.bl:hover .bl-t{color:var(--accent)}@media(max-width:820px){.bl{grid-template-columns:1fr;gap:4px}}\n</style>", 1)
home = home.replace("{{LATEST_POSTS}}", latest)
home_ld = {"@context": "https://schema.org", "@graph": [dict(PERSON),
    {"@type": "WebSite", "@id": SITE + "/#site", "url": SITE + "/", "name": "Duke Gallo", "publisher": {"@id": SITE + "/#duke"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in json.load(open(os.path.join(src, "home_faq.json")))]}]}
home_title = re.search(r"<title>(.*?)</title>", home).group(1)
home_desc = re.search(r'<meta name="description" content="(.*?)">', home).group(1)
head_extra = f"""<link rel="canonical" href="{SITE}/">
{ICONS}
<meta property="og:type" content="profile">
<meta property="og:site_name" content="Duke Gallo">
<meta property="og:title" content="{home_title}">
<meta property="og:description" content="{home_desc}">
<meta property="og:url" content="{SITE}/">
<meta property="og:image" content="{OG_DEFAULT}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{home_title}">
<meta name="twitter:description" content="{home_desc}">
<meta name="twitter:image" content="{OG_DEFAULT}">
<link rel="alternate" type="application/rss+xml" title="Duke Gallo Blog" href="{SITE}/blog/feed.xml">
<script type="application/ld+json">{json.dumps(home_ld)}</script>"""
home = home.replace("{{HEAD_EXTRA}}", head_extra).replace("{{YEAR}}", str(datetime.date.today().year))
open(os.path.join(dist, "index.html"), "w").write(home)
for f in glob.glob(os.path.join(src, "static", "*")):
    shutil.copy(f, dist)
open(os.path.join(dist, "duke.jpg"), "wb").write(base64.b64decode(open(os.path.join(src, "duke.jpg.b64")).read()))

# sitemap, robots, RSS
today = datetime.date.today().isoformat()
urls = [(SITE + "/", today), (SITE + "/blog/", posts[0]["date"] if posts else today)] + [(u, today) for u in extra_pages] + [(f"{SITE}/blog/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
open(os.path.join(dist, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
open(os.path.join(dist, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
def rfc822(d): return datetime.datetime.combine(datetime.date.fromisoformat(d), datetime.time(15)).strftime("%a, %d %b %Y %H:%M:%S +0000")
items = "".join(f"<item><title>{esc(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link><guid>{SITE}/blog/{p['slug']}/</guid><pubDate>{rfc822(p['date'])}</pubDate><description>{esc(p['description'])}</description></item>" for p in posts[:20])
open(os.path.join(dist, "blog", "feed.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Duke Gallo Blog</title><link>{SITE}/blog/</link><description>Mortgage and real estate insight from Duke Gallo</description>{items}</channel></rss>\n')
open(os.path.join(dist, "404.html"), "w").write(page("Page not found | Duke Gallo", "This page doesn't exist.", SITE + "/404", header("") + '<article><h1>Page not found</h1><p><a href="/">Go to the homepage</a> or <a href="/blog/">read the blog</a>.</p></article>'))
print(f"Built {len(posts)} posts into {dist}")
