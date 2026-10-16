# Gale, 2026-10-16 (v1.0.1 after independent check): site-well table from plan API mentions, classified by the plan
# table they appear in, joined to the RRC OG_WELLBORE_EWA public bulk file. Public sources only.
import csv, json, re
import pandas as pd
SCOPE = {s["site_slug"]: s for s in json.load(open("work/scope.json"))}
SRC = {r["site_slug"]: r for r in csv.DictReader(open("out/sources_epa_mrv_plans.csv", encoding="utf-8"))}
ROLES = json.load(open("work/table_roles.json"))
REF = "reference_in_text_figure_or_other_table"
PRI = {"legacy_penetrations_aor_mma": 1, "mma_well_list": 1, "unit_well_list": 2, "project_wells": 3, REF: 9}
def role_of(slug, page):
    for s, a, b, role, title in ROLES:
        if s == slug and a <= page <= b: return role, title
    return REF, ""
APIRX = re.compile(r"42[-\s]?\d{3}[-\s]?[0-9A-Z]\d{4}")
TYPE = re.compile(r"^(PROD_OIL|PROD_GAS|INJ_H2O|INJ_WAG|INJ_WTR|INJ_CO2|INJ_SWD|INJ_GAS|DISP_H2O|WSW|SWS|SWD|OBS|WATER SUPPLY|PRODUCERS?|INJECTORS?)$", re.I)
STAT = re.compile(r"^(ACTIVE|INACTIVE|SHUT[_ -]?IN|TA|TEMP_AB|P ?& ?A|P&A|DRY HOLE|SPUD DATE ONLY|PERMITTED|CANCELLED|(?:Plugged|Active|Inactive|Shut[- ]?In)\s*[\u2010-]\s*.+)$", re.I)
def parse_row(ctx):
    ctx = re.sub(r"(P ?& ?A|INACTIVE|ACTIVE|SHUT_IN|TEMP_AB)(?=(?:PROD|INJ|SHUT|ACTIVE|INACTIVE|TEMP))", r"\1 | ", ctx)  # cells glued by PDF text extraction
    # keep only this row: cut the context at the next API number after the first
    first = APIRX.search(ctx)
    rest = ctx[first.end():] if first else ctx
    nxt = APIRX.search(rest)
    row = (ctx[:first.end()] if first else "") + (rest[:nxt.start()] if nxt else rest)
    toks = [t.strip() for t in re.split(r"\s*\|\s*|\s+(?=(?:PROD|INJ|DISP|WSW|SWS|P&A|P & A|ACTIVE|INACTIVE|SHUT|TA\b|TEMP))", rest[:nxt.start()] if nxt else rest) if t.strip()]
    ty = next((t for t in toks if TYPE.match(t)), "")
    st = next((t for t in toks if STAT.match(t) and t != ty), "")
    if not ty and st.upper().replace(" ", "") == "P&A":   # rows like "API P&A INACTIVE": P&A is the type column
        ty = st; st = next((t for t in toks if STAT.match(t) and t != ty), "")
    return row.strip(" |"), ty, st
ment = list(csv.DictReader(open("work/plan_api_mentions.csv", encoding="utf-8")))
sw = {}
for m in ment:
    slug, pg = m["site_slug"], int(m["page"])
    role, title = role_of(slug, pg)
    k = (slug, m["api10"])
    r = sw.setdefault(k, {"pages": set(), "mentions": 0, "role": REF, "title": "", "rows": [], "types": [], "stats": [],
                          "first": m["context"], "printed": set()})
    r["pages"].add(pg); r["mentions"] += 1; r["printed"].add(re.sub(r"\D", "", m["api_as_printed"]))
    if PRI[role] < PRI[r["role"]]:
        r["role"], r["title"], r["rows"], r["types"], r["stats"] = role, title, [], [], []
    if role == r["role"] and role != REF:
        row, ty, st = parse_row(m["context"].replace("\u0003", ""))
        r["rows"].append(row)
        if ty and ty not in r["types"]: r["types"].append(ty)
        if st and st not in r["stats"]: r["stats"].append(st)
cols = {0:"district",2:"api8",3:"county_name",4:"oil_gas_code",5:"lease_name",7:"field_name",11:"operator_name",
        15:"api_depth_ft",18:"well_type_name",20:"plug_date",27:"ewa_id",28:"w2g1_filed",30:"completion_date",31:"w3_file_date"}
need = set(k[1][2:] for k in sw)
chunks = []
for ch in pd.read_csv("raw/rrc/OG_WELLBORE_EWA_Report.csv", header=None, dtype=str, usecols=list(cols), chunksize=500000,
                      encoding="latin-1", on_bad_lines="skip"):
    ch = ch.rename(columns=cols); ch = ch[ch["api8"].isin(need)]
    if len(ch): chunks.append(ch)
rrc = pd.concat(chunks).fillna("")
for c in rrc.columns: rrc[c] = rrc[c].str.strip()
rrc["ewa_n"] = pd.to_numeric(rrc["ewa_id"], errors="coerce").fillna(0)
R = {}
for api8, g in rrc.groupby("api8"):
    g = g.sort_values(["completion_date", "w2g1_filed", "ewa_n"])     # most recent last
    def latest(f):
        v = [x for x in g[f] if x]
        return v[-1] if v else ""
    depths = [int(x) for x in g["api_depth_ft"] if x.isdigit() and int(x) > 0]
    ops = list(dict.fromkeys(x for x in g["operator_name"] if x))
    R[api8] = {"rrc_rows": len(g), "rrc_county": latest("county_name"), "rrc_district": latest("district"),
        "rrc_field_name": latest("field_name"), "rrc_lease_name": latest("lease_name"), "rrc_operator_name": latest("operator_name"),
        "rrc_other_operators": "; ".join(o for o in ops if o != latest("operator_name")),
        "rrc_well_type": latest("well_type_name"), "rrc_oil_gas_code": "/".join(sorted(set(g["oil_gas_code"]) - {""})),
        "rrc_depth_ft": max(depths) if depths else "", "rrc_plug_date": max(g["plug_date"]),
        "rrc_w3_file_date": max(g["w3_file_date"]), "rrc_latest_completion_date": max(g["completion_date"])}
RRCF = ["rrc_rows","rrc_county","rrc_district","rrc_field_name","rrc_lease_name","rrc_operator_name","rrc_other_operators",
        "rrc_well_type","rrc_oil_gas_code","rrc_depth_ft","rrc_plug_date","rrc_w3_file_date","rrc_latest_completion_date"]
NOTES = {("wellman", "4216533912"): "Source plan lists this Gaines API as WU 303-ST; RRC and the Seminole East Field plan identify it as an ESSAU (Seminole East) well."}
rows = []
for (slug, api10), r in sorted(sw.items()):
    j = R.get(api10[2:])
    if api10[5:] == "00000": match = "placeholder_api"
    elif j: match = "matched"
    elif not api10[2:].isdigit(): match = "no_match_nonnumeric_api"
    else: match = "no_match_in_EWA"
    side = sorted(p[10:12] for p in r["printed"] if len(p) >= 12 and p[10:12] not in ("", "00"))
    o = {"site_slug": slug, "site_name": SCOPE[slug]["site_name"], "api10": api10, "plan_role": r["role"],
         "plan_table_title": r["title"], "plan_entries": len(r["rows"]) if r["rows"] else 0,
         "plan_type_raw": "; ".join(r["types"]), "plan_status_raw": "; ".join(r["stats"]),
         "plan_row_raw": " || ".join(dict.fromkeys(r["rows"])) if r["rows"] else r["first"],
         "plan_sidetrack_suffixes": ";".join(dict.fromkeys(side)),
         "plan_pages": ";".join(map(str, sorted(r["pages"]))), "plan_mentions": r["mentions"], "plan_url": SRC[slug]["plan_url"],
         "rrc_match": match, "note": NOTES.get((slug, api10), "")}
    for f in RRCF: o[f] = (j or {}).get(f, "") if match == "matched" else ""
    rows.append(o)
with open("out/site_wells.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
s = pd.DataFrame(rows)
print(s.groupby("rrc_match").size().to_string())
for slug, api in [("seminole-east-field-sef","4216500168"),("wellman","4244500089"),("wellman","4244500579"),("denver-unit","4250134924"),("south-plains-complex","4221900675"),("denver-unit","4216500561"),("bull-moose-gas-plant","4249504327")]:
    x = s[(s.site_slug==slug)&(s.api10==api)].iloc[0]
    print(slug, api, "|", x.plan_type_raw, "|", x.plan_status_raw, "|", x.plan_sidetrack_suffixes, "|", x.rrc_operator_name, "|", x.rrc_other_operators)

