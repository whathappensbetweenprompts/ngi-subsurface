# Gale, 2026-10-16: keyword screen of monitoring methods mentioned in each plan (presence + page count). Not a reading of commitments.
import re, json, csv
SCOPE = json.load(open("work/scope.json"))
K = {
 "injection_rate_pressure_scada": r"\bSCADA\b|injection (?:rate|pressure)|bottom[- ]?hole pressure|wellhead pressure",
 "mechanical_integrity_testing": r"mechanical integrity|\bMIT\b|annul(?:ar|us) pressure",
 "surface_leak_detection_h2s_co2_sensors": r"H2S (?:detector|sensor|monitor)|gas detector|CO2 (?:detector|sensor)|leak detection",
 "soil_gas": r"soil[- ]gas",
 "groundwater_usdw_sampling": r"\bUSDW\b|groundwater (?:monitor|sampl)|shallow aquifer|water well sampl",
 "atmospheric_eddy_covariance": r"eddy covariance|atmospheric monitor|open[- ]path",
 "pulsed_neutron_saturation_logging": r"pulsed neutron|\bPNL\b|\bRST\b|reservoir saturation",
 "fiber_optic_das_dts": r"fiber[- ]optic|\bDTS\b|\bDAS\b",
 "seismic_monitoring_or_surveys": r"microseismic|seismic monitor|seismometer|time[- ]lapse seismic|4D seismic|VSP|vertical seismic profil",
 "insar_surface_deformation": r"InSAR|surface deformation|tiltmeter",
 "pressure_front_or_monitoring_wells": r"monitoring well|observation well|pressure front|in[- ]zone monitor|above[- ]zone monitor",
 "tracers": r"tracer",
 "mass_balance_equations": r"mass balance|Equation RR-",
}
rows = []
for s in SCOPE:
    t = open(f"work/text/{s['site_slug']}.txt", encoding="utf-8").read()
    pages = re.split(r"\n=====PAGE \d+=====\n", t)[1:]
    row = {"site_slug": s["site_slug"], "uic_class": s["uic_class"]}
    for k, pat in K.items():
        row[k] = sum(1 for p in pages if re.search(pat, p, re.I))
    rows.append(row)
with open("out/monitoring_keyword_screen.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
