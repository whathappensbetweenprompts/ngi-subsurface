# Gale, 2026-10-16: scan MRV plan PDFs: per-page text, API-number candidates, county names, penetration keywords.
import fitz, re, os, json, glob, collections
API = re.compile(r"\b42[-\s]?(\d{3})[-\s]?(\d{5})(?:[-\s]?(\d{2}))?(?:[-\s]?(\d{2}))?\b")
CNTY = re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+Count(?:y|ies)\b")
KW = re.compile(r"penetration|plugged and abandoned|wellbore inventory|area of review|legacy well", re.I)
os.makedirs("work/text", exist_ok=True)
summary = {}
for pdf in sorted(glob.glob("raw/epa/*.pdf")):
    slug = os.path.basename(pdf).split("__")[0]
    try:
        doc = fitz.open(pdf)
    except Exception as e:
        summary[slug] = {"error": str(e)}; continue
    pages_api = collections.Counter(); apis = set(); counties = collections.Counter(); kwpages = []
    textless = 0
    with open(f"work/text/{slug}.txt", "w", encoding="utf-8") as out:
        for i, p in enumerate(doc):
            t = p.get_text()
            if len(t.strip()) < 20: textless += 1
            out.write(f"\n=====PAGE {i+1}=====\n{t}")
            for m in API.finditer(t):
                apis.add("42" + m.group(1) + m.group(2)); pages_api[i+1] += 1
            for c in CNTY.findall(t): counties[c] += 1
            if KW.search(t): kwpages.append(i+1)
    summary[slug] = {"pages": len(doc), "textless_pages": textless, "unique_api10": len(apis),
                     "pages_with_api": len(pages_api), "top_api_pages": pages_api.most_common(5),
                     "counties": counties.most_common(6), "keyword_pages": kwpages[:25]}
json.dump(summary, open("work/scan_summary.json", "w"), indent=1)
for k, v in summary.items(): print(k, json.dumps(v))
