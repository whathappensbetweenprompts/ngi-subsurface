# Gale, 2026-10-16: list MRV-plan document links on EPA Subpart RR facility pages (public).
import re, sys, json, requests
from urllib.parse import urljoin
slugs = sys.argv[1:]
H = {"User-Agent": "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"}
out = {}
for s in slugs:
    url = "https://www.epa.gov/ghgreporting/" + s
    try:
        r = requests.get(url, headers=H, timeout=60)
        links = re.findall(r'href="([^"]+\.pdf[^"]*)"[^>]*>(.*?)</a>', r.text, re.S|re.I)
        out[s] = {"status": r.status_code, "links": [[urljoin(url, h), re.sub(r"<[^>]+>|\s+", " ", t).strip()] for h, t in links]}
        # county / state hints
        m = re.findall(r"([A-Z][a-z]+(?: [A-Z][a-z]+)? Count(?:y|ies))", r.text)
        out[s]["counties"] = sorted(set(m))[:10]
    except Exception as e:
        out[s] = {"error": str(e)}
print(json.dumps(out, indent=1))
