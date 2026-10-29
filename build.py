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

src, dist = sys.argv[1], sys.argv[2]
shutil.rmtree(dist, ignore_errors=True)
os.makedirs(dist)

posts = []
for f in glob.glob(os.path.join(src, "posts", "*.json")):
    p = json.load(open(f))
    for k in ["slug", "title", "description", "date", "category", "image", "image_alt", "body_html"]:
        assert p.get(k), f"{f}: missing {k}"
    assert re.fullmatch(r"[a-z0-9-]+", p["slug"]), f"bad slug {p['slug']}"
    posts.append(p)
posts.sort(key=lambda p: p["date"], reverse=True)
slugs = [p["slug"] for p in posts]
assert len(slugs) == len(set(slugs)), "duplicate slug"

def esc(s): return html.escape(s, quote=True)
def nice_date(d): return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")
def read_min(body): return max(2, round(len(re.sub(r"<[^>]+>", " ", body).split()) / 225))

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Figtree:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">'

CSS = """
:root{--bg:#f7f8f9;--surface:#fff;--ink:#14202b;--muted:#5b6872;--line:#dfe3e7;--accent:#1d5b78;--accent-soft:#e6eff3;
--display:"Bricolage Grotesque","Helvetica Neue",Arial,sans-serif;--body:"Figtree","Helvetica Neue",Arial,sans-serif;--mono:"JetBrains Mono",ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#0f1519;--surface:#151d22;--ink:#e8edf0;--muted:#94a1aa;--line:#26323a;--accent:#7fbcd6;--accent-soft:#1a2c35;color-scheme:dark}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.7 var(--body);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
img{max-width:100%;height:auto}a{color:var(--accent)}
a:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.wrap{max-width:1040px;margin:0 auto}
h1,h2,h3{font-family:var(--display);font-weight:700;line-height:1.12;letter-spacing:-.015em;text-wrap:balance}
.label{font:500 12px/1.2 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
header.top{display:flex;justify-content:space-between;align-items:center;gap:16px;padding-block:24px;flex-wrap:wrap}
.mark{font:700 18px/1 var(--display);color:var(--ink);text-decoration:none}
nav{display:flex;gap:24px;flex-wrap:wrap}nav a{color:var(--muted);text-decoration:none;font-weight:500;font-size:15px}
nav a:hover,nav a[aria-current]{color:var(--ink)}
.blog-head{padding-block:48px 32px;border-bottom:1px solid var(--line)}
.blog-head h1{font-size:clamp(40px,7vw,72px);margin:12px 0 0}
.blog-head p{max-width:56ch;color:var(--muted);font-size:19px;margin:16px 0 0}
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
@media (max-width:820px){.cards{grid-template-columns:1fr 1fr}}
@media (max-width:520px){.cards{grid-template-columns:1fr}nav{gap:16px}}
"""

FOOTER = f"""<footer>
    <p>Duke Gallo, NMLS #{NMLS} · West Capital Lending, Inc. · Equal Housing Opportunity. Verify licensing at <a href="https://www.nmlsconsumeraccess.org/" target="_blank" rel="noopener">nmlsconsumeraccess.org</a>.</p>
    <p>Blog content is for general education only and is not a commitment to lend, a rate quote, or financial, legal, or tax advice. All loans are subject to credit approval and underwriting. Not all applicants will qualify. Programs and guidelines change; contact me for current details.</p>
    <p>© {datetime.date.today().year} Duke Gallo</p>
  </footer>"""

def header(active):
    return f"""<header class="top">
    <a class="mark" href="/">DG</a>
    <nav aria-label="Primary">
      <a href="/#about">About</a><a href="/#career">Career</a><a href="/blog/"{' aria-current="page"' if active=='blog' else ''}>Blog</a><a href="/#contact">Contact</a>
    </nav>
  </header>"""

def page(title, desc, canonical, body, og_type="website", image=None, jsonld=None, extra_head=""):
    img = image or f"{SITE}/duke.jpg"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="author" content="{AUTHOR}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{esc(img)}">
<meta property="og:site_name" content="Duke Gallo">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Duke Gallo Blog" href="{SITE}/blog/feed.xml">
{extra_head}{FONTS}
<style>{CSS}</style>
{ld}
</head>
<body>
<div class="wrap">
  {body}
  {FOOTER}
</div>
</body>
</html>
"""

def card(p, h="h2"):
    return f"""<a class="card" href="/blog/{p['slug']}/">
        <img src="{esc(p['image'])}" alt="{esc(p['image_alt'])}" loading="lazy" width="640" height="400">
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
  <article>
    <div class="meta"><a href="/blog/">Blog</a><span>{esc(p['category'])}</span><span>{read_min(p['body_html'])} min read</span></div>
    <h1>{esc(p['title'])}</h1>
    <p class="dek">{esc(p['description'])}</p>
    <div class="byline"><img src="/duke.jpg" alt="Duke Gallo" width="44" height="44"><div><b>Duke Gallo</b><span>Vice President, West Capital Lending · <time datetime="{p['date']}">{nice_date(p['date'])}</time></span></div></div>
    <figure class="hero-img" style="margin-inline:0"><img src="{esc(p['image'])}" alt="{esc(p['image_alt'])}" width="1440" height="810">{credit}</figure>
    <div class="body">
{p['body_html']}
    </div>
    <aside class="cta">
      <h2>Have a question about your situation?</h2>
      <p>Call or text me at <b>(949) 688-5959</b> or email <b>dgallo@westcapitallending.com</b>. Loan officers interested in joining my team are welcome to reach out too.</p>
    </aside>
  </article>
  {more}"""
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BlogPosting", "headline": p["title"], "description": p["description"],
             "image": p["image"], "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
             "mainEntityOfPage": url, "keywords": ", ".join(p.get("keywords", [])),
             "author": {"@type": "Person", "name": AUTHOR, "url": SITE, "jobTitle": "Vice President, Mortgage Loan Originator"},
             "publisher": {"@type": "Person", "name": AUTHOR, "url": SITE}},
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
blog_body = f"""{header('blog')}
  <div class="blog-head">
    <div class="label">The Duke Gallo Blog</div>
    <h1>Mortgages, real estate, and building a team</h1>
    <p>Plain-English guides for homebuyers and homeowners, practical notes for real estate agents, and straight talk for loan officers thinking about their next move.</p>
  </div>
  <div class="cards">{cards}</div>"""
os.makedirs(os.path.join(dist, "blog"), exist_ok=True)
open(os.path.join(dist, "blog", "index.html"), "w").write(page(
    "Mortgage & Real Estate Blog | Duke Gallo",
    "Mortgage and real estate guides from Duke Gallo, Vice President at West Capital Lending: buying, refinancing, market insight, and loan officer careers.",
    f"{SITE}/blog/", blog_body,
    jsonld={"@context": "https://schema.org", "@type": "Blog", "name": "The Duke Gallo Blog", "url": f"{SITE}/blog/",
            "author": {"@type": "Person", "name": AUTHOR}}))

# Homepage
home = open(os.path.join(src, "home.html")).read()
latest = ""
if posts:
    latest = ('  <section id="blog">\n    <div class="split">\n      <div><div class="label">From the blog</div><h2>Latest writing</h2>'
              '<p style="margin-top:16px"><a href="/blog/">All posts →</a></p></div>\n      <div class="bloglist">'
              + "".join(f'<a class="bl" href="/blog/{p["slug"]}/"><span class="bl-d">{nice_date(p["date"])}</span><span class="bl-t">{esc(p["title"])}</span></a>' for p in posts[:3])
              + "</div>\n    </div>\n  </section>\n")
    home = home.replace("</style>", ".bloglist{display:grid}.bl{display:grid;grid-template-columns:150px 1fr;gap:16px;padding-block:18px;border-bottom:1px solid var(--line);text-decoration:none;color:var(--ink)}.bl:first-child{padding-top:0}.bl-d{font:500 13px var(--mono);color:var(--muted);padding-top:4px}.bl-t{font:700 20px/1.25 var(--display)}.bl:hover .bl-t{color:var(--accent)}@media(max-width:820px){.bl{grid-template-columns:1fr;gap:4px}}\n</style>", 1)
home = home.replace("{{LATEST_POSTS}}", latest)
home = home.replace("<meta name=\"description\"", f'<link rel="canonical" href="{SITE}/">\n<meta property="og:title" content="Duke Gallo">\n<meta property="og:image" content="{SITE}/duke.jpg">\n<meta name="description"', 1)
open(os.path.join(dist, "index.html"), "w").write(home)
open(os.path.join(dist, "duke.jpg"), "wb").write(base64.b64decode(open(os.path.join(src, "duke.jpg.b64")).read()))

# sitemap, robots, RSS
today = datetime.date.today().isoformat()
urls = [(SITE + "/", today), (SITE + "/blog/", posts[0]["date"] if posts else today)] + [(f"{SITE}/blog/{p['slug']}/", p.get("updated", p["date"])) for p in posts]
open(os.path.join(dist, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
open(os.path.join(dist, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
def rfc822(d): return datetime.datetime.combine(datetime.date.fromisoformat(d), datetime.time(15)).strftime("%a, %d %b %Y %H:%M:%S +0000")
items = "".join(f"<item><title>{esc(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link><guid>{SITE}/blog/{p['slug']}/</guid><pubDate>{rfc822(p['date'])}</pubDate><description>{esc(p['description'])}</description></item>" for p in posts[:20])
open(os.path.join(dist, "blog", "feed.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Duke Gallo Blog</title><link>{SITE}/blog/</link><description>Mortgage and real estate insight from Duke Gallo</description>{items}</channel></rss>\n')
open(os.path.join(dist, "404.html"), "w").write(page("Page not found | Duke Gallo", "This page doesn't exist.", SITE + "/404", header("") + '<article><h1>Page not found</h1><p><a href="/">Go to the homepage</a> or <a href="/blog/">read the blog</a>.</p></article>'))
print(f"Built {len(posts)} posts into {dist}")
