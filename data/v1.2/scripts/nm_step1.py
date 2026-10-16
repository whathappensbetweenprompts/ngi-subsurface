# Gale, 2026-10-16: NM extension step 1 - find, download and scan the EPA Subpart RR plans for New Mexico Permian sites.
import re, json, os, hashlib, datetime, csv, collections, requests, fitz
from urllib.parse import urljoin
H = {"User-Agent": "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"}
SLUGS = ["hobbs-field", "red-hills-gas-processing-plant", "maljamar-gas-plant", "dark-horse-treating-plant",
         "titan-treating-facility", "copperhead-gas-plant", "dkl-libby-gas-plant"]
API = re.compile(r"\b30[-\s]?(0\d{2})[-\s]?(\d{5})(?:[-\s]?(\d{2}))?(?:[-\s]?(\d{2}))?\b")
CAP = re.compile(r"((?:Table|Figure|Appendix|Exhibit|Attachment)\s*[A-Z]?[\d\.\-]*[^\n]{0,110})")
rows = []; summary = {}
for slug in SLUGS:
    page = "https://www.epa.gov/ghgreporting/" + slug
    t = requests.get(page, headers=H, timeout=60).text
    links = [(urljoin(page, h), re.sub(r"<[^>]+>|\s+", " ", x).strip()) for h, x in re.findall(r'href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', t, re.S | re.I)]
    plan = [u for u, x in links if x.lower().startswith("mrv plan")]
    if not plan: summary[slug] = {"error": "no plan link", "links": links}; continue
    url = plan[0]; fn = f"raw/epa_nm/{slug}__{url.rsplit('/', 1)[1]}"
    if not os.path.exists(fn):
        r = requests.get(url, headers=H, timeout=900); r.raise_for_status(); open(fn, "wb").write(r.content)
    b = open(fn, "rb").read()
    rows.append({"site_slug": slug, "epa_page": page, "plan_url": url, "local_file": fn, "bytes": len(b),
                 "sha256": hashlib.sha256(b).hexdigest(), "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    doc = fitz.open(fn); per = collections.Counter(); apis = set(); caps = {}
    with open(f"work_nm/text/{slug}.txt", "w", encoding="utf-8") as out:
        for i, p in enumerate(doc):
            x = p.get_text(); out.write(f"\n=====PAGE {i+1}=====\n{x}")
            for m in API.finditer(x): apis.add("30" + m.group(1) + m.group(2)); per[i + 1] += 1
            if per[i + 1] >= 3:
                c = [c.strip() for c in CAP.findall(x) if not re.search(r"\.{5,}", c)][:2]
                caps[i + 1] = " || ".join(c)[:160]
    summary[slug] = {"pages": len(doc), "unique_nm_api": len(apis), "pages_ge3": {k: (per[k], caps.get(k, "")) for k in sorted(caps)}}
with open("out_nm/sources_epa_mrv_plans_nm.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(summary, open("work_nm/scan.json", "w"), indent=1)
for k, v in summary.items():
    print("#####", k, v.get("pages"), "unique", v.get("unique_nm_api"), v.get("error", ""))
    last = None
    for pg, (n, cap) in (v.get("pages_ge3") or {}).items():
        if cap != last or n >= 3 and cap: print("   p", pg, n, ":", cap or "(cont.)"); last = cap
