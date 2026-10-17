"""Build site_status.csv for dataset v1.5.

Joins EPA's public Subpart RR stored-CO2 table (epa_rr_sequestofco2fac.json, from
https://data.epa.gov/efservice/rr_sequestofco2fac/JSON) to the 53 sites by GHGRP facility id,
then applies the public-source status research in research/: the batch_*.json files, then
state_records.json (state well and injection records, which take precedence), then manual.json.
Run from the v1.5 folder: python scripts/build_status.py
"""
import json, glob, csv, collections, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(HERE, *a)

sites = list(csv.DictReader(open(P('facility_ids.csv'), encoding='utf-8')))
epa = collections.defaultdict(dict)
for r in json.load(open(P('epa_rr_sequestofco2fac.json'))):
    epa[str(r['facility_id'])][r['reporting_year']] = float(r['rr1112_total_co2_sequestered'] or 0)
research = {}
for f in sorted(glob.glob(P('research', 'batch_*.json'))) + [P('research', 'state_records.json'), P('research', 'manual.json')]:
    for x in json.load(open(f)):
        research[x['slug']] = x

# operating_status groups the detailed status for the map
OP = {'injecting': 'storing', 'eor_flood_ongoing': 'storing', 'reported_to_epa': 'storing',
      'built_not_injecting': 'built', 'built_injection_unconfirmed': 'built', 'eor_recycle_only': 'built', 'not_built': 'not_built', 'unclear': 'unclear'}

rows = []
for s in sites:
    e = {y: round(v, 1) for y, v in sorted(epa.get(s['ghgrp_facility_id'], {}).items())}
    x = research.get(s['site_slug'])
    if x:
        st = dict(status=x['status'], basis=x.get('basis', 'public_sources'), start=x.get('injection_start', ''), summary=x['summary'],
                  date=x['evidence_date'], conf=x['confidence'], src=[z['url'] for z in x['sources']])
    elif e and max(e.values()) > 0:
        last = max(e)
        st = dict(status='reported_to_epa', basis='epa_reported', start=str(min(y for y, v in e.items() if v > 0)),
                  summary=f"Reported {e[last]:,.0f} metric tons of CO2 stored in {last} under Subpart RR. EPA's public data ends with reporting year 2023.",
                  date=f'reporting year {last}', conf='high', src=['https://data.epa.gov/efservice/rr_sequestofco2fac/JSON'])
    else:
        raise SystemExit(f"no status for {s['site_slug']}")
    rows.append(dict(site_slug=s['site_slug'], facility_name=s['facility_name'], state=s['state'], site_group=s['site_group'],
                     ghgrp_facility_id=s['ghgrp_facility_id'], operating_status=OP[st['status']], status_detail=st['status'],
                     status_basis=st['basis'], injection_start=st['start'],
                     epa_stored_metric_tons_by_year=';'.join(f'{y}:{v}' for y, v in e.items()),
                     latest_epa_year=max(e) if e else '', summary=st['summary'], evidence_date=st['date'],
                     confidence=st['conf'], sources=' | '.join(st['src'])))

with open(P('site_status.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), 'sites')
print(collections.Counter(r['operating_status'] for r in rows))
print(sorted(collections.Counter((r['site_group'], r['operating_status']) for r in rows).items()))
