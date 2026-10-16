# Gale, 2026-10-16: download current MRV plan PDFs from EPA, record provenance (url, sha256, bytes, utc time).
import json, hashlib, os, datetime, requests, csv
L = json.loads(open("work/epa_links.json","rb").read().decode("utf-16"))
H = {"User-Agent": "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"}
rows = []
for slug, v in L.items():
    plans = [u for u, t in v.get("links", []) if t.lower().startswith("mrv plan")]
    if not plans:
        print("NO PLAN", slug); continue
    url = plans[0]
    fn = os.path.join("raw", "epa", slug + "__" + url.rsplit("/", 1)[1])
    if not os.path.exists(fn):
        r = requests.get(url, headers=H, timeout=600); r.raise_for_status()
        open(fn, "wb").write(r.content)
    b = open(fn, "rb").read()
    rows.append({"site_slug": slug, "epa_page": "https://www.epa.gov/ghgreporting/" + slug, "plan_url": url,
                 "local_file": fn.replace("\\", "/"), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                 "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    print(slug, len(b))
with open("out/sources_epa_mrv_plans.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
