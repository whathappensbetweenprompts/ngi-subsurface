# Gale, 2026-10-16: extract every Texas API-number mention from the in-scope MRV plan texts, with page and context.
import re, csv, collections, json
SCOPE = json.load(open("work/scope.json"))
API = re.compile(r"\b42[-\s]?(\d{3})[-\s]?([0-9A-Z]\d{4})(?:[-\s]?(\d{2}))?(?:[-\s]?(\d{2}))?\b")
mentions = []
for site in SCOPE:
    slug = site["site_slug"]
    txt = open(f"work/text/{slug}.txt", encoding="utf-8").read()
    pages = re.split(r"\n=====PAGE (\d+)=====\n", txt)[1:]
    for i in range(0, len(pages), 2):
        pg = int(pages[i]); body = pages[i + 1]; lines = body.split("\n")
        n_on_page = len(API.findall(body))
        for li, line in enumerate(lines):
            for m in API.finditer(line):
                ctx = " | ".join(l.strip() for l in lines[li:li + 4] if l.strip())
                mentions.append({"site_slug": slug, "page": pg, "api_as_printed": m.group(0),
                                 "api10": "42" + m.group(1) + m.group(2), "county_code": m.group(1),
                                 "api_mentions_on_page": n_on_page, "table_page": int(n_on_page >= 10),
                                 "context": ctx[:240]})
with open("work/plan_api_mentions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(mentions[0].keys())); w.writeheader(); w.writerows(mentions)
c = collections.Counter((m["site_slug"]) for m in mentions)
u = collections.defaultdict(set)
for m in mentions: u[m["site_slug"]].add(m["api10"])
for s in SCOPE: print(s["site_slug"], "mentions", c[s["site_slug"]], "unique", len(u[s["site_slug"]]))
