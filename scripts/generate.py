#!/usr/bin/env python3
"""Generate LaTeX fragments and a static site from canonical portfolio content."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "content/profile.json").read_text())
GEN = ROOT / "build/generated"
SITE = ROOT / "site"
PRODUCTS = ROOT / "products"


def tex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
        "->": r"\ensuremath{\rightarrow}",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def write(name: str, text: str) -> None:
    (GEN / name).write_text(text.strip() + "\n")


def header() -> str:
    return (
        rf"\VitaeHeader{{{tex(DATA['name'])}}}{{{tex(DATA['professional_title'])}}}"
        rf"{{{tex(DATA['location'])} \quad {tex(DATA['github'])} \quad {tex(DATA['linkedin'])}}}"
    )


def experience(items, detailed=True, environment="Employer") -> str:
    blocks = []
    for item in items:
        progression = item.get("progression", "")
        intro = tex(item["short"])
        body = ""
        if progression:
            body += rf"\RoleProgression{{{tex(progression)}}}\par "
        body += intro
        if detailed:
            body += r"\begin{itemize}" + "".join(rf"\item {tex(a)}" for a in item["achievements"]) + r"\end{itemize}"
        blocks.append(rf"\begin{{{environment}}}{{{tex(item['organisation'])}}}{{{tex(item['role'])}}}{{{tex(item['period'])}}}{{{tex(item['location'])}}}{body}\end{{{environment}}}")
    return "\n".join(blocks)


def generate_tex() -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    write("header.tex", header())
    write("summary.tex", rf"\begin{{ExecutiveSummary}}{tex(DATA['summary'])}\end{{ExecutiveSummary}}")
    write("timeline.tex", r"\CareerTimeline{Research}{Academic Leadership}{Industrial Bioinformatics}{Commercial Genomics}{Product Leadership}{Platform Strategy}")
    write("international.tex", rf"{{\sffamily\footnotesize\color{{Slate}}{tex(DATA['international_experience'])}}}")
    write("career-transition.tex", rf"\begin{{ExecutiveSummary}}{tex(DATA['career_transition'])}\end{{ExecutiveSummary}}")

    themes = "\n".join(rf"\LeadershipArea{{{tex(n)}}}{{{tex(d)}}}" for n, d in DATA["themes"])
    write("themes.tex", themes)
    write("themes-core.tex", "\n".join(rf"\LeadershipArea{{{tex(n)}}}{{{tex(d)}}}" for n, d in DATA["themes"][:4]))

    highlights = "\n".join(rf"\begin{{CareerHighlight}}{{{tex(n)}}}{tex(d)}\end{{CareerHighlight}}" for n, d in DATA["highlights"])
    write("highlights.tex", highlights)
    write("highlights-core.tex", "\n".join(rf"\begin{{CareerHighlight}}{{{tex(n)}}}{tex(d)}\end{{CareerHighlight}}" for n, d in DATA["highlights"][:2]))

    write("experience-product.tex", experience(DATA["experience"][:1], detailed=True))
    write("experience-commercial.tex", experience(DATA["experience"][1:6], detailed=True))
    write("experience-foundations.tex", experience(DATA["experience"][6:], detailed=True))
    write("experience-cv-primary.tex", experience(DATA["experience"][:1], detailed=True))
    write("experience-cv-history.tex", experience(DATA["experience"][1:], detailed=False, environment="CvEmployer"))

    bio = "\n" + r"\par\medskip" + "\n"
    bio = bio.join(tex(p) for p in DATA["biography"])
    write("biography.tex", bio)
    education = "\n".join(rf"\EducationEntry{{{tex(x)}}}" for x in DATA["education"])
    write("education.tex", education)
    talks = "\n".join(rf"\TalkEntry{{{tex(x)}}}" for x in DATA["talks"])
    write("talks.tex", talks)
    training = "\n".join(rf"\TalkEntry{{{tex(x)}}}" for x in DATA["training"])
    write("training.tex", training)
    letter = DATA["letter"]
    write("letter.tex", "\n\n".join(tex(letter[k]) for k in ("salutation", "opening", "body", "close")) + r"\par\bigskip Sincerely,\par\medskip Stephen Rudd")


def card(title: str, body: str) -> str:
    return f'<article class="card"><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></article>'


def products() -> list[dict[str, str]]:
    """Read concise product case studies from their canonical Markdown files."""
    result = []
    for path in sorted(PRODUCTS.glob("*.md")):
        if path.name == "README.md":
            continue
        title, _, body = path.read_text().partition("\n\n")
        result.append({"slug": path.stem.lower(), "title": title.removeprefix("# "), "body": body.strip()})
    return result


def product_html(product: dict[str, str]) -> str:
    paragraphs = "".join(f"<p>{html.escape(p)}</p>" for p in product["body"].split("\n\n") if not p.startswith("##"))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(product['title'])} | Stephen Rudd</title><link rel="stylesheet" href="../style.css"></head><body><header class="product-header"><nav><a class="mark" href="../index.html">SR</a><div><a href="../index.html#products">Products</a><a href="https://github.com/sagrudd/vitae/releases/latest">PDF portfolio</a></div></nav><main><p class="kicker">Product case study</p><h1>{html.escape(product['title'])}</h1><p class="lede">{html.escape(DATA['strapline'])}</p></main></header><section class="product-copy">{paragraphs}</section><footer><strong>{html.escape(DATA['name'])}</strong><a href="../index.html">Executive portfolio</a></footer></body></html>'''


def product_card(product: dict[str, str]) -> str:
    lead = product["body"].split("\n\n", 1)[0]
    return f'<article class="card"><h3><a href="products/{product["slug"]}.html">{html.escape(product["title"])}</a></h3><p>{html.escape(lead)}</p></article>'


def generate_site() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "products").mkdir(exist_ok=True)
    theme_cards = "".join(card(*x) for x in DATA["themes"])
    roles = "".join(
        f'<article class="role"><div><span>{html.escape(x["period"])}</span><h3>{html.escape(x["organisation"])}</h3><em>{html.escape(x["role"])}</em></div><p>{html.escape(x["short"])}</p></article>'
        for x in DATA["experience"]
    )
    training_items = "".join(f"<li>{html.escape(item)}</li>" for item in DATA["training"])
    product_cards = "".join(product_card(product) for product in products())
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Executive portfolio of Stephen Rudd, computational biology and bioinformatics product leader.">
<title>{html.escape(DATA['name'])} - {html.escape(DATA['title'])}</title><link rel="stylesheet" href="style.css"></head>
<body><header><nav><a class="mark" href="#top">SR</a><div><a href="#leadership">Leadership</a><a href="#career">Career</a><a href="#training">Training</a><a href="#products">Products</a><a href="publications/index.html">Publications</a><a href="search/index.html">Search</a><a href="https://github.com/sagrudd/vitae/releases/latest">PDF portfolio</a></div></nav>
<main id="top"><p class="kicker">{html.escape(DATA['strapline'])}</p><h1>{html.escape(DATA['name'])}</h1><h2>{html.escape(DATA['title'])}</h2><p class="lede">{html.escape(DATA['summary'])}</p><p class="international">{html.escape(DATA['international_experience'])}</p></main></header>
<section id="leadership"><p class="eyebrow">Areas of leadership</p><h2>Science translated into systems</h2><div class="grid">{theme_cards}</div></section>
<section class="dark"><blockquote>“Listen closely to scientific users. Build repeatable capability. Turn analysis into a platform.”</blockquote></section>
<section id="career"><p class="eyebrow">Career narrative</p><h2>Increasing scope, one consistent purpose</h2><div class="roles">{roles}</div></section>
<section id="training"><p class="eyebrow">Training and enablement</p><h2>Capability is part of the product</h2><ul class="training">{training_items}</ul></section>
<section id="products"><p class="eyebrow">Products and platforms</p><h2>Selected product case studies</h2><div class="grid">{product_cards}</div></section>
<footer><strong>{html.escape(DATA['name'])}</strong><span>{html.escape(DATA['location'])}</span><a href="https://{html.escape(DATA['linkedin'])}">LinkedIn</a><a href="https://{html.escape(DATA['github'])}">GitHub</a></footer></body></html>'''
    (SITE / "index.html").write_text(page)
    for product in products():
        (SITE / "products" / f"{product['slug']}.html").write_text(product_html(product))
    (SITE / "style.css").write_text('''@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=Libertinus+Serif&display=swap');
:root{--blue:#12263a;--ink:#1d2730;--muted:#63717e;--paper:#f7f5f0;--line:#d7d9d5}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#fff;font-family:'IBM Plex Sans',sans-serif}header{background:var(--paper);padding:0 6vw 7rem}nav{height:6rem;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}nav a{color:var(--blue);text-decoration:none;margin-left:2rem;font-size:.82rem;letter-spacing:.05em}.mark{margin:0;border:1px solid var(--blue);padding:.5rem;font-weight:600}main{max-width:1000px;padding-top:7rem}.kicker,.eyebrow{color:#3e6178;text-transform:uppercase;letter-spacing:.18em;font-size:.72rem;font-weight:600}h1{font-family:'Libertinus Serif',serif;color:var(--blue);font-size:clamp(4rem,10vw,8rem);font-weight:400;line-height:.8;margin:.8rem 0 2rem}header h2{font-weight:300;font-size:clamp(1.5rem,3vw,2.2rem);margin:0 0 3rem}.lede{max-width:850px;font-family:'Libertinus Serif',serif;font-size:1.35rem;line-height:1.6}.international{color:var(--muted);font-size:.82rem;letter-spacing:.04em;margin-top:2rem}section{padding:7rem 6vw;max-width:1280px;margin:auto}section>h2{font-family:'Libertinus Serif',serif;color:var(--blue);font-size:2.7rem;font-weight:400}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:0;border-top:1px solid var(--line)}.card{padding:2rem 2rem 2rem 0;border-bottom:1px solid var(--line)}.card:nth-child(odd){border-right:1px solid var(--line)}.card:nth-child(even){padding-left:2rem}.card h3{font-size:.9rem;text-transform:uppercase;letter-spacing:.08em;color:var(--blue)}.card h3 a{color:inherit}.card p,.role p,.product-copy p{line-height:1.6;color:var(--muted)}.dark{max-width:none;background:var(--blue);color:white;text-align:center}.dark blockquote{font-family:'Libertinus Serif',serif;font-size:clamp(1.8rem,4vw,3.5rem);font-weight:400;max-width:1000px;margin:auto}.role{display:grid;grid-template-columns:minmax(260px,1fr) 2fr;gap:3rem;padding:2rem 0;border-top:1px solid var(--line)}.role span{color:#3e6178;font-size:.75rem;text-transform:uppercase;letter-spacing:.1em}.role h3{font-size:1.2rem;margin:.5rem 0}.role em{font-style:normal;color:var(--muted)}.training{max-width:850px;padding:0 0 0 1.2rem;color:var(--muted);line-height:1.7}.training li{margin:.75rem 0}.product-header{padding-bottom:4rem}.product-copy{max-width:820px;margin:auto;padding:5rem 6vw}.product-copy p{font-family:'Libertinus Serif',serif;font-size:1.25rem;color:var(--ink)}footer{padding:3rem 6vw;background:var(--paper);display:flex;gap:2rem;flex-wrap:wrap}footer a{color:var(--blue)}@media(max-width:700px){header{padding-bottom:4rem}nav div a:not(:last-child){display:none}main{padding-top:4rem}.grid{display:block}.card{padding:1.5rem 0!important;border-right:0!important}.role{display:block}.role p{margin-top:1rem}section{padding:4rem 6vw}}
''')
    (SITE / ".nojekyll").write_text("")


if __name__ == "__main__":
    generate_tex()
    generate_site()
