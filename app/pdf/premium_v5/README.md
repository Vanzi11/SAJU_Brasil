# Saju Brasil — Leitura Premium (Ivã) — PDF generator

Standalone reconstruction of the Lovable-generated PDF (v5). Produces an
18-page A4 report with an editorial "Korean art book" aesthetic.

## Requirements

- Python 3.9+
- `pip install reportlab`

## Files

    build_pdf.py                           # generator (single file)
    data/relatorio_iva_premium_demonstracao.md   # source content (Ivã)
    fonts/InstrumentSerif-Regular.ttf
    fonts/InstrumentSerif-Italic.ttf
    fonts/CrimsonPro-Regular.ttf
    fonts/CrimsonPro-Italic.ttf
    fonts/Inter-Regular.ttf
    fonts/Inter-Italic.ttf

Hanja/CJK glyphs use ReportLab's built-in CID font `HeiseiMin-W3`
(Adobe-Japan1); no extra TTF needed.

## Run

    python build_pdf.py

Output: `leitura_premium_iva.pdf` in the same directory.

## Notes

- Content is currently inlined in `build_pdf.py` (page-by-page functions).
  The markdown in `data/` is kept as the canonical source you can edit
  and re-wire into the script when needed.
- Palette, fonts and layout constants live at the top of `build_pdf.py`.
- Font paths are resolved relative to the script (`./fonts/`).
- Fonts: Instrument Serif and Crimson Pro are OFL, Inter is OFL — see
  Google Fonts for licenses.

## Caveat

This is a reconstruction from the rendered v5 PDF, not the byte-identical
original script (which was lost in an ephemeral sandbox reset). Layout
matches v5 closely; small kerning / line-break differences are expected.
