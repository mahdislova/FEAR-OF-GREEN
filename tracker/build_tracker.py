"""Build the season tracker HTML from canon. Run from the repo root:  python3 tracker/build_tracker.py
The tracker is a view of canon; it holds no facts of its own."""
import html, re, glob, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def read(p): return open(os.path.join(ROOT, p), encoding="utf-8").read()

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    return s

def md(text):
    """Small markdown renderer: paragraphs, bullet lists, tables."""
    out, lines, i = [], text.strip().split("\n"), 0
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"-+", c) for c in cells): rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            out.append('<div class="wide"><table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>")
            continue
        if l.lstrip().startswith("- "):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                items.append(lines[i].lstrip()[2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>"); continue
        if l.startswith("#"): i += 1; continue
        para = [l]; i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("|", "- ", "#")):
            para.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)

def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""

season = read("canon/season-one.md")
world = read("canon/world-and-rules.md")
project = read("PROJECT.md")

# promise lines
promise = section(season, "The promise")

# episodes
eps = []
for p in sorted(glob.glob(os.path.join(ROOT, "episodes", "episode-*.md"))):
    t = open(p, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", t, re.M).group(1)
    head = t.split("## Scenes")[0]
    cold = re.search(r"\*\*Cold open:\*\*\s*(.+)", head)
    change = re.search(r"\*\*Change:\*\*\s*(.+?)\n", head)
    fg = re.search(r"\*\*Foreground:\*\*\s*(.+)", head)
    bg = re.search(r"\*\*Background:\*\*\s*(.+)", head)
    beats = [(l[2:] if l.startswith("- ") else "↳ " + l.strip()[2:]) for l in head.split("\n") if l.startswith("- ") or l.startswith("  - ")]
    scenes = t.split("## Scenes", 1)[1].strip() if "## Scenes" in t else ""
    has_scenes = bool(re.search(r"^### ", scenes, re.M))
    eps.append(dict(title=title, cold=cold.group(1).strip() if cold else "", change=change.group(1).strip().rstrip(".") if change else "",
                    fg=fg.group(1).strip() if fg else "", bg=bg.group(1).strip() if bg else "", beats=beats, has_scenes=has_scenes))

# cast
cast = []
for p in sorted(glob.glob(os.path.join(ROOT, "characters", "*.md"))):
    t = open(p, encoding="utf-8").read()
    name = re.search(r"^# (.+)$", t, re.M).group(1)
    first = next((l for l in t.split("\n")[1:] if l.startswith("**")), "")
    cast.append((name, first))

CSS = """
:root{--bg:#0b1513;--panel:#12201d;--panel2:#172925;--ink:#e8f0ec;--muted:#a3b6ae;--glow:#7fe0b0;--line:#2a3d38;color-scheme:dark}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:64px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,"Segoe UI",sans-serif}
a{color:var(--glow)}code{font-size:.9em;color:var(--glow)}
header{padding:56px max(16px,6vw) 36px;background:radial-gradient(ellipse at 85% 0%,#1f4a3b 0,transparent 55%),linear-gradient(150deg,#13231f,#0b1513)}
.eyebrow{font-size:12px;letter-spacing:3px;color:var(--glow);font-weight:700;text-transform:uppercase}
h1,h2,h3{font-family:Georgia,"Times New Roman",serif;font-weight:400;line-height:1.15;text-wrap:balance}
h1{font-size:clamp(36px,6vw,64px);margin:14px 0}h2{font-size:clamp(26px,4vw,34px);margin:0 0 14px}h3{font-size:21px;margin:0 0 6px}
.promise p{max-width:820px;font-size:18px;color:#d3e2dc}
.pill{display:inline-block;border:1px solid #47605a;border-radius:20px;padding:3px 11px;font-size:12px;margin:6px 6px 0 0}
nav{position:sticky;top:0;z-index:5;background:#0b1513ee;border-bottom:1px solid var(--line);display:flex;gap:20px;padding:13px max(16px,6vw);overflow-x:auto}
nav a{font-size:13px;white-space:nowrap;text-decoration:none;color:var(--ink)}nav a:hover{color:var(--glow)}
main{max-width:1280px;margin:auto;padding:30px max(16px,5vw) 70px}section{margin:0 0 60px}
.lead{color:var(--muted);max-width:860px}
.eps{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.ep{background:var(--panel);border:1px solid var(--line);border-radius:9px;padding:18px 20px;min-width:0}
.ep .num{font-family:Georgia,serif;color:var(--glow);font-size:13px;letter-spacing:2px;text-transform:uppercase}
.meta{font-size:13.5px;color:var(--muted);margin:4px 0}.meta b{color:var(--ink);font-weight:600}
.ep ul{padding-left:18px;margin:10px 0 0}.ep li{margin:0 0 7px;font-size:14.5px}
.tag{font-size:11px;padding:2px 8px;border-radius:4px;background:#163a2e;color:#9ed9c0;margin-left:6px;vertical-align:2px}
.wide{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{padding:10px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
th{color:var(--muted);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:1px;background:var(--panel2)}
#grid table{min-width:1500px}#grid td:first-child,#grid th:first-child{position:sticky;left:0;background:var(--panel2);font-weight:600;min-width:150px}
#grid td{min-width:130px}
.cast{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.cast div{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 14px;font-size:13.5px;min-width:0}
.cast b{display:block;font-family:Georgia,serif;font-size:16px;font-weight:400;margin-bottom:3px}
.prose p,.prose li{max-width:880px}
footer{color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:18px}
@media(max-width:860px){.eps{grid-template-columns:1fr}.cast{grid-template-columns:1fr 1fr}}
@media(max-width:520px){.cast{grid-template-columns:1fr}}
"""

ep_html = "".join(f"""<article class="ep" id="ep{n}"><div class="num">Episode {n}</div><h3>{inline(e['title'].split(' — ',1)[-1])}{'<span class="tag">scenes in progress</span>' if e['has_scenes'] else ''}</h3>
<p class="meta"><b>Change:</b> {inline(e['change'])}</p><p class="meta"><b>Foreground:</b> {inline(e['fg'])}</p><p class="meta"><b>Background:</b> {inline(e['bg'])}</p><p class="meta"><b>Cold open:</b> {inline(e['cold'])}</p>
<ul>{''.join(f'<li>{inline(b)}</li>' for b in e['beats'])}</ul></article>""" for n, e in enumerate(eps, 1))
cast_html = "".join(f"<div><b>{inline(n)}</b>{inline(f)}</div>" for n, f in cast)
today = datetime.date.today().isoformat()

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Green Gallows Season Tracker</title><style>{CSS}</style></head><body>
<header><div class="eyebrow">The Green Gallows · Season one</div><h1>Season Tracker</h1>
<div class="promise">{md(promise)}</div>
<span class="pill">Generated from canon · {today}</span><span class="pill">Spine provisional</span><span class="pill">Only writer-finalized work is canon</span></header>
<nav><a href="#secret">The secret</a><a href="#episodes">Episodes</a><a href="#grid">Thread grid</a><a href="#threads">Threads</a><a href="#changes">Five changes</a><a href="#coldopens">Cold opens</a><a href="#cast">Cast</a><a href="#ending">Ending</a><a href="#open">Open questions</a></nav>
<main>
<section id="secret" class="prose"><div class="eyebrow">The secret</div><h2>The light is a living thing in a freezer.</h2>{md(section(world, "The engine"))}</section>
<section id="episodes"><div class="eyebrow">Ten episodes</div><h2>Episode by episode</h2><p class="lead">The current beats for each episode, straight from the episode files.</p><div class="eps">{ep_html}</div></section>
<section id="grid"><div class="eyebrow">Thread grid</div><h2>Every thread, every episode</h2><p class="lead">Scroll sideways. A dash means the thread rests that week.</p>{md(section(season, "Thread grid"))}</section>
<section id="threads" class="prose"><div class="eyebrow">The threads</div><h2>How each line runs</h2>{md(section(season, "The threads"))}</section>
<section id="changes"><div class="eyebrow">Structure</div><h2>The five changes</h2>{md(section(season, "The five changes"))}</section>
<section id="coldopens"><div class="eyebrow">History</div><h2>Told in cold opens</h2>{md(section(season, "Cold opens"))}</section>
<section id="cast"><div class="eyebrow">Cast</div><h2>Who's who</h2><div class="cast">{cast_html}</div></section>
<section id="ending" class="prose"><div class="eyebrow">The ending</div><h2>Lights out</h2>{md(section(season, "The ending"))}</section>
<section id="open" class="prose"><div class="eyebrow">Still open</div><h2>Open questions</h2>{md(section(project, "Open questions"))}</section>
<footer>Built by <code>tracker/build_tracker.py</code> from <code>canon/</code>, <code>episodes/</code>, <code>characters/</code> and <code>PROJECT.md</code>. Change the canon files, then rebuild. Never edit this page by hand.</footer>
</main></body></html>"""
out = os.path.join(ROOT, "tracker", "green-gallows-season-tracker.html")
open(out, "w", encoding="utf-8").write(page)
print("wrote", out, len(eps), "episodes", len(cast), "characters")
