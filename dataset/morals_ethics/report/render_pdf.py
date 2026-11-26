"""Render report.html to the PDF (Chromium via Playwright)."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

here = Path(__file__).resolve().parent
out = here / "ConsciousMind_Morals_Ethics_Research_Progress_Report.pdf"
exe = sys.argv[1] if len(sys.argv) > 1 else None
foot = ('<div style="font-family:DejaVu Sans,Arial;font-size:7px;color:#777;width:100%;padding:0 16mm;display:flex;justify-content:space-between">'
        '<span>Faizan Ahmed, SE23UCSE003 | ConsciousMind: Morals and Ethics | Research Progress Report</span>'
        '<span>Page <span class="pageNumber"></span></span></div>')
head = ('<div style="font-family:DejaVu Sans,Arial;font-size:7px;color:#777;width:100%;padding:0 16mm">'
        'Faizan Ahmed, SE23UCSE003 | ConsciousMind: Morals and Ethics | Research Progress Report</div>')
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
    pg = b.new_page()
    pg.goto((here / "report.html").as_uri(), wait_until="networkidle")
    pg.pdf(path=str(out), format="A4", print_background=True, display_header_footer=True,
           header_template=head, footer_template=foot,
           margin={"top": "17mm", "bottom": "16mm", "left": "16mm", "right": "16mm"})
    b.close()
print(out)
