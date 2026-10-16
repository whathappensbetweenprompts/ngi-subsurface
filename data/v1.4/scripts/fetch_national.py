# Gale, 2026-10-16: download and extract the 31 Subpart RR plans not yet in the dataset; count tokens (free count endpoint).
import json, re, os, hashlib, datetime, csv, requests, fitz
from urllib.parse import urljoin
H = {"User-Agent": "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"}
R = [r for r in json.load(open("national/epa_rr_table.json")) if r["table"] == 0]
done = set(l.strip() for l in open("national/done_slugs.txt"))
rows = []
for r in R:
    page = r["links"].split()[0]; slug = page.rsplit("/", 1)[1]
    if slug in done: continue
    try:
        t = requests.get(page, headers=H, timeout=60).text
        links = [(urljoin(page, h), re.sub(r"<[^>]+>|\s+", " ", x).strip()) for h, x in re.findall(r'href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', t, re.S | re.I)]
        plan = [u for u, x in links if x.lower().startswith("mrv plan")] or [u for u, x in links if "mrv" in x.lower() or "mrv" in u.lower()] or [u for u, x in links if "plan" in x.lower()]
        if not plan:
            rows.append({"site_slug": slug, "state": r["State"], "uic_class": r["UIC Well Class"], "decision_date": r["Date of Final Decision"], "error": "no plan link: " + "; ".join(x for _, x in links)[:300]}); continue
        url = plan[0]; fn = f"national/raw/{slug}__{url.rsplit('/', 1)[1]}"
        if not os.path.exists(fn):
            x = requests.get(url, headers=H, timeout=900); x.raise_for_status(); open(fn, "wb").write(x.content)
        b = open(fn, "rb").read(); doc = fitz.open(fn); chars = 0; empty = 0
        with open(f"national/text/{slug}.txt", "w", encoding="utf-8") as out:
            for i, p in enumerate(doc):
                s = p.get_text(); chars += len(s); empty += len(s.strip()) < 30
                out.write(f"\n=====PAGE {i+1}=====\n{s}")
        rows.append({"site_slug": slug, "state": r["State"], "uic_class": r["UIC Well Class"], "decision_date": r["Date of Final Decision"], "epa_page": page,
                     "plan_url": url, "local_file": fn, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(), "pages": len(doc), "text_chars": chars,
                     "image_only_pages": empty, "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "error": ""})
    except Exception as e:
        rows.append({"site_slug": slug, "state": r["State"], "error": str(e)[:300]})
    print(slug, rows[-1].get("pages"), rows[-1].get("text_chars"), rows[-1].get("error", ""), flush=True)
keys = sorted({k for r in rows for k in r}, key=lambda k: list(rows[0]).index(k) if k in rows[0] else 99)
with open("national/sources_national.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
# token count (free endpoint), key read from file and never printed
k = open(os.path.expanduser(r"~\.secrets\anthropic_console_key.txt"), encoding="utf-8-sig").read().strip()
tot = 0
for r in rows:
    if r.get("error"): continue
    txt = open(f"national/text/{r['site_slug']}.txt", encoding="utf-8").read()
    j = requests.post("https://api.anthropic.com/v1/messages/count_tokens", headers={"x-api-key": k, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                      json={"model": "claude-sonnet-5-5", "messages": [{"role": "user", "content": txt}]}, timeout=120).json()
    n = j.get("input_tokens"); r["tokens"] = n; tot += n or 0
    print("TOKENS", r["site_slug"], n, j.get("error", ""), flush=True)
print("TOTAL TOKENS", tot)
json.dump(rows, open("national/sources_national.json", "w"), indent=1)
