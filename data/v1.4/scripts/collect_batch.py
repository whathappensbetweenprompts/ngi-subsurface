# Gale, 2026-10-16: wait for the batch, download results, write one JSON per site, tally usage. Key read from file, never printed.
import os, json, time, re, requests, datetime
K = open(os.path.expanduser(r"~\.secrets\anthropic_console_key.txt"), encoding="utf-8-sig").read().strip()
H = {"x-api-key": K, "anthropic-version": "2023-06-01"}
bid = open("national/batch_id.txt").read().strip()
log = open("national/results/poll.log", "a", encoding="utf-8")
while True:
    b = requests.get(f"https://api.anthropic.com/v1/messages/batches/{bid}", headers=H, timeout=60).json()
    log.write(f"{datetime.datetime.now():%H:%M:%S} {b.get('processing_status')} {b.get('request_counts')}\n"); log.flush()
    if b.get("processing_status") == "ended": break
    time.sleep(120)
raw = requests.get(b["results_url"], headers=H, timeout=600).text
open("national/results/results.jsonl", "w", encoding="utf-8").write(raw)
cmap = json.load(open("national/custom_id_map.json"))
use = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}; bad = []
for line in raw.splitlines():
    r = json.loads(line); slug = cmap.get(r["custom_id"], r["custom_id"])
    if r["result"]["type"] != "succeeded": bad.append((slug, r["result"]["type"], str(r["result"])[:200])); continue
    m = r["result"]["message"]; u = m["usage"]
    use["input"] += u.get("input_tokens", 0); use["output"] += u.get("output_tokens", 0)
    use["cache_read"] += u.get("cache_read_input_tokens", 0) or 0; use["cache_write"] += u.get("cache_creation_input_tokens", 0) or 0
    txt = "".join(c.get("text", "") for c in m["content"] if c["type"] == "text").strip()
    txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt)
    try:
        d = json.loads(txt); d["site_slug"] = slug
        json.dump(d, open(f"national/sites/{slug}.json", "w", encoding="utf-8"), indent=1)
    except Exception as e:
        open(f"national/results/{slug}.unparsed.txt", "w", encoding="utf-8").write(txt); bad.append((slug, "unparsed", str(e)[:150]))
    if m.get("stop_reason") != "end_turn": bad.append((slug, "stop_reason", m.get("stop_reason")))
json.dump({"batch_id_tail": bid[-10:], "usage": use, "problems": bad}, open("national/results/summary.json", "w"), indent=1)
log.write("DONE\n"); log.close()
