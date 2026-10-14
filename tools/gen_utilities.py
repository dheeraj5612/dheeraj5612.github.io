#!/usr/bin/env python3
"""Generate <siteDir>/utilities/index.html. Usage: gen_utilities.py <siteDir>"""
import json, os, re, sys
from html import escape

CATS = ["Markets and investing", "Money, work and immigration", "Home and property",
        "Hobbies, gear and travel", "AI and tech tools", "Small business and trades"]
DESC = ("50 small web tools built and run by Dheeraj Namburu: calculators, planners, and lookup tools. "
        "33 live on their own domains, 17 deployed as previews.")
MODIFIED = "2026-10-13"
SIZES = "(max-width: 719px) 110px, (max-width: 1079px) 28vw, 260px"
OG_IMG = "https://dheerajnamburu.com/assets/share/og-home-v1.png"
OG_ALT = "Dheeraj Namburu, Software Engineer at Microsoft"
HOW = [
    ("Small and static.", "46 are static builds, 2 are Next.js apps, and 2 are Node API apps. 48 of the 50 have no npm dependencies. All of them run on Cloudflare."),
    ("One shared data service.", "One shared Cloudflare Worker serves public data from sources like FRED, SEC EDGAR, FINRA, and NYC Open Data to the sites that need it, with caching, timeouts, and a last good fallback."),
    ("Repeatable releases.", "Live sites are released from pinned commits, with a receipt recorded for each one. A launch controller checks preview builds before they go out, and previews stay out of search engines."),
    ("Analytics only with consent.", "Every site asks before measuring anything, and sends no analytics request until the visitor agrees."),
]


def die(msg):
    sys.exit("gen_utilities: " + msg)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def rewrite(frag):
    """Rewrite href/src URLs for a page one directory below the homepage."""
    skip_done = [False]

    def attr(m):
        name, q, val = m.group(1), m.group(2), m.group(3)
        if re.match(r"(https?:|mailto:|tel:|data:|/)", val):
            return m.group(0)
        if val.startswith("#"):
            if val == "#main":
                new = "../"
                if name == "href" and not skip_done[0] and 'class="skip"' in m.string[max(0, m.start() - 40):m.start()]:
                    new = "#main"
            else:
                new = "../" + val
            if val == "#main" and new == "#main":
                skip_done[0] = True
        else:
            new = "../" + val
        new = new.replace("../utilities/", "./")
        return f"{name}={q}{new}{q}"

    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', attr, frag)


def extract(home):
    m = re.search(r"<body\b[^>]*>.*?</header>", home, re.S)
    if not m:
        die("homepage: <body>...</header> not found")
    prefix = m.group(0)
    m = re.search(r"<footer\b.*</body>", home, re.S)
    if not m:
        die("homepage: <footer>...</body> not found")
    suffix = m.group(0)
    contact = None
    for sm in re.finditer(r"<section\b([^>]*)>", home):
        cm = re.search(r'class\s*=\s*"([^"]*)"', sm.group(1))
        if cm and "contact" in cm.group(1).split():
            end = home.find("</section>", sm.start())
            if end < 0:
                die("homepage: contact section not closed")
            contact = home[sm.start():end + len("</section>")]
            break
    if not contact:
        die("homepage: contact section not found")
    return prefix, suffix, contact


def head_copy(home):
    h = re.search(r"<head\b.*?</head>", home, re.S)
    if not h:
        die("homepage: <head> not found")
    h = h.group(0)
    out = []
    for t in re.findall(r"<(?:link|meta)\b[^>]*>", h):
        if re.match(r'<link\b[^>]*rel="(icon|apple-touch-icon|preload)"', t) or \
           re.match(r'<meta\b[^>]*name="theme-color"', t) or \
           (re.match(r'<link\b[^>]*rel="stylesheet"', t) and re.search(r'href="styles\.css', t)):
            out.append(rewrite(t))
    return out


def ensure_period(s):
    s = s.strip()
    return s if s[-1] in ".!?" else s + "."


def main():
    if len(sys.argv) != 2:
        die("usage: gen_utilities.py <siteDir>")
    site = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(here, "utilities.json"), encoding="utf-8"))
    live = [d for d in data if d["status"] == "live"]
    prev = [d for d in data if d["status"] == "preview"]
    if (len(data), len(live), len(prev)) != (50, 33, 17):
        die(f"expected 50/33/17 entries, got {len(data)}/{len(live)}/{len(prev)}")
    if len(DESC) > 155:
        die(f"DESC is {len(DESC)} characters, limit is 155")
    for d in data:
        if d["category"] not in CATS:
            die(f"unknown category {d['category']!r} ({d['slug']})")
    for d in live:
        for ext in (".webp", "-320.webp"):
            p = os.path.join(site, "assets", "utilities", d["slug"] + ext)
            if not os.path.isfile(p):
                die("missing thumbnail " + p)
    home = open(os.path.join(site, "index.html"), encoding="utf-8").read()
    prefix, suffix, contact = extract(home)
    prefix, suffix, contact = rewrite(prefix), rewrite(suffix), rewrite(contact)
    brand_old, brand_new = 'aria-label="Dheeraj Namburu, back to top"', 'aria-label="Dheeraj Namburu, home"'
    if prefix.count(brand_old) != 1:
        die("header brand link label not found")
    prefix = prefix.replace(brand_old, brand_new)
    suffix = re.sub(r'<a\b([^>]*\bhref="\./"[^>]*)>', lambda m: m.group(0) if "aria-current" in m.group(1) else f'<a{m.group(1)} aria-current="page">', suffix)

    key = lambda d: d["name"].lower()
    order = []  # live in page order
    sections = []
    for c in CATS:
        cl = sorted([d for d in live if d["category"] == c], key=key)
        cp = sorted([d for d in prev if d["category"] == c], key=key)
        order += cl
        s = slugify(c)
        count = f"{len(cl)} live" + (f" · {len(cp)} preview{'s' if len(cp) != 1 else ''}" if cp else "")
        o = [f'<section class="u-category" id="{s}" aria-labelledby="{s}-title">',
             f'<div class="section-head"><h2 id="{s}-title">{escape(c)}</h2><p class="u-count">{count}</p></div>',
             '<div class="u-grid">']
        for d in cl:
            u, n = escape(d["url"], True), escape(d["name"])
            o.append('<article class="u-card">'
                     f'<a class="u-thumb" href="{u}" tabindex="-1" aria-hidden="true" data-track-group="utility" data-kind="live"><img src="../assets/utilities/{d["slug"]}.webp" srcset="../assets/utilities/{d["slug"]}-320.webp 320w, ../assets/utilities/{d["slug"]}.webp 640w" sizes="{SIZES}" width="640" height="400" loading="lazy" decoding="async" alt=""></a>'
                     f'<h3><a href="{u}" data-track-group="utility" data-kind="live">{n} <span aria-hidden="true">↗</span></a></h3>'
                     f'<p>{escape(ensure_period(d["what"]))}</p>'
                     f'<p class="u-domain">{escape(d["domain"])}</p></article>')
        o.append("</div>")
        if cp:
            o.append('<h3 class="u-previews-title">Previews</h3><ul class="u-previews">')
            for d in cp:
                o.append(f'<li><a href="{escape(d["url"], True)}" rel="nofollow" data-track-group="utility" data-kind="preview">{escape(d["name"])} <span aria-hidden="true">↗</span></a>'
                         f'<span class="u-what">{escape(ensure_period(d["what"]))}</span><span class="u-badge">Preview</span></li>')
            o.append("</ul>")
        o.append("</section>")
        sections.append("\n".join(o))

    B = "https://dheerajnamburu.com/"
    items = [{"@type": "ListItem", "position": i, "name": d["name"], "url": d["url"]} for i, d in enumerate(order, 1)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": B + "#website", "name": "Dheeraj Namburu", "url": B},
        {"@type": "Person", "@id": B + "#person", "name": "Dheeraj Namburu", "url": B},
        {"@type": "CollectionPage", "@id": B + "utilities/#webpage", "url": B + "utilities/", "name": "Utility portfolio",
         "description": DESC, "dateModified": MODIFIED,
         "isPartOf": {"@id": B + "#website"}, "author": {"@id": B + "#person"}, "creator": {"@id": B + "#person"},
         "breadcrumb": {"@id": B + "utilities/#breadcrumb"}, "mainEntity": {"@id": B + "utilities/#itemlist"}},
        {"@type": "BreadcrumbList", "@id": B + "utilities/#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": B},
            {"@type": "ListItem", "position": 2, "name": "Utility portfolio", "item": B + "utilities/"}]},
        {"@type": "ItemList", "@id": B + "utilities/#itemlist", "name": "Live utility sites",
         "numberOfItems": len(order), "itemListElement": items}]}
    title = "Utility Portfolio | Dheeraj Namburu"
    head = ['<!doctype html>', '<html lang="en">', '<head>',
            '<meta charset="utf-8">', '<meta name="viewport" content="width=device-width,initial-scale=1">',
            '<title>Utility Portfolio: 50 Small Web Tools | Dheeraj Namburu</title>',
            f'<meta name="description" content="{DESC}">',
            '<meta name="robots" content="max-image-preview:large">',
            '<link rel="canonical" href="https://dheerajnamburu.com/utilities/">',
            '<meta property="og:type" content="website">',
            '<meta property="og:url" content="https://dheerajnamburu.com/utilities/">',
            '<meta property="og:site_name" content="Dheeraj Namburu">',
            '<meta property="og:locale" content="en_US">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{DESC}">',
            f'<meta property="og:image" content="{OG_IMG}">',
            '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
            '<meta property="og:image:type" content="image/png">',
            f'<meta property="og:image:alt" content="{OG_ALT}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{title}">',
            f'<meta name="twitter:description" content="{DESC}">',
            f'<meta name="twitter:image" content="{OG_IMG}">',
            f'<meta name="twitter:image:alt" content="{OG_ALT}">']
    css = False
    for t in head_copy(home):
        head.append(t)
        if 'rel="stylesheet"' in t and not css:
            head.append('<link rel="stylesheet" href="utilities.css?v=20261013-ux2">')
            css = True
    if not css:
        die("homepage: styles.css link not found")
    head.append('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + '</script>')
    head.append('</head>')

    cats_n = len(CATS)
    stats = [(50, "sites built and running"), (len(live), "live on their own domains"),
             (len(prev), "deployed as previews"), (cats_n, "categories")]
    main = ['<main id="main">',
            '<section class="u-hero" aria-labelledby="u-title">',
            '<div class="u-hero-copy">',
            '<p class="u-back"><a href="../"><span aria-hidden="true">←</span> Back to home</a></p>',
            '<p class="eyebrow">UTILITY PORTFOLIO</p>',
            '<h1 id="u-title">50 small web tools I built and run.</h1>',
            '<p class="u-lede">Calculators, planners, and lookup tools. Each one answers a single practical question, like what a 3D print job should cost or how much tile a room needs. 33 are live on their own domains and 17 are deployed as previews.</p>',
            '<div class="actions"><a class="button" href="../Dheeraj-Namburu-Resume.pdf">View résumé <span aria-hidden="true">↗</span></a><a class="button secondary" href="mailto:dheerajnamburu@gmail.com">Email me <span aria-hidden="true">↗</span></a></div>',
            '</div>',
            '<ul class="u-stats">' + "".join(f"<li><strong>{n}</strong> <span>{l}</span></li>" for n, l in stats) + "</ul>",
            '</section>',
            '<section class="u-how" aria-labelledby="u-how-title">',
            '<p class="eyebrow">HOW THEY ARE BUILT</p>',
            '<h2 id="u-how-title">Small sites on shared tooling.</h2>',
            '<div class="u-how-grid">' + "".join(f"<article><h3>{t}</h3><p>{b}</p></article>" for t, b in HOW) + '</div>',
            '</section>',
            '<nav class="u-jump" aria-label="Categories">' + "".join(
                f'<a href="#{slugify(c)}">{escape(c)} <span>{sum(1 for d in data if d["category"] == c)}</span></a>' for c in CATS) + '</nav>']
    main += sections
    main.append('<p class="u-note">Live sites run on their own domains. Previews are deployed and working but not launched yet, so search engines are asked not to index them.</p>')
    main.append(contact)
    main.append('</main>')

    page = "\n".join(head) + "\n" + prefix + "\n" + "\n".join(main) + "\n" + suffix
    if not page.endswith("\n"):
        page += "\n"
    os.makedirs(os.path.join(site, "utilities"), exist_ok=True)
    with open(os.path.join(site, "utilities", "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(page)
    counts = {c: sum(1 for d in data if d["category"] == c) for c in CATS}
    print(f"ok: {len(data)} total, {len(live)} live, {len(prev)} preview; " + "; ".join(f"{c}={n}" for c, n in counts.items()))


main()
