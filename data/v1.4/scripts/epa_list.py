# Gale, 2026-10-16: national list of Subpart RR facilities from EPA's Subpart RR page.
import requests, re, json, csv, collections, html
from urllib.parse import urljoin
U = "https://www.epa.gov/ghgreporting/subpart-rr-geologic-sequestration-carbon-dioxide"
H = {"User-Agent": "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"}
t = requests.get(U, headers=H, timeout=60).text
clean = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
rows = []
for ti, tb in enumerate(re.findall(r"<table.*?</table>", t, re.S)):
    # caption / preceding heading
    pre = t[:t.find(tb)]; hd = re.findall(r"<h[2-4][^>]*>(.*?)</h[2-4]>", pre, re.S); heading = clean(hd[-1]) if hd else ""
    heads = [clean(h) for h in re.findall(r"<th[^>]*>(.*?)</th>", tb, re.S)]
    for tr in re.findall(r"<tr.*?</tr>", tb, re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if not tds: continue
        links = [urljoin(U, h) for h in re.findall(r'href="([^"]+)"', tr)]
        rows.append({"table": ti, "heading": heading, **{(heads[i] if i < len(heads) else f"c{i}"): clean(td) for i, td in enumerate(tds)}, "links": " ".join(links)})
json.dump(rows, open("national/epa_rr_table.json", "w"), indent=1)
for ti in sorted({r["table"] for r in rows}):
    rr = [r for r in rows if r["table"] == ti]
    print("TABLE", ti, "|", rr[0]["heading"], "| rows", len(rr), "| cols", [k for k in rr[0] if k not in ("table", "heading", "links")])
    print("   states", collections.Counter(r.get("State", "") for r in rr).most_common())
    print("   example", {k: v for k, v in rr[0].items() if k != "heading"})
