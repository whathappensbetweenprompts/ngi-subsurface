# Gale: OCR the ADM plan pages cited in the coding, so quotes can be checked independently of the coder's own OCR.
import json, subprocess, sys, pymupdf
d = json.load(open('sites/archer-daniels-midland-company-illinois-industrial-carbon-capture-and-sequestration.json'))
pages = sorted({p for r in d['rows'] for p in r['pages']})
doc = pymupdf.open(sys.argv[1]); out = []
for n in range(1, len(doc) + 1):
    if n in pages:
        doc[n - 1].get_pixmap(dpi=250).save('adm_ocr/_p.png')
        t = subprocess.run(['tesseract', 'adm_ocr/_p.png', '-', '--psm', '3'], capture_output=True, text=True).stdout
    else:
        t = ''
    out.append(f"\n=====PAGE {n}=====\n{t}")
open('adm_ocr/archer-daniels-midland-company-illinois-industrial-carbon-capture-and-sequestration.txt', 'w').write(''.join(out))
print('ocr pages', len(pages))
