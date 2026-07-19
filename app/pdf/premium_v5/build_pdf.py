#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Saju Brasil — Leitura Premium (Ivã), PDF generator.

Reconstructed from the v5 visual reference. Produces an 18-page A4 report
with an editorial "Korean art book" aesthetic: ivory background, serif
titles + sans body, sparse layouts and small Hanja accents.

Dependencies:  pip install reportlab
Fonts (bundled in ./fonts/):
    Instrument Serif  (display serif, regular + italic)
    Crimson Pro       (body serif, regular + italic)
    Inter             (sans, regular + italic)
Hanja is rendered with ReportLab's built-in CID font HeiseiMin-W3 (Adobe-Japan1).

Usage:
    python build_pdf.py
Output: ./leitura_premium_iva.pdf
"""
from __future__ import annotations
import os, re, math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# ----------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT_PATH = os.path.join(HERE, "leitura_premium_iva.pdf")

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pt
MARGIN_X = 92
MARGIN_Y = 84
TOTAL_PAGES = 18

# Palette
IVORY      = HexColor("#f7f3ea")   # background
INK        = HexColor("#2b2540")   # deep indigo, titles
BODY       = HexColor("#3a3324")   # warm dark, body
MUTED      = HexColor("#8a7f6a")   # muted taupe
HAIRLINE   = HexColor("#c9bfa8")   # thin rules
ACCENT     = HexColor("#a03a2d")   # oxide red — for CJK accents, "you are here"
GOLD       = HexColor("#b58b3a")   # earth
GHOST      = HexColor("#e6dcc4")   # ghosted large hanja

# Element colors
COL_MADEIRA = HexColor("#4a6b46")
COL_FOGO    = HexColor("#a03a2d")
COL_TERRA   = HexColor("#b58b3a")
COL_METAL   = HexColor("#8a7f6a")
COL_AGUA    = HexColor("#3b5a7a")

def _register_fonts() -> None:
    def reg(name, fname):
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fname)))
    reg("Display",        "InstrumentSerif-Regular.ttf")
    reg("Display-It",     "InstrumentSerif-Italic.ttf")
    reg("Body",           "CrimsonPro-Regular.ttf")
    reg("Body-It",        "CrimsonPro-Italic.ttf")
    reg("Sans",           "Inter-Regular.ttf")
    reg("Sans-It",        "Inter-Italic.ttf")
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

_register_fonts()
CJK = "HeiseiMin-W3"

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x2E80 <= cp <= 0x9FFF or
        0xF900 <= cp <= 0xFAFF or
        0x3000 <= cp <= 0x30FF or
        0xFF00 <= cp <= 0xFFEF
    )

def draw_bg(c: canvas.Canvas) -> None:
    c.setFillColor(IVORY); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

def draw_footer(c: canvas.Canvas, chapter: str, page: int) -> None:
    y = 44
    c.setFillColor(MUTED); c.setFont("Sans-It", 7.5)
    c.drawString(MARGIN_X, y, chapter)
    c.setFont("Sans", 7.5)
    label = f"— {page:02d} / {TOTAL_PAGES} —"
    c.drawCentredString(PAGE_W/2, y, label)
    c.drawRightString(PAGE_W - MARGIN_X, y, "SAJU BRASIL")

def draw_hanja_glyph(c: canvas.Canvas, ch: str, x: float, y: float, size: float, color=ACCENT) -> None:
    c.setFillColor(color); c.setFont(CJK, size)
    c.drawCentredString(x, y, ch)

def draw_top_hanja(c: canvas.Canvas, ch: str) -> None:
    draw_hanja_glyph(c, ch, PAGE_W/2, PAGE_H - 60, 12, ACCENT)

def draw_chapter_header(c: canvas.Canvas, roman: str, label: str, title_main: str, title_italic: str, subtitle: str) -> None:
    x = MARGIN_X
    y = PAGE_H - 140
    c.setFillColor(MUTED); c.setFont("Sans", 8)
    c.drawString(x, y, f"{roman}  ·  {label.upper()}")
    c.setStrokeColor(ACCENT); c.setLineWidth(0.8)
    c.line(x, y - 8, x + 60, y - 8)
    # Title
    y2 = y - 60
    c.setFillColor(INK); c.setFont("Display", 30)
    tw = c.stringWidth(title_main + " ", "Display", 30)
    c.drawString(x, y2, title_main + " ")
    c.setFont("Display-It", 30)
    c.drawString(x + tw, y2, title_italic)
    # Subtitle
    c.setFillColor(MUTED); c.setFont("Body-It", 11)
    c.drawString(x, y2 - 24, subtitle)

# --- Inline styled text with CJK-aware fallback --------------------------------
# Style tokens: **bold**, *italic*; auto-detects CJK codepoints and swaps font.

_TOKEN_RE = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")

def _split_style(text: str):
    """Yield (segment, style) where style ∈ {'', 'b', 'i'}."""
    for part in _TOKEN_RE.split(text):
        if not part: continue
        if part.startswith("**") and part.endswith("**"):
            yield part[2:-2], "b"
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            yield part[1:-1], "i"
        else:
            yield part, ""

def _font_for(style: str, base_family: str) -> str:
    # base_family: 'Body' or 'Sans'
    if style == "b":  # emulate bold on Crimson: keep Body but slightly heavier via overprint if needed; use Sans-bold-like fallback (Inter regular is fine but we want emphasis) — swap to a heavier serif alt: fake bold via twice-drawn.
        return base_family
    if style == "i":
        return base_family + "-It"
    return base_family

def _atoms(text: str, style: str, base_family: str, size: float):
    """Break text into atoms grouped by [font, is_cjk]."""
    curr = []
    curr_cjk = None
    latin_font = _font_for(style, base_family)
    for ch in text:
        cjk = is_cjk(ch)
        if curr_cjk is None:
            curr_cjk = cjk
        if cjk != curr_cjk:
            yield "".join(curr), (CJK if curr_cjk else latin_font), style
            curr = []; curr_cjk = cjk
        curr.append(ch)
    if curr:
        yield "".join(curr), (CJK if curr_cjk else latin_font), style

def _measure(atoms, size):
    w = 0
    for text, font, _ in atoms:
        w += pdfmetrics.stringWidth(text, font, size)
    return w

def draw_wrapped(c: canvas.Canvas, text: str, x: float, y: float, w: float,
                 size=10.5, leading=15, base_family="Body", color=BODY,
                 align="left") -> float:
    """Draw a styled, CJK-aware wrapped paragraph. Returns new y."""
    # Split into words but keep whitespace groups
    # We tokenize into segments, then further split each segment into words.
    styled_words = []  # list of (word_atoms, style)
    for seg, style in _split_style(text):
        # Split preserving spaces
        parts = re.split(r"(\s+)", seg)
        for p in parts:
            if not p: continue
            if p.isspace():
                styled_words.append((list(_atoms(p, style, base_family, size)), style, True))
            else:
                styled_words.append((list(_atoms(p, style, base_family, size)), style, False))

    # Build lines
    lines = []
    line = []
    line_w = 0
    for atoms, style, is_space in styled_words:
        aw = _measure(atoms, size)
        if not line and is_space:
            continue  # skip leading space
        if line_w + aw > w and line:
            # drop trailing space
            while line and line[-1][2]:
                line_w -= _measure(line[-1][0], size)
                line.pop()
            lines.append(line)
            line = []
            line_w = 0
            if is_space:
                continue
        line.append((atoms, style, is_space))
        line_w += aw
    if line:
        while line and line[-1][2]:
            line.pop()
        if line:
            lines.append(line)

    for ln in lines:
        line_width = sum(_measure(a, size) for a, s, sp in ln)
        if align == "center":
            cx = x + (w - line_width) / 2
        elif align == "right":
            cx = x + w - line_width
        else:
            cx = x
        for atoms, style, _ in ln:
            for atext, afont, astyle in atoms:
                c.setFont(afont, size)
                c.setFillColor(color)
                c.drawString(cx, y, atext)
                aw = pdfmetrics.stringWidth(atext, afont, size)
                if astyle == "b":
                    # Fake bold: overprint at +0.35pt offset
                    c.drawString(cx + 0.35, y, atext)
                cx += aw
        y -= leading
    return y

# ----------------------------------------------------------------------------
# Small vector motifs
# ----------------------------------------------------------------------------

def motif_mountain(c, cx, cy, s=30, color=INK):
    c.setStrokeColor(color); c.setLineWidth(0.7); c.setFillColor(IVORY)
    p = c.beginPath()
    p.moveTo(cx - s, cy)
    p.lineTo(cx - s*0.3, cy + s*0.9)
    p.lineTo(cx - s*0.05, cy + s*0.55)
    p.lineTo(cx + s*0.35, cy + s)
    p.lineTo(cx + s, cy)
    c.drawPath(p, stroke=1, fill=0)

def motif_bamboo(c, cx, cy, s=30, color=INK):
    c.setStrokeColor(color); c.setLineWidth(0.7)
    # main stalk
    c.line(cx, cy, cx, cy + s*1.6)
    # nodes
    for i in range(3):
        yy = cy + s*0.4*(i+1)
        c.line(cx - 4, yy, cx + 4, yy)
    # leaves as gentle curves
    p = c.beginPath()
    p.moveTo(cx, cy + s*0.8); p.curveTo(cx+8, cy+s*0.9, cx+18, cy+s*0.75, cx+22, cy+s*0.6)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath()
    p.moveTo(cx, cy + s*1.2); p.curveTo(cx+6, cy+s*1.25, cx+14, cy+s*1.15, cx+18, cy+s*1.0)
    c.drawPath(p, stroke=1, fill=0)

def motif_wave(c, cx, cy, s=30, color=INK):
    c.setStrokeColor(color); c.setLineWidth(0.6)
    for i in range(2):
        yy = cy + i*4
        p = c.beginPath()
        p.moveTo(cx - s, yy)
        for k in range(6):
            x0 = cx - s + k*(2*s/6)
            x1 = x0 + (2*s/6)
            p.curveTo(x0 + s/12, yy + 3, x1 - s/12, yy + 3, x1, yy)
        c.drawPath(p, stroke=1, fill=0)

def motif_seal(c, cx, cy, ch="四柱", size=10):
    """Small red seal square with 2 hanja."""
    r = 10
    c.setFillColor(ACCENT); c.setStrokeColor(ACCENT)
    c.rect(cx - r, cy - r, 2*r, 2*r, fill=1, stroke=0)
    c.setFillColor(IVORY); c.setFont(CJK, size)
    # split 2 chars vertically
    if len(ch) >= 2:
        c.drawCentredString(cx, cy + 1.5, ch[0])
        c.drawCentredString(cx, cy - 8, ch[1])
    else:
        c.drawCentredString(cx, cy - size/3, ch)

def hairline(c, x1, y1, x2, y2, color=HAIRLINE, w=0.5):
    c.setStrokeColor(color); c.setLineWidth(w); c.line(x1, y1, x2, y2)

def centered_ornament(c, cx, cy, color=ACCENT):
    """— · — ornament."""
    c.setStrokeColor(color); c.setLineWidth(0.6)
    c.line(cx - 22, cy, cx - 6, cy)
    c.line(cx + 6, cy, cx + 22, cy)
    c.setFillColor(color); c.circle(cx, cy, 1.0, fill=1, stroke=0)

# ============================================================================
# PAGES
# ============================================================================

def page_cover(c):
    draw_bg(c)
    # Corner brackets
    c.setStrokeColor(HAIRLINE); c.setLineWidth(0.6)
    L = 22; m = 46
    for (x, y, dx, dy) in [
        (m, PAGE_H-m, 1, -1), (PAGE_W-m, PAGE_H-m, -1, -1),
        (m, m, 1, 1), (PAGE_W-m, m, -1, 1),
    ]:
        c.line(x, y, x + dx*L, y); c.line(x, y, x, y + dy*L)

    # Header brand
    c.setFillColor(MUTED); c.setFont("Sans", 9)
    c.drawCentredString(PAGE_W/2, PAGE_H - 140, "S A J U   B R A S I L")
    hairline(c, PAGE_W/2 - 14, PAGE_H - 154, PAGE_W/2 + 14, PAGE_H - 154, MUTED)

    # Ghosted large Hanja (Mu 戊)
    c.setFillColor(GHOST); c.setFont(CJK, 380)
    c.drawCentredString(PAGE_W/2, PAGE_H - 560, "戊")

    # Titles
    c.setFillColor(INK); c.setFont("Display", 30)
    c.drawCentredString(PAGE_W/2, 260, "Leitura Personalizada")
    c.setFont("Display-It", 30)
    c.drawCentredString(PAGE_W/2, 232, "Premium")
    c.setFillColor(MUTED); c.setFont("Body-It", 11)
    c.drawCentredString(PAGE_W/2, 212, "um retrato dos seus padrões, pela tradição coreana dos Quatro Pilares")

    # Name
    c.setFillColor(INK); c.setFont("Display", 34)
    c.drawCentredString(PAGE_W/2, 160, "Ivã")
    c.setFillColor(MUTED); c.setFont("Sans", 9)
    meta = "11 · 11 · 1982     ·     12H30     ·     SALVADOR, BAHIA"
    c.drawCentredString(PAGE_W/2, 138, meta)

    # Red seal
    motif_seal(c, PAGE_W/2, 110, "四柱", 10)

    # Bottom epigraph
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, 76, "não é sobre prever sua vida — é sobre entender seus padrões para decidir melhor")

def page_colophon(c):
    draw_bg(c)
    # top-right hanja + kanji label
    c.setFillColor(ACCENT); c.setFont(CJK, 11)
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 60, "四 柱")

    # Centered epigraph
    c.setFillColor(INK); c.setFont("Display-It", 18)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 + 20, "abra sem pressa.")
    c.drawCentredString(PAGE_W/2, PAGE_H/2 - 6, "este mapa é seu.")

    # Colophon bottom-left
    x = MARGIN_X; y = 160
    c.setFillColor(MUTED); c.setFont("Sans", 8); c.setLineWidth(0.5)
    for line in ["EDIÇÃO PREMIUM · V.5", "SAJU BRASIL · SÃO PAULO", "IMPRESSO PARA IVÃ"]:
        c.drawString(x, y, line); y -= 12
    hairline(c, x, y+4, x+40, y+4, MUTED)
    y -= 12
    c.drawString(x, y, "TIRAGEM ÚNICA")

def page_intro(c):
    draw_bg(c); draw_top_hanja(c, "序")
    draw_chapter_header(c, "I", "Abertura", "Antes de ler", "o seu mapa",
                        "uma tradição de séculos, agora na sua mão")

    # Body block
    x = MARGIN_X + 40; y = PAGE_H - 260; w = PAGE_W - 2*MARGIN_X - 80
    p1 = ("Na Coreia, antes de um casamento, de uma sociedade ou de uma grande decisão, é "
          "comum consultar o **Saju** — os quatro pilares. A palavra vem do costume de ler o "
          "destino de uma pessoa a partir de quatro colunas: o ano, o mês, o dia e a hora em "
          "que ela nasceu. Cada pilar carrega dois caracteres; os oito juntos formam um "
          "retrato único — o seu.")
    p2 = ("O Saju não é religião, nem adivinhação. É um sistema de observação refinado por "
          "gerações de estudiosos, que lê o mundo através de **cinco elementos** — Madeira, "
          "Fogo, Terra, Metal e Água — e dos ritmos com que eles se alimentam e se contêm. "
          "Na Coreia de hoje, ele convive naturalmente com a vida moderna: universitárias "
          "consultam o Saju antes de escolher carreira, casais antes do casamento, "
          "empreendedores antes de abrir negócios.")
    p3 = ("Não para saber \"o que vai acontecer\" — mas para entender **com que padrões estão "
          "jogando**. É assim que a Saju Brasil trabalha: *não é sobre prever sua vida — é sobre "
          "entender seus padrões para decidir melhor.*")

    y = draw_wrapped(c, p1, x, y, w, 10.5, 15); y -= 6
    y = draw_wrapped(c, p2, x, y, w, 10.5, 15); y -= 6
    y = draw_wrapped(c, p3, x, y, w, 10.5, 15)

    # bamboo decoration bottom-right
    motif_bamboo(c, PAGE_W - MARGIN_X - 20, 160, 36, color=INK)
    draw_footer(c, "i · abertura", 3)

def page_method(c):
    draw_bg(c); draw_top_hanja(c, "讀")
    draw_chapter_header(c, "II", "Método", "Como ler", "o seu mapa", "o mapa em camadas")

    items = [
        ("i",   "Os Quatro Pilares", "ano (raízes e herança), mês (vida pública e carreira), dia (eu íntimo e vínculos) e hora (projetos e maturidade)."),
        ("ii",  "O Mestre do Dia",   "o caractere que rege o pilar do dia é o centro de tudo: o \"você essencial\". Todo o restante do mapa é lido em relação a ele."),
        ("iii", "Os Cinco Elementos","a contagem revela seus talentos naturais (o que transborda) e suas habilidades a cultivar (o que falta). Não existe mapa perfeito: existe mapa compreendido."),
        ("iv",  "Os Dez Arquétipos", "dez padrões clássicos que descrevem como cada energia do mapa se relaciona com o seu centro. Os que acendem — e os que se apagam — desenham seu jeito único de funcionar."),
        ("v",   "Os Ciclos de Década","a vida avança em fases de dez anos. Elas não determinam o que acontece: indicam o clima de cada década — quando plantar, quando construir, quando colher."),
    ]
    y = PAGE_H - 275
    x_num = MARGIN_X + 60; x_txt = MARGIN_X + 100
    w = PAGE_W - MARGIN_X - x_txt
    for roman, title, desc in items:
        c.setFillColor(ACCENT); c.setFont("Display-It", 16)
        c.drawRightString(x_num, y, roman)
        c.setFillColor(INK); c.setFont("Display", 13)
        c.drawString(x_txt, y, title)
        yy = y - 16
        yy = draw_wrapped(c, desc, x_txt, yy, w, 9.8, 13.5, color=BODY)
        y = yy - 10

    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    y -= 4
    y = draw_wrapped(c,
        "Leia sem pressa, de preferência num momento só seu. Marque o que fizer sentido — e também o que incomodar: costuma ser onde mora o crescimento.",
        x_txt, y, w, 10, 14, base_family="Body", color=MUTED)

    draw_footer(c, "ii · método", 4)

def page_pillars(c):
    draw_bg(c); draw_top_hanja(c, "四")
    draw_chapter_header(c, "III", "Estrutura", "Os Quatro", "Pilares",
                        "as energias do momento exato do seu nascimento")

    # 4 columns
    cols = [
        ("ANO",  "raízes · origem",      "壬", "戌", "Im · Água Yang", "Sul · Cão, Terra"),
        ("MÊS",  "carreira · vida pública","辛", "亥", "Sin · Metal Yin","Hae · Porco, Água"),
        ("DIA",  "eu íntimo · vínculos", "戊", "戌", "Mu · Terra Yang", "Sul · Cão, Terra"),
        ("HORA", "projetos · maturidade","戊", "午", "Mu · Terra Yang", "O · Cavalo, Fogo"),
    ]
    top_y = PAGE_H - 300
    col_w = (PAGE_W - 2*MARGIN_X) / 4
    for i, (label, sub, top_ch, bot_ch, l1, l2) in enumerate(cols):
        cx = MARGIN_X + col_w*(i + 0.5)
        # header
        c.setFillColor(ACCENT); c.setFont("Sans", 8)
        c.drawCentredString(cx, top_y, label)
        c.setFillColor(MUTED); c.setFont("Body-It", 8.5)
        c.drawCentredString(cx, top_y - 12, sub)
        # hanja stack
        c.setFillColor(INK); c.setFont(CJK, 56)
        c.drawCentredString(cx, top_y - 78, top_ch)
        c.drawCentredString(cx, top_y - 138, bot_ch)
        # divider
        if i < 3:
            x_div = MARGIN_X + col_w*(i+1)
            hairline(c, x_div, top_y - 148, x_div, top_y - 30, HAIRLINE)
        # legend
        c.setFillColor(ACCENT); c.setLineWidth(0.6)
        c.line(cx - 14, top_y - 168, cx - 4, top_y - 168)
        c.setFillColor(BODY); c.setFont("Sans", 8)
        c.drawCentredString(cx, top_y - 180, l1)
        c.drawCentredString(cx, top_y - 192, l2)

    # Bottom epigraph
    y = 220
    c.setFillColor(BODY); c.setFont("Body-It", 11)
    c.drawCentredString(PAGE_W/2, y, "Oito caracteres · cinco elementos em jogo.")
    y -= 20
    # "No centro, o seu Mestre do Dia: Mu (戊) — a Montanha."
    txt = "No centro, o seu Mestre do Dia: Mu (戊) — a Montanha."
    # measure & center manually with mixed CJK
    parts = [("No centro, o seu Mestre do Dia: Mu (", "Body-It"),
             ("戊", CJK),
             (") — a Montanha.", "Body-It")]
    total = sum(pdfmetrics.stringWidth(t, f, 11) for t, f in parts)
    cx = (PAGE_W - total)/2
    for t, f in parts:
        c.setFont(f, 11); c.setFillColor(BODY); c.drawString(cx, y, t)
        cx += pdfmetrics.stringWidth(t, f, 11)

    motif_seal(c, PAGE_W/2, 150, "四柱", 9)
    draw_footer(c, "iii · estrutura", 5)

def page_elements(c):
    draw_bg(c); draw_top_hanja(c, "五")
    draw_chapter_header(c, "IV", "Balança", "Os Cinco", "Elementos",
                        "o que transborda são talentos naturais · o que falta, habilidades a cultivar")

    # Five circles at middle
    els = [
        ("木", "MADEIRA", 0, "0%",  COL_MADEIRA),
        ("火", "FOGO",    1, "12%", COL_FOGO),
        ("土", "TERRA",   4, "50%", COL_TERRA),
        ("金", "METAL",   1, "12%", COL_METAL),
        ("水", "ÁGUA",    2, "25%", COL_AGUA),
    ]
    cy = PAGE_H - 470
    total_w = PAGE_W - 2*MARGIN_X
    step = total_w / 5
    for i, (ch, name, count, pct, col) in enumerate(els):
        cx = MARGIN_X + step*(i + 0.5)
        # circle
        r = 22
        if name == "TERRA":
            c.setFillColor(col); c.setStrokeColor(col)
            c.circle(cx, cy, r, fill=1, stroke=0)
            c.setFillColor(IVORY)
        else:
            c.setFillColor(IVORY); c.setStrokeColor(col); c.setLineWidth(1.0)
            c.circle(cx, cy, r, fill=1, stroke=1)
            c.setFillColor(col)
        c.setFont(CJK, 18)
        c.drawCentredString(cx, cy - 6, ch)
        # name
        c.setFillColor(ACCENT if name=="TERRA" else MUTED); c.setFont("Sans", 8)
        c.drawCentredString(cx, cy - 40, name)
        # count big
        c.setFillColor(col); c.setFont("Display", 22)
        c.drawCentredString(cx, cy - 66, str(count))
        # percent
        c.setFillColor(MUTED); c.setFont("Sans", 7.5)
        c.drawCentredString(cx, cy - 80, pct)

    # ornament + verdict
    centered_ornament(c, PAGE_W/2, cy - 108)
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, cy - 128, "Dominante: Terra  ·  Ausente: Madeira")
    c.setFillColor(INK); c.setFont("Display", 15)
    c.drawCentredString(PAGE_W/2, cy - 150, "Seu elemento de equilíbrio")
    c.setFillColor(ACCENT); c.setFont("Display-It", 22)
    c.drawCentredString(PAGE_W/2, cy - 176, "Madeira")

    draw_footer(c, "iv · balança", 6)

def page_reading(c):
    draw_bg(c); draw_top_hanja(c, "戊")
    draw_chapter_header(c, "V", "Leitura", "A sua", "leitura", "a conversa longa, sem pressa")

    x = MARGIN_X + 40; y = PAGE_H - 260; w = PAGE_W - 2*MARGIN_X - 80
    p1 = ("Ivã, este é o seu mapa completo. Não a versão essencial — a conversa longa, aquela em que "
          "a gente senta sem pressa e vai camada por camada. O Saju é o sistema com que a Coreia lê, "
          "há séculos, os padrões que cada pessoa carrega do instante em que nasceu. Oito caracteres, "
          "quatro pilares, e dentro deles: seu jeito de decidir, de amar, de prosperar, de travar e de "
          "destravar.")
    p2 = ("A primeira verdade da casa vale dobrado aqui: **não é sobre prever sua vida — é sobre "
          "entender seus padrões para decidir melhor.**")
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w); y -= 10

    # Sub-heading
    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "A estrutura")
    hairline(c, x, y - 4, x + 60, y - 4, ACCENT)
    y -= 22

    p3 = ("Quatro pilares sustentam a sua leitura. O do **ano** — suas raízes — traz Água Yang sobre o "
          "Cão. O do **mês** — sua face pública — Metal Yin sobre o Porco. O do **dia** — seu eu íntimo — "
          "Terra Yang sobre o Cão. E o da **hora** — seus projetos e legado — Terra Yang sobre o Cavalo. "
          "Oito caracteres, cinco elementos em jogo, e no centro deles o seu Mestre do Dia: **Mu (戊), a "
          "Terra Yang. A montanha.**")
    p4 = ("Seu mapa mostra tendências de funcionamento, não definições fixas. Mas as tendências, "
          "você vai ver, contam uma história impressionantemente coerente.")
    y = draw_wrapped(c, p3, x, y, w); y -= 6
    y = draw_wrapped(c, p4, x, y, w)

    motif_mountain(c, PAGE_W - MARGIN_X - 40, 160, 20, INK)
    draw_footer(c, "v · leitura", 7)

def page_core(c):
    draw_bg(c); draw_top_hanja(c, "性")
    draw_chapter_header(c, "VI", "Núcleo", "O núcleo", "de quem você é",
                        "os dez arquétipos — três acesos, dois apagados")

    x = MARGIN_X + 40; y = PAGE_H - 265; w = PAGE_W - 2*MARGIN_X - 80
    p1 = ("Antes de aprofundar, deixa eu te apresentar uma camada que o relatório essencial só toca de "
          "longe: os **dez deuses** (十神).    Apesar do nome dramático, não são divindades — são os **dez "
          "arquétipos** com que o Saju descreve como cada energia do mapa se relaciona com o seu "
          "centro.")
    p2 = ("Cinco pares: o Companheiro e o Rival (relações de igual para igual), o Deus do Alimento e o "
          "Oficial Ferido (expressão criativa), a Riqueza Direta e a Indireta (jeito de gerar valor), o "
          "Oficial Direto e o Indireto (relação com ordem e autoridade), o Selo Direto e o Indireto (jeito "
          "de aprender e ser amparado).")
    p3 = ("Cada mapa acende alguns desses dez e apaga outros — e é esse desenho que faz de você, "
          "você. O seu acende três, e a combinação é rara.")
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w); y -= 6
    y = draw_wrapped(c, p3, x, y, w); y -= 10

    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "Os que acendem")
    hairline(c, x, y - 4, x + 90, y - 4, ACCENT)
    y -= 22

    p4 = ("**A Riqueza Indireta (偏財)** é a energia mais forte do seu mapa — o arquétipo do caçador de "
          "oportunidades. Quem tem essa dominância não enxerga o dinheiro como salário: enxerga "
          "como fluxo, projeto, valor escondido onde ninguém olhou. É a marca do empreendedor.")
    p5 = ("**O Oficial Ferido (傷官)** — nome estranho, comportamento que você conhece bem: é o olhar "
          "que entra em qualquer sala e vê, em segundos, o que está errado e como poderia ser melhor. "
          "No seu pilar do mês, ele atua na carreira: você não consegue executar sem questionar. Isso já "
          "te causou atrito com chefias, aposto. Também é sua maior vantagem competitiva.")
    p6 = ("**O Selo Direto (正印)**, em dose leve, é o amparo do conhecimento: o estudioso discreto em "
          "você, que confia no que aprendeu e busca legitimidade no saber.")
    y = draw_wrapped(c, p4, x, y, w); y -= 6
    y = draw_wrapped(c, p5, x, y, w); y -= 6
    y = draw_wrapped(c, p6, x, y, w)

    draw_footer(c, "vi · núcleo", 8)

def page_breath_core(c):
    draw_bg(c)
    y = PAGE_H/2 + 30
    c.setFillColor(INK); c.setFont("Display-It", 22)
    text = "um solitário confiável, com olhar de"
    c.drawCentredString(PAGE_W/2, y, text); y -= 30
    c.drawCentredString(PAGE_W/2, y, "melhorista, fome de oportunidade e"); y -= 30
    c.drawCentredString(PAGE_W/2, y, "respaldo no estudo.")
    c.setFillColor(MUTED); c.setFont("Body-It", 9)
    c.drawCentredString(PAGE_W/2, y - 34, "esse é o núcleo.")
    motif_mountain(c, PAGE_W/2, y - 100, 26, INK)
    # simple centered page number
    c.setFillColor(MUTED); c.setFont("Sans", 7.5)
    c.drawCentredString(PAGE_W/2, 44, f"— 09 / {TOTAL_PAGES} —")

def page_block(c):
    draw_bg(c); draw_top_hanja(c, "阻")
    draw_chapter_header(c, "VII", "Bloqueio", "O bloqueio", "central",
                        "a seção que peço que você releia daqui a um mês")

    x = MARGIN_X + 40; y = PAGE_H - 260; w = PAGE_W - 2*MARGIN_X - 80
    p1 = ("Seu mapa tem quatro partes de Terra e **zero de Madeira**. A Terra acumula: responsabilidade, "
          "patrimônio, conhecimento, peso. A Madeira rompe e cresce: o novo, o risco, o começo "
          "imperfeito. Sem Madeira nativa, o seu excesso de Terra não encontra quem o desafie — e a "
          "Riqueza Indireta, o seu caçador de oportunidades, fica **enterrada sob a montanha**.")
    p2 = ("Você VÊ a oportunidade (o Oficial Ferido garante isso), sente o impulso (a Riqueza Indireta "
          "garante isso)… e a Terra diz \"espera, analisa mais um pouco, ainda não é seguro\".")
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w); y -= 8

    # highlighted line
    c.setFillColor(INK); c.setFont("Display", 13)
    y -= 6
    y = draw_wrapped(c, "o seu bloqueio central tem nome: a espera pelo 100% pronto.",
                     x + 20, y, w - 20, size=13, leading=18, color=INK, base_family="Body")
    y -= 6

    p3 = ("Não é medo, não é preguiça — é o mecanismo da sua própria solidez trabalhando contra "
          "você. E aqui vai o dado mais revelador do seu mapa: dos 23 aos 42 anos, seus ciclos de "
          "década foram de **Madeira dupla** (Tigre e Coelho). Durante vinte anos, a vida te emprestou o "
          "elemento que te falta — e aposto que foram suas décadas de mais crescimento.")
    p4 = ("Esses ciclos acabaram. A Madeira agora não vem mais de graça: **precisa ser plantada por "
          "decisão sua, todos os dias.** Quem entende isso, destrava. Quem não entende, passa a vida "
          "esperando voltar um vento que era emprestado.")
    y = draw_wrapped(c, p3, x, y, w); y -= 6
    y = draw_wrapped(c, p4, x, y, w)

    motif_bamboo(c, PAGE_W - MARGIN_X - 30, 150, 30, INK)
    draw_footer(c, "vii · bloqueio", 10)

def page_five(c):
    draw_bg(c); draw_top_hanja(c, "五")
    draw_chapter_header(c, "VIII", "Elementos", "Os cinco elementos, ", "um a um",
                        "leitura por dentro da balança")

    x = MARGIN_X + 40; y = PAGE_H - 270; w = PAGE_W - 2*MARGIN_X - 80
    lines = [
        "**Terra (4)** — sua fundação e seu excesso. Dá constância, palavra firme, senso prático. Em excesso: acúmulo, rigidez de rotina, dificuldade de soltar.",
        "**Água (2)** — sua fluidez social e financeira: você negocia, sente o ambiente, adapta o discurso. É a Água que impede sua montanha de virar pedra.",
        "**Fogo (1)** — presente em dose única, no pilar da hora: seu entusiasmo é seletivo e tardio — acende para projetos, não para plateias.",
        "**Metal (1)** — no pilar do mês: precisão e crítica na vida pública, o fio da sua análise.",
        "**Madeira (0)** — a ausência que define o jogo, como você já viu.",
    ]
    for ln in lines:
        y = draw_wrapped(c, ln, x, y, w); y -= 8

    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y - 4, "Prescrição")
    hairline(c, x, y - 8, x + 70, y - 8, ACCENT)
    y -= 26

    p1 = ("Sua prescrição de equilíbrio é uma só, repetida sem culpa: **plante Madeira.** Estudo novo a "
          "cada ciclo, verde no ambiente de trabalho, projetos que começam pequenos e crescem, "
          "natureza com frequência de remédio.")
    p2 = "Quando a vida pesar, não pergunte \"o que corto?\" — pergunte *\"o que planto?\".*"
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w)

    motif_wave(c, MARGIN_X + 30, 160, 30, INK)
    draw_footer(c, "viii · elementos", 11)

def page_career(c):
    draw_bg(c); draw_top_hanja(c, "業")
    draw_chapter_header(c, "IX", "Vocação", "Carreira ", "& prosperidade",
                        "o desenho do seu trabalho e do seu dinheiro")

    x = MARGIN_X + 40; y = PAGE_H - 265; w = PAGE_W - 2*MARGIN_X - 80
    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "Carreira e vocação")
    hairline(c, x, y - 4, x + 110, y - 4, ACCENT); y -= 22

    p1 = ("Seu desenho profissional é claro: **você foi feito para construir o próprio terreno.** O padrão da "
          "Riqueza Indireta com Oficial Ferido é quase incompatível com subordinação longa — você "
          "respeita competência, não cargo.")
    p2 = ("Ambientes onde você floresce: autonomia, problema difícil, resultado mensurável, poucas "
          "reuniões. Ambientes onde murcha: hierarquia rígida, processo pelo processo, chefias que "
          "pedem execução sem escuta.")
    p3 = ("Sua forma natural de liderar não é carismática — é **estrutural**: você lidera criando o chão "
          "firme onde os outros conseguem trabalhar. Times pequenos e leais funcionam melhor para "
          "você.")
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w); y -= 6
    y = draw_wrapped(c, p3, x, y, w); y -= 12

    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "Prosperidade")
    hairline(c, x, y - 4, x + 80, y - 4, ACCENT); y -= 22

    p4 = ("Com Riqueza Indireta dominante sobre base de Terra, seu dinheiro tem duas velocidades: "
          "**enxerga rápido, constrói devagar** — patrimônio sólido vindo de fontes que ninguém mais "
          "viu. Seu risco não é gastar demais; é **analisar demais**: a oportunidade tem prazo de validade, "
          "e a Terra adora perder esse prazo com prudência.")
    p5 = ("Seu ajuste financeiro: defina de antemão quanto do seu capital (de dinheiro E de tempo) é "
          "*\"verba de plantio\"* — a parte que PODE ser arriscada sem ameaçar a montanha. Com a "
          "fronteira clara, sua prudência para de vetar tudo e passa a proteger só o que deve proteger.")
    y = draw_wrapped(c, p4, x, y, w); y -= 6
    y = draw_wrapped(c, p5, x, y, w)

    draw_footer(c, "ix · vocação", 12)

def page_love(c):
    draw_bg(c); draw_top_hanja(c, "情")
    draw_chapter_header(c, "X", "Vínculos", "Amor ", "e a sua cena",
                        "lealdade de montanha  ·  animais dos ramos  ·  a única estrela")

    x = MARGIN_X + 40; y = PAGE_H - 265; w = PAGE_W - 2*MARGIN_X - 80
    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "Amor e vínculos"); hairline(c, x, y-4, x+100, y-4, ACCENT); y -= 22
    p1 = ("No pilar do dia, a montanha ama como montanha: **lealdade absoluta, demonstração "
          "discreta.** Você prova amor provendo, resolvendo, estando — e espera que isso seja lido "
          "como a declaração que é. Nem sempre é.")
    p2 = ("Com Água no mapa, você se atrai por quem traz fluidez e movimento — justamente o que "
          "sua Terra não tem. É uma troca linda quando consciente, e uma fonte de atrito quando não. "
          "*Pergunta para levar: quando alguém que você ama muda de planos, o que você sente primeiro — "
          "curiosidade ou incômodo?*")
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w); y -= 10

    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "Seus animais"); hairline(c, x, y-4, x+80, y-4, ACCENT); y -= 22
    p3 = ("Os quatro animais dos seus ramos compõem uma cena: **dois Cães** (ano e dia) — lealdade em "
          "dose dupla, o guardião que protege o território; um **Porco** (mês) — na vida pública, "
          "generosidade e uma inteligência social que desarma; um **Cavalo** (hora) — nos projetos de "
          "longo prazo, o desejo de campo aberto, de correr o próprio percurso. *O guardião leal que "
          "sonha em galopar.*")
    y = draw_wrapped(c, p3, x, y, w); y -= 10

    c.setFillColor(ACCENT); c.setFont("Display-It", 14)
    c.drawString(x, y, "Sua estrela"); hairline(c, x, y-4, x+75, y-4, ACCENT); y -= 22
    p4 = ("Sobre eles, sua única estrela — o **Dossel Floral (華蓋殺)**: espiritualidade, arte, refinamento "
          "solitário. É a estrela dos que precisam de silêncio como os outros precisam de plateia. Tenha "
          "mais momentos só seus, com o mesmo compromisso com que as pessoas marcam reuniões.")
    y = draw_wrapped(c, p4, x, y, w)

    draw_footer(c, "x · vínculos", 13)

def page_cycles(c):
    draw_bg(c); draw_top_hanja(c, "運")
    draw_chapter_header(c, "XI", "Tempo", "Seus ciclos ", "de década",
                        "o clima de cada fase — quando plantar, construir, colher")

    # Timeline
    x_line = MARGIN_X + 90
    y_top = PAGE_H - 300
    rows = [
        ("3–12 anos",   "Água sobre Ja — Água (Rato)",       "壬子", False),
        ("13–22 anos",  "Água sobre Chuk — Terra (Boi)",     "癸丑", False),
        ("23–32 anos",  "Madeira sobre In — Madeira (Tigre)","甲寅", False),
        ("33–42 anos",  "Madeira sobre Myo — Madeira (Coelho)","乙卯", False),
        ("43–52 anos",  "Fogo sobre Jin — Terra (Dragão)",   "丙辰", True),
        ("53–62 anos",  "Fogo sobre Sa — Fogo (Serpente)",   "丁巳", False),
        ("63–72 anos",  "Terra sobre O — Fogo (Cavalo)",     "戊午", False),
        ("73–82 anos",  "Terra sobre Mi — Terra (Cabra)",    "己未", False),
        ("83–92 anos",  "Metal sobre Sin — Metal (Macaco)",  "庚申", False),
        ("93–102 anos", "Metal sobre Yu — Metal (Galo)",     "辛酉", False),
    ]
    row_h = 42
    # vertical line
    hairline(c, x_line, y_top - row_h*(len(rows)-1) - 8, x_line, y_top + 8, HAIRLINE, 0.6)

    for i, (age, desc, ch, active) in enumerate(rows):
        y = y_top - i*row_h
        # marker
        if active:
            c.setFillColor(ACCENT); c.setStrokeColor(ACCENT)
            c.circle(x_line, y, 4, fill=1, stroke=0)
        else:
            c.setFillColor(IVORY); c.setStrokeColor(HAIRLINE); c.setLineWidth(0.8)
            c.circle(x_line, y, 3.5, fill=1, stroke=1)
        # age
        c.setFillColor(ACCENT if active else INK); c.setFont("Display", 13)
        c.drawString(x_line + 18, y - 4, age)
        # description
        c.setFillColor(ACCENT if active else BODY); c.setFont("Body-It" if active else "Body", 10)
        c.drawString(x_line + 100, y - 4, desc)
        # "você está aqui"
        if active:
            c.setFillColor(ACCENT); c.setFont("Body-It", 9)
            c.drawRightString(PAGE_W - MARGIN_X - 44, y - 4, "você está aqui")
        # hanja right
        c.setFillColor(ACCENT if active else INK); c.setFont(CJK, 16)
        c.drawRightString(PAGE_W - MARGIN_X, y, ch)

    # bottom quote
    y_q = y_top - row_h*len(rows) - 20
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, y_q,
        "\"a percepção de sorte aumenta quando comportamento e contexto estão alinhados.\"")

    draw_footer(c, "xi · tempo", 14)

def page_breath_now(c):
    draw_bg(c)
    y = PAGE_H/2 + 20
    c.setFillColor(INK); c.setFont("Display-It", 26)
    c.drawCentredString(PAGE_W/2, y, "é agora.")
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, y - 28, "a sua década — 43 a 52 — é a que pede obra.")
    # simple open circle motif
    c.setStrokeColor(ACCENT); c.setLineWidth(0.7)
    c.circle(PAGE_W/2, y - 110, 14, fill=0, stroke=1)
    c.setFillColor(MUTED); c.setFont("Sans", 7.5)
    c.drawCentredString(PAGE_W/2, 44, f"— 15 / {TOTAL_PAGES} —")

def page_plan(c):
    draw_bg(c); draw_top_hanja(c, "行")
    draw_chapter_header(c, "XII", "Plano", "O seu ", "plano",
                        "o que fazer mais, o que evitar, por onde começar")

    x = MARGIN_X + 40; y = PAGE_H - 270; w = PAGE_W - 2*MARGIN_X - 80

    def block(title, body, y):
        c.setFillColor(ACCENT); c.setFont("Display-It", 13)
        c.drawString(x, y, title); hairline(c, x, y-4, x+len(title)*6, y-4, ACCENT)
        return draw_wrapped(c, body, x, y-20, w) - 6

    y = block("Faça mais",
              "Plante Madeira diariamente — um estudo em andamento, verde por perto, um projeto "
              "pequeno crescendo, sempre. Dê primeiros passos com **70% de certeza**, porque sua Terra "
              "completa os 30% no caminho. Separe sua *verba de plantio* e arrisque dentro dela sem culpa.", y)
    y = block("Evite",
              "Esperar o 100% pronto — no seu mapa, é o nome que o bloqueio usa para parecer "
              "prudência. Acumular responsabilidade alheia até sufocar o próprio novo. Amar só em atos: "
              "**diga também** — o outro não lê montanha.", y)
    y = block("Comece esta semana",
              "Escolha UMA oportunidade que você vem analisando há meses e dê nela um primeiro passo "
              "pequeno e irreversível — uma conversa marcada, um registro feito, um protótipo no ar.", y)

    y -= 8
    c.setFillColor(INK); c.setFont("Display-It", 15)
    draw_wrapped(c,
        "sua sorte é você quem faz — ela aumenta quando suas ações acompanham sua energia.",
        x + 30, y, w - 30, size=15, leading=22, color=INK, base_family="Body")

    motif_mountain(c, PAGE_W - MARGIN_X - 40, 160, 22, INK)
    draw_footer(c, "xii · plano", 16)

def page_synth(c):
    draw_bg(c); draw_top_hanja(c, "定")
    draw_chapter_header(c, "XIII", "Síntese", "Seu Saju ", "em quatro linhas",
                        "o mapa condensado, para levar consigo")

    x = MARGIN_X + 40; y = PAGE_H - 290; w = PAGE_W - 2*MARGIN_X - 80

    rows = [
        ("MESTRE DO DIA",       "Mu (戊) — Terra Yang",       "guardião leal com faro de empreendedor"),
        ("BLOQUEIO CENTRAL",    "a espera pelo 100% pronto", "prudência que veta o novo"),
        ("ELEMENTO DE EQUILÍBRIO","Madeira",                 "plantada por decisão, todos os dias"),
        ("SUA DÉCADA",          "43–52 · Fogo sobre Terra",  "o acumulado quer virar obra"),
    ]
    for label, main, right in rows:
        c.setFillColor(ACCENT); c.setFont("Sans", 7.5)
        c.drawString(x, y, label)
        hairline(c, x, y - 4, x + w, y - 4, HAIRLINE)
        # main (may include CJK)
        c.setFillColor(INK)
        # draw mixed
        parts = []
        for ch in main:
            parts.append((ch, CJK if is_cjk(ch) else "Display"))
        # collapse consecutive
        merged = []
        for ch, f in parts:
            if merged and merged[-1][1] == f:
                merged[-1] = (merged[-1][0] + ch, f)
            else:
                merged.append((ch, f))
        cx = x
        for t, f in merged:
            c.setFont(f, 18); c.drawString(cx, y - 22, t)
            cx += pdfmetrics.stringWidth(t, f, 18)
        # right descriptor
        c.setFillColor(MUTED); c.setFont("Body-It", 9.5)
        c.drawRightString(x + w, y - 22, right)
        y -= 52

    # ornament + quote
    centered_ornament(c, PAGE_W/2, y - 4)
    c.setFillColor(INK); c.setFont("Display-It", 13)
    q = ["\"quando você entende seu padrão,",
         "deixa de reagir no automático",
         "e passa a agir com intenção.\""]
    yy = y - 30
    for ln in q:
        c.drawCentredString(PAGE_W/2, yy, ln); yy -= 22

    motif_seal(c, PAGE_W/2, yy - 30, "四柱", 9)

    # brand line
    c.setFillColor(MUTED); c.setFont("Sans", 8)
    c.drawCentredString(PAGE_W/2, yy - 90,
        "SAJU BRASIL   ·   PARA IVÃ   ·   EDIÇÃO PREMIUM V.5   ·   SAJUBRASIL.COM.BR")

    draw_footer(c, "xiii · síntese", 17)

def page_closing(c):
    draw_bg(c)
    # mountain + bamboo composition
    motif_mountain(c, PAGE_W/2 - 20, PAGE_H/2 + 70, 40, INK)
    motif_bamboo(c, PAGE_W/2 + 30, PAGE_H/2 + 60, 30, INK)

    y = PAGE_H/2 - 20
    c.setFillColor(INK); c.setFont("Display-It", 20)
    c.drawCentredString(PAGE_W/2, y, "o seu caminho pede Madeira.")
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, y - 24, "cultive-a um pouco por dia — e volte a este mapa quando precisar")
    c.drawCentredString(PAGE_W/2, y - 38, "se lembrar de quem você é.")
    centered_ornament(c, PAGE_W/2, y - 62)

    y2 = 200
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    for line in [
        "este relatório é uma ferramenta de autoconhecimento baseada na tradição coreana do Saju.",
        "ele não substitui acompanhamento médico ou psicológico,",
        "e nenhum mapa decide por você: o caminho é sempre seu.",
    ]:
        c.drawCentredString(PAGE_W/2, y2, line); y2 -= 24

    c.setFillColor(MUTED); c.setFont("Sans", 7.5)
    c.drawCentredString(PAGE_W/2, 44, f"— 18 / {TOTAL_PAGES} —")

# ============================================================================
# Build
# ============================================================================

def build():
    c = canvas.Canvas(OUT_PATH, pagesize=A4)
    c.setTitle("Leitura Premium Saju — Ivã")
    c.setAuthor("Saju Brasil")

    pages = [
        page_cover, page_colophon, page_intro, page_method, page_pillars,
        page_elements, page_reading, page_core, page_breath_core, page_block,
        page_five, page_career, page_love, page_cycles, page_breath_now,
        page_plan, page_synth, page_closing,
    ]
    for p in pages:
        p(c); c.showPage()
    c.save()
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    build()
