# Gale, 2026-10-16: submit the national monitoring-commitment coding as one Message Batch. The API key is read from file and never printed.
import json, os, sys, requests
K = open(os.path.expanduser(r"~\.secrets\anthropic_console_key.txt"), encoding="utf-8-sig").read().strip()
HDR = {"x-api-key": K, "anthropic-version": "2023-06-01", "content-type": "application/json"}
MODEL = sys.argv[1] if len(sys.argv) > 1 else "claude-fable-5-1"
system = open("national/api_system_prompt.md", encoding="utf-8").read()
src = [r for r in json.load(open("national/sources_national.json")) if not r.get("error")]
reqs = []
for r in src:
    txt = open(f"national/text/{r['site_slug']}.txt", encoding="utf-8").read()
    reqs.append({"custom_id": r["site_slug"][:64], "params": {
        "model": MODEL, "max_tokens": 32000,
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": f"site_slug: {r['site_slug']}\n\nPlan text follows.\n{txt}"}]}})
ids = [q["custom_id"] for q in reqs]; assert len(ids) == len(set(ids)), "custom_id collision"
json.dump({q["custom_id"]: r["site_slug"] for q, r in zip(reqs, src)}, open("national/custom_id_map.json", "w"), indent=1)
resp = requests.post("https://api.anthropic.com/v1/messages/batches", headers=HDR, json={"requests": reqs}, timeout=300)
j = resp.json()
print("HTTP", resp.status_code, "| model", MODEL, "| requests", len(reqs))
print({k: j.get(k) for k in ("id", "processing_status", "request_counts", "expires_at")} if resp.status_code == 200 else j.get("error"))
if resp.status_code == 200: open("national/batch_id.txt", "w").write(j["id"])
