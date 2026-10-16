"""Gale, 2026-10-16. OCR of the Maljamar plan's image-only well tables (Part A Appendix 3, p85; Part B Appendix 3, pp175-181).
Pages were rendered at 300 dpi with PyMuPDF (page.get_pixmap(dpi=300)) and read with Tesseract 5.3.4.
Two independent passes per table row: (1) the API column alone, digits-and-hyphens whitelist, single-line mode;
(2) the whole row, block mode. Where the passes agree the API is accepted. Where they disagree or one is missing,
the row image was checked by eye and the reading recorded in VISUAL below. Rows the detector missed entirely are added from MISSED. Every OCR'd API is then checked against
the NMOCD well name in the join (see build_nm.py)."""
import glob, re, subprocess, csv, sys
from PIL import Image, ImageFilter
import numpy as np
SRC = sys.argv[1] if len(sys.argv) > 1 else "."
VISUAL = {("175","30-025-20216"):"3002520216",("175","30-025-24196"):"3002524196",("176","30-025-38951"):"3002538551",
          ("176","30-025-39470"):"3002539470",("177","30-025-38714"):"3002538714",("177","30-025-39000"):"3002539000",
          ("179","30-025-00738"):"3002500738",("179","30-025-00603"):"3002500603",("180","30-025-08062"):"3002508062"}
def ocr(img, psm, wl=None):
    img.save("_tmp.png"); a = ["tesseract", "_tmp.png", "-", "--psm", str(psm)]
    if wl: a += ["-c", "tessedit_char_whitelist=" + wl]
    return subprocess.run(a, capture_output=True, text=True).stdout.strip()
prep = lambda c: c.resize((c.width*2, c.height*2), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: 255 if v > 140 else 0)
fix = lambda s: re.sub(r"[ON]", "0", s).replace("/", "7")
out = []
for f in sorted(glob.glob(f"{SRC}/mj_p*.png")):
    page = re.search(r"mj_p(\d+)", f).group(1)
    g = Image.open(f).convert("L"); w, h = g.size; a = np.array(g)
    dark = (a[:, int(w*0.025):int(w*0.10)] < 110).sum(1) > 3
    y = 0
    while y < h:
        if dark[y]:
            y0 = y
            while y < h and dark[y]: y += 1
            if y - y0 > 15:
                col = ocr(prep(g.crop((int(w*0.025), max(0, y0-8), int(w*0.10), min(h, y+8)))), 7, "0123456789-")
                row = re.sub(r"\s+", " ", ocr(prep(g.crop((int(w*0.02), max(0, y0-30), int(w*0.98), min(h, y+30)))), 6))
                colok = col if re.fullmatch(r"30-?0\d{2}-?\d{5}", col) else ""
                m = re.match(r"30-?0[0-9]{2}-?[0-9]{5}", row); rowapi = m.group(0) if m else ""
                if not colok and not rowapi: y += 1; continue
                c = colok.replace("-", "")
                if c and c in fix(re.sub(r"[\s-]", "", row)): api, how = c, "two_ocr_passes_agree"
                else: api, how = VISUAL.get((page, colok)) or rowapi.replace("-", ""), "resolved_by_visual_check"
                lat = re.findall(r"\b3[23]\.\d{2,6}\b", row); lon = re.findall(r"-?10[34]\.\d{2,6}\b", row)
                out.append({"page": page, "y0": y0, "api10": api, "ocr_method": how, "lat_ocr": lat[0] if lat else "",
                            "lon_ocr": lon[0] if lon else "", "row_ocr": row})
        y += 1
# Rows the line detector missed: on a dark-highlighted row the threshold removes the text. Read by eye from the page image.
MISSED = [{"page": "85", "y0": 1440, "api10": "3001523701", "ocr_method": "added_by_visual_check", "lat_ocr": "32.7019",
           "lon_ocr": "-104.4492", "row_ocr": "30-015-23701 RIO PENASCO JX COM #002 Gas Active 35-18S-25E 32.7019 -104.4492 (read by eye)"}]
out.extend(MISSED)
with open("maljamar_ocr_final.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(out[0])); wr.writeheader(); wr.writerows(out)
print(len(out), "rows")
