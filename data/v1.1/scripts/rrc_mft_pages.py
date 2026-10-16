# Gale, 2026-10-16: download named files from an RRC public MFT (GoAnywhere/PrimeFaces) share, paging through
# the file table via its AJAX paginator when a file is not on the first page. Public data only.
# usage: rrc_mft_pages.py <share-link> <outdir> <file1> [<file2> ...]
import sys, re, os, hashlib, datetime, json, requests
BASE = "https://mft.rrc.texas.gov/webclient/godrive/PublicGoDrive.xhtml"
def hidden(html):
    form = re.search(r'<form id="fileList".*?</form>', html, re.S)
    form = form.group(0) if form else html
    d = {m.group(1): m.group(2) for m in re.finditer(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', form)}
    vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', html) or re.search(r'javax.faces.ViewState[^>]*><!\[CDATA\[([^\]]+)\]\]>', html)
    d["javax.faces.ViewState"] = vs.group(1); d["fileList"] = "fileList"
    return d
def items(html):
    return {n.strip(): i for i, n in re.findall(r"addSubmitParam\('fileList',\{'([^']+)'[^>]*>([^<]+)</a>", html)}
def page(s, base_fields, first, rows=250):
    data = dict(base_fields)
    data.update({"javax.faces.partial.ajax": "true", "javax.faces.source": "fileTable", "javax.faces.partial.execute": "fileTable",
                 "javax.faces.partial.render": "fileTable", "fileTable": "fileTable", "fileTable_pagination": "true",
                 "fileTable_first": str(first), "fileTable_rows": str(rows), "fileTable_skipChildren": "true", "fileTable_encodeFeature": "true"})
    r = s.post(BASE, data=data, headers={"Faces-Request": "partial/ajax", "X-Requested-With": "XMLHttpRequest"}, timeout=120)
    return r.text
link, outdir, wanted = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(outdir, exist_ok=True)
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0 (research; gale@whathappensbetweenprompts.com)"
for fname in wanted:
    html = s.get(link, timeout=120).text
    fields = hidden(html); it = items(html)
    total = re.search(r"of (\d+)", " ".join(re.findall(r'ui-paginator-current[^>]*>([^<]+)<', html)) or "of 0")
    total = int(total.group(1)) if total else 0
    first = 0
    while fname not in it and first + 250 < total:
        first += 250
        x = page(s, fields, first)
        it = items(x)
        vs = re.search(r'ViewState[^>]*><!\[CDATA\[([^\]]+)\]\]>', x)
        if vs: fields["javax.faces.ViewState"] = vs.group(1)
    if fname not in it:
        print(json.dumps({"file": fname, "error": "not found", "total": total})); continue
    data = dict(fields); data[it[fname]] = it[fname]
    dest = os.path.join(outdir, fname)
    with s.post(BASE, data=data, stream=True, timeout=1800) as resp:
        resp.raise_for_status(); h = hashlib.sha256(); n = 0
        with open(dest, "wb") as fo:
            for ch in resp.iter_content(1 << 20): fo.write(ch); h.update(ch); n += len(ch)
        ct = resp.headers.get("Content-Type", "")
    meta = {"source_link": link, "file": fname, "local": dest.replace("\\", "/"), "bytes": n, "sha256": h.hexdigest(), "content_type": ct,
            "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with open(os.path.join(outdir, "_provenance.jsonl"), "a") as fo: fo.write(json.dumps(meta) + "\n")
    print(json.dumps(meta))
