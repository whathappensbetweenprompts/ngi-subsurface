# Gale, 2026-10-16. Build the New Mexico well inventory (v1.2): plan well lists joined to NMOCD well records.
import re, json, csv, collections, datetime, difflib, requests, time
ROLES = json.load(open("work_nm/table_roles_nm.json")); ROLES.pop("_note")
PRI = {"unit_well_list": 1, "mma_well_list": 1, "aor_well_list": 1, "radius_well_list": 1, "project_wells": 2, "reference_in_text_figure_or_other_table": 9}
API = re.compile(r"(?<![\d-])30\s?-?\s?(0[0-4]\d)\s?-?\s?(\d{5})(?:\s?-?\s?(\d{2}))?(?:\s?-?\s?(\d{2}))?(?!\d)")
SRC = {r["site_slug"]: r for r in csv.DictReader(open("out_nm/sources_epa_mrv_plans_nm.csv", encoding="utf-8"))}
def pages(slug):
    t = open(f"work_nm/text/{slug}.txt", encoding="utf-8").read()
    return {int(p.split("=====")[0]): p.split("=====\n", 1)[1] for p in t.split("=====PAGE ")[1:]}
def role_of(slug, pg, src):
    for a, b, role, s, title in ROLES.get(slug, []):
        if a <= pg <= b and s == src: return role, title
    return None, None
ent = collections.defaultdict(lambda: {"roles": set(), "titles": set(), "entries": 0, "rows": [], "pages": set(), "mentions": 0,
                                       "suffix": set(), "src": set(), "ocr_methods": set(), "ocr_latlon": []})
for slug in SRC:
    P = pages(slug)
    for pg, body in P.items():
        ms = list(API.finditer(body)); flat = re.sub(r"\s+", " ", body)
        for i, m in enumerate(ms):
            api = "30" + m.group(1) + m.group(2); e = ent[(slug, api)]
            e["mentions"] += 1; e["pages"].add(pg)
            for s in (m.group(3), m.group(4)):
                if s and s != "00": e["suffix"].add(s)
            nxt = ms[i + 1].start() if i + 1 < len(ms) else min(len(body), m.end() + 200)
            if slug == "hobbs-field":  # Hobbs rows read: well name | API | type | status, one cell per line
                before = [x for x in body[:m.start()].split("\n") if x.strip()]; after = [x for x in body[m.end():].split("\n") if x.strip()]
                start, end = None, None; ctx0 = " | ".join([before[-1].strip(), m.group(0)] + [x.strip() for x in after[:2]])
            else:  # all other lists start each row with the API
                start, end = m.start(), nxt
            ctx = ctx0 if start is None else re.sub(r"\s+", " ", body[start:end]).strip()
            role, title = role_of(slug, pg, "text")
            if role:
                e["roles"].add(role); e["titles"].add(f"p{pg}: {title}"); e["entries"] += 1; e["rows"].append(ctx[:300]); e["src"].add("text")
            elif not e["rows"]:
                e["ref_ctx"] = ctx[:300]
for r in csv.DictReader(open("publish/_ocr_tmp/maljamar_ocr_final.csv", encoding="utf-8")):
    slug = "maljamar-gas-plant"; pg = int(r["page"]); e = ent[(slug, r["api10"])]
    role, title = role_of(slug, pg, "ocr")
    e["roles"].add(role); e["titles"].add(f"p{pg}: {title}"); e["entries"] += 1; e["rows"].append("[OCR] " + r["row_ocr"][:300])
    e["pages"].add(pg); e["mentions"] += 1; e["src"].add("ocr"); e["ocr_methods"].add(r["ocr_method"])
    if r["lat_ocr"] and r["lon_ocr"]: e["ocr_latlon"].append((r["lat_ocr"], r["lon_ocr"]))
# ---- NMOCD lookup: EMNRD/OCD well layers as published on the NM Environment Department's public GIS server
B = "https://mercator.env.nm.gov/server/rest/services/emnrd/ocd_wells/MapServer"
LAYERS = {0: "Oil Wells", 1: "Gas Wells", 2: "CO2 Wells", 3: "Injection Wells", 4: "Water Wells"}
apis = sorted({a for (_, a) in ent})
fmt = lambda a: f"{a[:2]}-{a[2:5]}-{a[5:]}"
rec = collections.defaultdict(list)
for L, lname in LAYERS.items():
    for i in range(0, len(apis), 150):
        chunk = apis[i:i + 150]
        q = {"where": "API IN (" + ",".join(f"'{fmt(a)}'" for a in chunk) + ")", "outFields": "*", "returnGeometry": "false", "f": "json"}
        for k in range(4):
            try: j = requests.post(f"{B}/{L}/query", data=q, timeout=120).json(); break
            except Exception: time.sleep(5)
        for f in j.get("features", []):
            a = f["attributes"]; a["_layer"] = lname; rec[a["API"].replace("-", "")].append(a)
recent = {}
for c in ("30-025-53", "30-025-54", "30-015-55", "30-015-56"):  # currency check: counts of recently assigned API ranges
    recent[c + "xxx"] = requests.get(f"{B}/0/query", params={"where": f"API like '{c}%'", "returnCountOnly": "true", "f": "json"}, timeout=60).json().get("count")
meta = requests.get(B, params={"f": "json"}, timeout=60).json()
prov = {"service": B, "layers": LAYERS, "service_description": meta.get("serviceDescription"),
        "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currency_check_oil_layer_counts": recent, "apis_queried": len(apis), "apis_found": len(rec),
        "note": "EMNRD Oil Conservation Division well locations and attributes, as served by the New Mexico Environment Department's public ArcGIS server. Queried by API with IN-lists of 150, all five layers. The NM State Land Office's NMOCD_Wells_V3 service was tried first and rejected: it holds no Lea County API above 30-025-50999, so it is missing wells permitted in recent years."}
json.dump(prov, open("out_nm/nmocd_source.json", "w"), indent=1)
def d(v):
    """Dates arrive as epoch ms (NMSLO copy) or 'YYYYMMDDhhmmss' strings (EMNRD copy). 1900-01-01 and 9999-12-31 are placeholders for 'none'."""
    if v in (None, "", 0): return ""
    if isinstance(v, str):
        s = v.strip()[:8]
        return "" if (not s.isdigit() or s.startswith("1900") or s.startswith("9999")) else s
    if v <= -2208988800000 + 86400000: return ""
    out = (datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=v)).strftime("%Y%m%d")
    return "" if out.startswith("9999") else out
# secondary: the NM State Land Office's older copy, used only for spud date, plug date and true vertical depth, which the EMNRD copy leaves blank
S = "https://mapservice.nmstatelands.org/arcgis/rest/services/Public/NMOCD_Wells_V3/MapServer/5"
sec = {}
for i in range(0, len(apis), 150):
    chunk = apis[i:i + 150]
    q = {"where": "API IN (" + ",".join(f"'{fmt(a)}'" for a in chunk) + ")", "outFields": "API,spud_date,plug_date,true_verti", "returnGeometry": "false", "f": "json"}
    for k in range(4):
        try: j = requests.post(S + "/query", data=q, timeout=120).json(); break
        except Exception: time.sleep(5)
    for f in j.get("features", []): sec[f["attributes"]["API"].replace("-", "")] = f["attributes"]
prov["secondary_service"] = S
prov["secondary_note"] = "NM State Land Office NMOCD_Wells_V3 (an older copy of the same OCD data; no Lea County API above 30-025-50999). Used only for nmslo_spud_date, nmslo_plug_date and nmslo_tvd_ft."
prov["secondary_apis_found"] = len(sec)
json.dump(prov, open("out_nm/nmocd_source.json", "w"), indent=1)
norm = lambda s: re.sub(r"[^A-Z0-9 ]", " ", (s or "").upper())
def name_check(nm, rows):
    if not nm or not rows: return ""
    words = [w for w in norm(nm).split() if not w.isdigit() and len(w) > 1]
    nums = [w.lstrip("0") or "0" for w in norm(nm).split() if re.fullmatch(r"\d+[A-Z]?", w)]
    t = " " + norm(" ".join(rows)).replace(" 0", " ") + " "
    tt = re.sub(r"\b0+(\d)", r"\1", norm(" ".join(rows)))
    w_ok = sum(1 for w in words if w in t) / len(words) if words else 1
    n_ok = all(re.search(rf"\b0*{re.escape(n)}\b", tt) for n in nums[-1:]) if nums else True
    return "match" if w_ok >= 0.5 and n_ok else ("partial" if w_ok >= 0.5 or n_ok else "no")
import math
def dist_m(a, b, c, e):
    R = 6371000; p1, p2 = math.radians(a), math.radians(c)
    return 2 * R * math.asin(math.sqrt(math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(e - b) / 2) ** 2))
out = []
for (slug, api), e in sorted(ent.items()):
    roles = e["roles"] - {None}
    role = min(roles, key=lambda r: PRI[r]) if roles else "reference_in_text_figure_or_other_table"
    R = rec.get(api, [])
    a = R[0] if R else {}
    row = {"site_slug": slug, "api10": api, "plan_role": role, "plan_roles_all": ";".join(sorted(roles)),
           "plan_table_title": " | ".join(sorted(e["titles"])), "plan_entries": e["entries"],
           "plan_row_raw": " || ".join(e["rows"]) if e["rows"] else e.get("ref_ctx", ""),
           "plan_sidetrack_suffixes": ";".join(sorted(e["suffix"])), "plan_pages": ";".join(map(str, sorted(e["pages"]))),
           "plan_mentions": e["mentions"], "plan_extraction": ";".join(sorted(e["src"])) or "text",
           "ocr_method": ";".join(sorted(e["ocr_methods"])), "plan_url": SRC[slug]["plan_url"],
           "nmocd_match": "matched" if R else "no_match", "nmocd_records": len(R)}
    for k_out, k in [("nmocd_well_name", "wellname"), ("nmocd_type", "type"), ("nmocd_status", "status"), ("nmocd_operator", "ogrid_name"),
                     ("nmocd_ogrid", "ogrid"), ("nmocd_ulstr", "ulstr"), ("nmocd_direction", "dir_status"),
                     ("nmocd_pools", "pool_id_list"), ("nmocd_md_ft", "meas_depth"), ("nmocd_total_depth_ft", "tot_depth"), ("nmocd_details_url", "URL"), ("nmocd_layer", "_layer")]:
        v = a.get(k, ""); row[k_out] = v.strip() if isinstance(v, str) else ("" if v in (None, 0) else v)
    row["nmocd_spud_date"] = d(a.get("spud_date")); row["nmocd_plug_date"] = d(a.get("plug_date")); row["nmocd_approval_date"] = d(a.get("apr_date")); row["nmocd_type_code"] = a.get("well_type", "")
    z = sec.get(api, {}); row["nmslo_spud_date"] = d(z.get("spud_date")); row["nmslo_plug_date"] = d(z.get("plug_date")); row["nmslo_tvd_ft"] = z.get("true_verti") or ""
    row["lat_nad83"] = a.get("latitude", ""); row["lon_nad83"] = a.get("longitude", "")
    row["name_check"] = ("" if role == "reference_in_text_figure_or_other_table" else ("hobbs_unit_name" if "HOBBS" in str(row["nmocd_well_name"]) else "not_hobbs_unit_name") if slug == "hobbs-field" else name_check(row["nmocd_well_name"], e["rows"]))
    if e["ocr_latlon"] and R:
        try:
            la, lo = e["ocr_latlon"][0]; lo = float(lo); lo = -abs(lo)
            row["ocr_location_check_m"] = round(dist_m(float(la), lo, a["latitude"], a["longitude"]))
        except Exception: row["ocr_location_check_m"] = ""
    else: row["ocr_location_check_m"] = ""
    out.append(row)
with open("out_nm/site_wells_nm.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
L = [r for r in out if r["plan_role"] != "reference_in_text_figure_or_other_table"]
print("rows", len(out), "listed", len(L), "unique listed", len({r["api10"] for r in L}), "matched", sum(r["nmocd_match"] == "matched" for r in L), "multi-record", sum(r["nmocd_records"] > 1 for r in out))
for s in SRC:
    l = [r for r in L if r["site_slug"] == s]
    print(f"{s:34s} listed {len(l):4d} matched {sum(r['nmocd_match']=='matched' for r in l):4d} names {dict(collections.Counter(r['name_check'] for r in l))} roles {dict(collections.Counter(r['plan_role'] for r in l))}")
print("status", collections.Counter(r["nmocd_status"] for r in L).most_common(12))
print("ocr loc check", sorted(r["ocr_location_check_m"] for r in L if r["ocr_location_check_m"] != "")[-8:])
print("unmatched", [(r["site_slug"][:6], r["api10"], r["plan_row_raw"][:60]) for r in L if r["nmocd_match"] != "matched"][:30])
print("name no (non-Hobbs)", [(r["site_slug"][:6], r["api10"], r["nmocd_well_name"], r["plan_row_raw"][:90]) for r in L if r["name_check"] == "no" and r["site_slug"] != "hobbs-field"])
print("hobbs names with HOBBS", collections.Counter("HOBBS" in str(r["nmocd_well_name"]) for r in L if r["site_slug"] == "hobbs-field"), [ (r["api10"], r["nmocd_well_name"]) for r in L if r["site_slug"] == "hobbs-field" and "HOBBS" not in str(r["nmocd_well_name"])][:20])
print("layers", collections.Counter(r["nmocd_layer"] for r in L), "status", collections.Counter(r["nmocd_status"] for r in L))
print(json.dumps(prov)[:600])
