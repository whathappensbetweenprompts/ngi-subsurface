# Gale, 2026-10-16: download a file from an RRC public MFT (GoAnywhere) share by submitting its JSF form.
import sys, re, hashlib, datetime, requests, json
link, wanted, dest = sys.argv[1], sys.argv[2], sys.argv[3]
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"
r = s.get(link, timeout=120); t = r.text
form = re.search(r'<form id="fileList".*?</form>', t, re.S).group(0)
data = {m.group(1): m.group(2) for m in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', form)}
if "javax.faces.ViewState" not in data:
    vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', t); data["javax.faces.ViewState"] = vs.group(1)
ids = re.findall(r"addSubmitParam\('fileList',\{'([^']+)'[^>]*>([^<]+)</a>", form)
target = [i for i, n in ids if n.strip() == wanted]
if not target: print("not found; files:", [n for i, n in ids][:50]); sys.exit(1)
data["fileList"] = "fileList"; data[target[0]] = target[0]
with s.post("https://mft.rrc.texas.gov/webclient/godrive/PublicGoDrive.xhtml", data=data, stream=True, timeout=1800) as resp:
    resp.raise_for_status(); h = hashlib.sha256(); n = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(1 << 20):
            f.write(chunk); h.update(chunk); n += len(chunk)
meta = {"source_link": link, "file": wanted, "local": dest, "bytes": n, "sha256": h.hexdigest(),
        "content_type": resp.headers.get("Content-Type"), "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
open(dest + ".provenance.json", "w").write(json.dumps(meta, indent=1)); print(json.dumps(meta))
