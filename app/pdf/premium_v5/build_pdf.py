#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bitna Saju — Leitura Premium, gerador de PDF · direção de arte v5 ("livro de arte de Seul").

Uso:
    python build_pdf.py entrada.json saida.pdf

`entrada.json` segue a MESMA interface do gerador v4 (app/pdf/gerar_pdf.py):
    { "produto": "premium"|"essencial", "nome": str|null, "idadeAproximada": int|null,
      "leitura": {...saída de traduzirSaju + ciclosDeDecada...}, "relatorio": str|null }

Este arquivo era uma reconstrução hard-coded do mapa do Ivã (11/11/1982). Foi
parametrizado para receber qualquer mapa calculado pelo motor: número de
pilares variável (3 quando a hora é desconhecida), qualquer Mestre do Dia,
e o texto narrativo (`relatorio`, escrito pelo LLM a partir dos prompts em
`relatorios/prompts/`) flui em capítulos com paginação automática.

Dependências: pip install reportlab pillow
(Pillow só é usada para tingir os ícones raster em assets/icons/ na cor do
elemento; se não estiver instalada, o gerador cai de volta pros ícones
vetoriais desenhados a mão, sem quebrar.)
Fontes bundled em ./fonts/: Instrument Serif, Crimson Pro, Inter.
Hanja: fonte TTF embutida (nunca a CID HeiseiMin-W3, que não embute no PDF) —
malgun.ttf no Windows, DroidSansFallbackFull no Linux; ver _cjk_candidates().
Se nenhuma fonte CJK for encontrada, os glifos hanja são omitidos com
degradação graciosa (nunca quebra a geração do PDF).
"""
from __future__ import annotations
import os, re, sys, json, math, platform
from datetime import date
from io import BytesIO
from functools import lru_cache
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ----------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
ICON_DIR = os.path.join(HERE, "assets", "icons")

# Pedido do Ivã: o corpo do PDF estava pequeno demais pra ler confortavelmente
# no celular. Em vez de tocar em ~80 chamadas de setFont() espalhadas pelo
# arquivo (título, corpo, rótulos, rodapé...), a fonte inteira do documento
# sobe uniformemente aqui, num só lugar: fazemos o patch de canvas.setFont e
# de pdfmetrics.stringWidth (medida de largura de texto) para somarem o mesmo
# delta - assim a medição de quebra de linha e o desenho continuam batendo
# entre si (sem isso, o texto quebraria linha "cedo demais" e vazaria da
# coluna). O leading (espaço entre linhas) dos parágrafos corridos é ajustado
# à parte, dentro de draw_wrapped/draw_wrapped_paginated, pelo mesmo delta.
FONT_BUMP = 3.5

_orig_setFont = canvas.Canvas.setFont
def _bumped_setFont(self, psfontname, size, leading=None):
    return _orig_setFont(self, psfontname, size + FONT_BUMP, leading)
canvas.Canvas.setFont = _bumped_setFont

_orig_stringWidth = pdfmetrics.stringWidth
def _bumped_stringWidth(text, fontName, fontSize, encoding='utf8'):
    return _orig_stringWidth(text, fontName, fontSize + FONT_BUMP, encoding)
pdfmetrics.stringWidth = _bumped_stringWidth

PAGE_W, PAGE_H = A4  # 595.27 x 841.89 pt
MARGIN_X = 92
MARGIN_Y = 84

# Palette — D9 "Livraria de Seul": marfim, roxo profundo, dourado, cinza quente + selo vermelho.
IVORY      = HexColor("#f7f3ea")
INK        = HexColor("#2b2540")
BODY       = HexColor("#3a3324")
MUTED      = HexColor("#8a7f6a")
HAIRLINE   = HexColor("#c9bfa8")
ACCENT     = HexColor("#a03a2d")   # selo vermelho (dojang)
GOLD       = HexColor("#b58b3a")
GHOST      = HexColor("#e6dcc4")

COL_MADEIRA = HexColor("#4a6b46")
COL_FOGO    = HexColor("#a03a2d")
COL_TERRA   = HexColor("#b58b3a")
COL_METAL   = HexColor("#8a7f6a")
COL_AGUA    = HexColor("#3b5a7a")
ELEM_ORDER  = ["Madeira", "Fogo", "Terra", "Metal", "Água"]
ELEM_CH     = {"Madeira": "木", "Fogo": "火", "Terra": "土", "Metal": "金", "Água": "水"}
COR_ELEM    = {"Madeira": COL_MADEIRA, "Fogo": COL_FOGO, "Terra": COL_TERRA, "Metal": COL_METAL, "Água": COL_AGUA}
HEX_ELEM    = {"Madeira": "#4a6b46", "Fogo": "#a03a2d", "Terra": "#b58b3a", "Metal": "#8a7f6a", "Água": "#3b5a7a"}
HEX_INK     = "#2b2540"

def _register_latin_fonts() -> None:
    def reg(name, fname):
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fname)))
    reg("Display",    "InstrumentSerif-Regular.ttf")
    reg("Display-It", "InstrumentSerif-Italic.ttf")
    reg("Body",       "CrimsonPro-Regular.ttf")
    reg("Body-It",    "CrimsonPro-Italic.ttf")
    reg("Sans",       "Inter-Regular.ttf")
    reg("Sans-It",    "Inter-Italic.ttf")

def _cjk_candidates():
    """Ordem de busca por SO — D12/tarefa 1: sempre TTF embutida, nunca CID não-incorporada.
    (path, subfontIndex|None). Precisa cobrir hanja E hangul (termos coreanos em prosa,
    ver GUIA_DE_VOZ) — DroidSansFallback tem hanja mas NÃO hangul, por isso Noto Serif
    CJK (variante KR) vem primeiro quando disponível."""
    win = platform.system() == "Windows"
    noto_serif = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
    noto_sans = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
    linux_mac = [
        (noto_serif, 1),   # Noto Serif CJK KR — hanja + hangul, combina com a serifa do livro
        (noto_sans, 1),    # Noto Sans CJK KR — mesmo repertório, fallback
        ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", None),  # só hanja
        ("/usr/share/fonts-droid-fallback/truetype/DroidSansFallback.ttf", None),
        ("/System/Library/Fonts/PingFang.ttc", 0),
    ]
    win_paths = [("C:/Windows/Fonts/malgun.ttf", None), ("C:/Windows/Fonts/msyh.ttc", 0)]
    order = (win_paths + linux_mac) if win else (linux_mac + win_paths)
    env = os.environ.get("SAJU_CJK_FONT")
    return ([(env, None)] if env else []) + order

def _register_cjk_font():
    for path, idx in _cjk_candidates():
        if not path or not os.path.exists(path):
            continue
        try:
            if idx is not None:
                pdfmetrics.registerFont(TTFont("CJK", path, subfontIndex=idx))
            else:
                pdfmetrics.registerFont(TTFont("CJK", path))
            return "CJK"
        except Exception:
            continue
    return None

_register_latin_fonts()
CJK = _register_cjk_font()  # None => hanja é omitido com degradação graciosa

# ----------------------------------------------------------------------------
# Hangul → Hanja (posicional: tronco vs. ramo têm sílabas hangul que colidem,
# ex. 신 = 辛 tronco OU 申 ramo — por isso dois mapas, nunca um só global)
# ----------------------------------------------------------------------------

STEMS_H2H = {'갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊','기':'己','경':'庚','신':'辛','임':'壬','계':'癸'}
BRANCHES_H2H = {'자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳','오':'午','미':'未','신':'申','유':'酉','술':'戌','해':'亥'}

def ganji_para_hanja(ganji: str) -> str:
    if not ganji:
        return ''
    if len(ganji) == 2:
        return STEMS_H2H.get(ganji[0], ganji[0]) + BRANCHES_H2H.get(ganji[1], ganji[1])
    return ''.join(STEMS_H2H.get(ch, BRANCHES_H2H.get(ch, ch)) for ch in ganji)

# Frases e hanja dos 10 Mestres do Dia (troncos celestes) — cobertura completa,
# não é fallback: todo mapa tem exatamente um destes 10.
FRASES_MESTRE = {
    # Versão completa (pedido de revisão do Ivã, D19) - a página-respiro
    # (page_breath_mestre) mostra a frase inteira, não mais o fragmento
    # curto; o " — " é intencional: o layout já divide a frase em duas
    # linhas centralizadas quando encontra esse separador.
    'Gap': 'O carvalho não pede licença para crescer — cresce reto, porque essa é a sua natureza.',
    'Eul': 'A hera encontra caminho onde não há porta — flexível por fora, decidida por dentro.',
    'Byeong': 'O sol não escolhe o que iluminar — ilumina tudo, generoso e constante.',
    'Jeong': 'A vela não compete com o sol — ela acende o que está perto.',
    'Mu': 'A montanha é firme, mas ama como montanha — não se move por pressão.',
    'Gi': 'O jardim não tem pressa — cada estação chega na hora certa.',
    'Gyeong': 'A espada se faz no fogo que ela não escolheu — e sai mais afiada por isso.',
    'Sin': 'A joia é pequena porque é preciosa — não precisa de tamanho para valer.',
    'Im': 'O rio não discute com a pedra — contorna, e chega ao mar do mesmo jeito.',
    'Gye': 'O orvalho chega em silêncio e alimenta tudo — sem pedir para ser visto.',
}
HANJA_MESTRE = {'Gap':'甲','Eul':'乙','Byeong':'丙','Jeong':'丁','Mu':'戊','Gi':'己','Gyeong':'庚','Sin':'辛','Im':'壬','Gye':'癸'}

# Ciclo decorativo de hanja para o topo de cada capítulo narrativo (ritmo visual,
# D10 — não carrega significado literal por seção, já que os títulos são do LLM).
HANJA_CYCLE = ['心','道','風','影','靜','光','源','念','望','悟','境','和','業','情']

DISCLAIMER_DEFAULT = [
    "Este relatório é uma ferramenta de autoconhecimento baseada na tradição coreana do Saju.",
    "Ele não substitui acompanhamento médico ou psicológico,",
    "e nenhum mapa decide por você: o caminho é sempre seu.",
]

# ----------------------------------------------------------------------------
# Helpers gerais
# ----------------------------------------------------------------------------

_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\U0001F1E6-\U0001F1FF"
    "\U0000FE0F"
    "]", flags=re.UNICODE)

def _strip_emoji(text: str) -> str:
    """Remove emoji que nenhuma das fontes (Display/Body/Sans/CJK) sabe
    desenhar — sem isso viram caixinhas vazias no PDF."""
    return _EMOJI_RE.sub('', text)

def is_cjk(ch: str) -> bool:
    cp = ord(ch)
    return (0x2E80 <= cp <= 0x9FFF or 0xF900 <= cp <= 0xFAFF or
            0x3000 <= cp <= 0x30FF or 0xFF00 <= cp <= 0xFFEF or
            0x1100 <= cp <= 0x11FF or 0x3130 <= cp <= 0x318F or
            0xAC00 <= cp <= 0xD7A3)  # jamo + hangul syllables (termos coreanos em prosa)

def draw_bg(c: canvas.Canvas) -> None:
    c.setFillColor(IVORY); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

def draw_footer(c: canvas.Canvas, chapter: str, page: int) -> None:
    y = 44
    c.setFillColor(MUTED); c.setFont("Sans-It", 7.5)
    c.drawString(MARGIN_X, y, chapter)
    c.setFont("Sans", 7.5)
    c.drawCentredString(PAGE_W/2, y, f"— {page:02d} —")
    c.drawRightString(PAGE_W - MARGIN_X, y, "BITNA SAJU")

def draw_hanja_glyph(c: canvas.Canvas, ch: str, x: float, y: float, size: float, color=ACCENT) -> None:
    if not CJK or not ch:
        return
    c.setFillColor(color); c.setFont(CJK, size)
    c.drawCentredString(x, y, ch)

def draw_top_hanja(c: canvas.Canvas, ch: str) -> None:
    draw_hanja_glyph(c, ch, PAGE_W/2, PAGE_H - 60, 12, ACCENT)

_ROMAN = [(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
def to_roman(n: int) -> str:
    n = max(1, n); res = ''
    for v, sym in _ROMAN:
        while n >= v:
            res += sym; n -= v
    return res or 'I'

def split_title(heading: str):
    """Quebra um título livre em (parte-regular, parte-itálica) — mimetiza o
    estilo bitonal original sem depender de curadoria manual por seção."""
    heading = (heading or '').strip()
    words = heading.split(' ')
    if len(words) <= 1:
        return heading, ''
    cut = max(1, round(len(words) * 0.55))
    return ' '.join(words[:cut]) + ' ', ' '.join(words[cut:])

_STOPWORDS = {'o','a','os','as','de','do','da','dos','das','seu','sua','seus','suas','um','uma'}
def derive_label(heading: str, avoid: set | None = None) -> str:
    """Extrai a palavra-rótulo do título do capítulo (pro cabeçalho/rodapé
    'V · ABERTURA'). `avoid` evita repetir um rótulo já usado por outra
    página - os títulos que o prompt do LLM manda escrever (ex: 'Abertura
    pessoal', 'A estrutura do seu mapa', 'Síntese final') colidem de propósito
    em tema com as páginas fixas (I Abertura, III Estrutura, Síntese final) e
    sem essa checagem o rodapé mostrava o mesmo rótulo duas vezes no livro."""
    words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]+", heading or '') if w.lower() not in _STOPWORDS]
    if not words:
        return 'leitura'
    avoid = {a.lower() for a in (avoid or ())}
    for w in words:
        if w.lower() not in avoid:
            return w
    return words[0]

def draw_chapter_header(c: canvas.Canvas, roman: str, label: str, title_main: str, title_italic: str, subtitle: str | None = None) -> None:
    x = MARGIN_X
    y = PAGE_H - 140
    c.setFillColor(MUTED); c.setFont("Sans", 8)
    c.drawString(x, y, f"{roman}  ·  {(label or '').upper()}")
    c.setStrokeColor(ACCENT); c.setLineWidth(0.8)
    c.line(x, y - 8, x + 60, y - 8)
    y2 = y - 60
    max_w = PAGE_W - 2*MARGIN_X
    main = title_main if (not title_italic or title_main.endswith(' ')) else title_main + ' '
    size = 30
    while size > 16:
        tw = pdfmetrics.stringWidth(main, "Display", size) + pdfmetrics.stringWidth(title_italic, "Display-It", size)
        if tw <= max_w:
            break
        size -= 2
    tw = pdfmetrics.stringWidth(main, "Display", size) + pdfmetrics.stringWidth(title_italic, "Display-It", size)
    if tw <= max_w:
        c.setFillColor(INK); c.setFont("Display", size)
        tw1 = pdfmetrics.stringWidth(main, "Display", size)
        c.drawString(x, y2, main)
        c.setFont("Display-It", size)
        c.drawString(x + tw1, y2, title_italic)
        sub_y = y2 - 24
    else:
        # título longo demais mesmo no tamanho mínimo — cai para duas linhas
        # (título encolhe, mas nunca vaza a margem, tarefa 1c)
        size2 = 22
        while size2 > 12 and (pdfmetrics.stringWidth(main.strip(), "Display", size2) > max_w or
                              pdfmetrics.stringWidth(title_italic, "Display-It", size2) > max_w):
            size2 -= 2
        c.setFillColor(INK); c.setFont("Display", size2)
        c.drawString(x, y2, main.strip())
        c.setFont("Display-It", size2)
        c.drawString(x, y2 - size2 - 4, title_italic)
        sub_y = y2 - size2 - 4 - 22
    if subtitle:
        c.setFillColor(MUTED); c.setFont("Body-It", 11)
        c.drawString(x, sub_y, _fit_line(subtitle, "Body-It", 11, max_w))

# --- Texto estilizado com fallback CJK-aware ---------------------------------
# Tokens de estilo: **negrito**, *itálico*; detecta hanja e troca de fonte.

_TOKEN_RE = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")

def _split_style(text: str):
    for part in _TOKEN_RE.split(text):
        if not part: continue
        if part.startswith("**") and part.endswith("**"):
            yield part[2:-2], "b"
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            yield part[1:-1], "i"
        else:
            yield part, ""

def _font_for(style: str, base_family: str) -> str:
    if style == "i":
        return base_family + "-It"
    return base_family

def _atoms(text: str, style: str, base_family: str):
    curr = []; curr_cjk = None
    latin_font = _font_for(style, base_family)
    for ch in text:
        cjk = is_cjk(ch) and bool(CJK)
        if curr_cjk is None:
            curr_cjk = cjk
        if cjk != curr_cjk:
            yield "".join(curr), (CJK if curr_cjk else latin_font), style
            curr = []; curr_cjk = cjk
        curr.append(ch)
    if curr:
        yield "".join(curr), (CJK if curr_cjk else latin_font), style

def _measure(atoms, size):
    return sum(pdfmetrics.stringWidth(text, font, size) for text, font, _ in atoms)

def _fit_line(text, font, size, max_w):
    """Trunca uma linha (sem quebrar) pra caber em max_w, com reticências -
    usado em legendas de cartão de largura fixa (ver page_archetypes), onde
    truncar por caractere fixo quebrava com o bump de fonte (D17)."""
    if pdfmetrics.stringWidth(text, font, size) <= max_w:
        return text
    t = text
    while t and pdfmetrics.stringWidth(t + '…', font, size) > max_w:
        t = t[:-1]
    return (t.rstrip() + '…') if t else text

def _wrap_lines(text: str, w: float, size: float, base_family: str):
    text = _strip_emoji(text)
    styled_words = []
    for seg, style in _split_style(text):
        parts = re.split(r"(\s+)", seg)
        for p in parts:
            if not p: continue
            atoms = list(_atoms(p, style, base_family))
            styled_words.append((atoms, style, p.isspace()))
    lines = []; line = []; line_w = 0
    for atoms, style, is_space in styled_words:
        aw = _measure(atoms, size)
        if not line and is_space:
            continue
        if line_w + aw > w and line:
            while line and line[-1][2]:
                line_w -= _measure(line[-1][0], size); line.pop()
            if line: lines.append(line)
            line = []; line_w = 0
            if is_space: continue
        line.append((atoms, style, is_space)); line_w += aw
    if line:
        while line and line[-1][2]: line.pop()
        if line: lines.append(line)
    return lines

def _draw_lines(c, lines, x, y, size, leading, color, align):
    for ln in lines:
        line_width = sum(_measure(a, size) for a, s, sp in ln)
        if align == "center": cx = x + (max(0, PAGE_W) and 0)  # placeholder, replaced below
        cx = x
        if align == "center":
            cx = x + 0  # width param not known here; caller pre-centers via w
        for atoms, style, _sp in ln:
            for atext, afont, astyle in atoms:
                c.setFont(afont, size); c.setFillColor(color)
                c.drawString(cx, y, atext)
                aw = pdfmetrics.stringWidth(atext, afont, size)
                if astyle == "b":
                    c.drawString(cx + 0.35, y, atext)
                cx += aw
        y -= leading
    return y

def draw_wrapped(c, text, x, y, w, size=10.5, leading=15, base_family="Body", color=BODY, align="left"):
    leading = leading + FONT_BUMP
    lines = _wrap_lines(text, w, size, base_family)
    for ln in lines:
        line_width = sum(_measure(a, size) for a, s, sp in ln)
        if align == "center": cx = x + (w - line_width)/2
        elif align == "right": cx = x + w - line_width
        else: cx = x
        for atoms, style, _sp in ln:
            for atext, afont, astyle in atoms:
                c.setFont(afont, size); c.setFillColor(color)
                c.drawString(cx, y, atext)
                aw = pdfmetrics.stringWidth(atext, afont, size)
                if astyle == "b": c.drawString(cx + 0.35, y, atext)
                cx += aw
        y -= leading
    return y

def draw_wrapped_paginated(c, text, x, y, w, min_y, new_page_fn, size=10.5, leading=15, base_family="Body", color=BODY):
    """Como draw_wrapped, mas quebra a página NO MEIO do parágrafo se preciso —
    é o que garante que o layout aguenta textos de qualquer tamanho (tarefa 1c)."""
    leading = leading + FONT_BUMP
    lines = _wrap_lines(text, w, size, base_family)
    i = 0
    while i < len(lines):
        if y - leading < min_y:
            y = new_page_fn()
        avail = max(1, int((y - min_y) / leading))
        chunk = lines[i:i+avail]
        for ln in chunk:
            cx = x
            for atoms, style, _sp in ln:
                for atext, afont, astyle in atoms:
                    c.setFont(afont, size); c.setFillColor(color)
                    c.drawString(cx, y, atext)
                    aw = pdfmetrics.stringWidth(atext, afont, size)
                    if astyle == "b": c.drawString(cx + 0.35, y, atext)
                    cx += aw
            y -= leading
        i += len(chunk)
    return y

# ----------------------------------------------------------------------------
# Pequenos motivos vetoriais (traço fino, D9 — proibido galáxia/mandala/cristal)
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
    c.line(cx, cy, cx, cy + s*1.6)
    for i in range(3):
        yy = cy + s*0.4*(i+1)
        c.line(cx - 4, yy, cx + 4, yy)
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
        p = c.beginPath(); p.moveTo(cx - s, yy)
        seg = 2*s/6; x = cx - s
        for k in range(6):
            x0 = cx - s + k*seg; x1 = x0 + seg
            p.curveTo(x0 + s/12, yy + 3, x1 - s/12, yy + 3, x1, yy)
        c.drawPath(p, stroke=1, fill=0)

def motif_seal(c, cx, cy, ch="四柱", size=10):
    r = 10
    c.setFillColor(ACCENT); c.setStrokeColor(ACCENT)
    c.rect(cx - r, cy - r, 2*r, 2*r, fill=1, stroke=0)
    if CJK:
        c.setFillColor(IVORY); c.setFont(CJK, size)
        if len(ch) >= 2:
            c.drawCentredString(cx, cy + 1.5, ch[0])
            c.drawCentredString(cx, cy - 8, ch[1])
        else:
            c.drawCentredString(cx, cy - size/3, ch)
    else:
        c.setFillColor(IVORY); c.setFont('Display-Bold' if False else 'Display', size*0.9)
        c.drawCentredString(cx, cy - size*0.3, 'SB')

def hairline(c, x1, y1, x2, y2, color=HAIRLINE, w=0.5):
    c.setStrokeColor(color); c.setLineWidth(w); c.line(x1, y1, x2, y2)

def centered_ornament(c, cx, cy, color=ACCENT):
    c.setStrokeColor(color); c.setLineWidth(0.6)
    c.line(cx - 22, cy, cx - 6, cy)
    c.line(cx + 6, cy, cx + 22, cy)
    c.setFillColor(color); c.circle(cx, cy, 1.0, fill=1, stroke=0)

MOTIF_ELEM = {'Madeira': motif_bamboo, 'Terra': motif_mountain, 'Água': motif_wave,
              'Fogo': motif_mountain, 'Metal': motif_wave}

# ----------------------------------------------------------------------------
# Icones de traco fino - elementos (usados no quadro de animais) e os 12
# animais dos ramos (pedido de revisao do Iva: trocar hanja por icones aqui).
# ----------------------------------------------------------------------------

def icon_gota(c, cx, cy, s=16, color=None):
    color = color or COL_AGUA
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    p = c.beginPath()
    p.moveTo(cx, cy + s)
    p.curveTo(cx + s*0.75, cy + s*0.1, cx + s*0.55, cy - s*0.75, cx, cy - s*0.75)
    p.curveTo(cx - s*0.55, cy - s*0.75, cx - s*0.75, cy + s*0.1, cx, cy + s)
    c.drawPath(p, stroke=1, fill=0)

def icon_chama(c, cx, cy, s=16, color=None):
    color = color or COL_FOGO
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    p = c.beginPath()
    p.moveTo(cx, cy - s)
    p.curveTo(cx + s*0.9, cy - s*0.2, cx + s*0.5, cy + s*0.5, cx, cy + s)
    p.curveTo(cx - s*0.5, cy + s*0.5, cx - s*0.35, cy + s*0.05, cx - s*0.15, cy - s*0.05)
    p.curveTo(cx - s*0.3, cy + s*0.25, cx, cy + s*0.15, cx, cy - s)
    c.drawPath(p, stroke=1, fill=0)

def icon_folha(c, cx, cy, s=16, color=None):
    color = color or COL_MADEIRA
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    p = c.beginPath()
    p.moveTo(cx, cy - s)
    p.curveTo(cx + s*0.9, cy - s*0.6, cx + s*0.9, cy + s*0.6, cx, cy + s)
    p.curveTo(cx - s*0.9, cy + s*0.6, cx - s*0.9, cy - s*0.6, cx, cy - s)
    c.drawPath(p, stroke=1, fill=0)
    c.line(cx, cy - s*0.8, cx, cy + s*0.8)

def icon_moeda(c, cx, cy, s=16, color=None):
    color = color or COL_METAL
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy, s*0.85, stroke=1, fill=0)
    q = s*0.28
    c.rect(cx - q, cy - q, 2*q, 2*q, stroke=1, fill=0)

def _icon_terra(c, cx, cy, s=16, color=None):
    motif_mountain(c, cx, cy - s*0.3, s*0.9, color or COL_TERRA)

ELEM_ICON = {'Água': icon_gota, 'Fogo': icon_chama, 'Madeira': icon_folha,
             'Terra': _icon_terra, 'Metal': icon_moeda}

# ----------------------------------------------------------------------------
# Icones raster (Gemini) - traco fino ornamentado, gerados como mascaras
# alpha-only (RGB=0, sem cor propria) em assets/icons/. Sao tingidos em tempo
# de execucao na cor do elemento do ramo (mesma logica que ja colore os
# icones vetoriais acima), entao um unico arquivo por animal/elemento serve
# para qualquer combinacao de cor. Se o arquivo nao existir (ou Pillow nao
# estiver instalado), cai de volta pros icones vetoriais desenhados a mao.
try:
    from PIL import Image as _PILImage
    _PIL_OK = True
except Exception:
    _PIL_OK = False

ANIMAL_ICON_FILES = {
    'Rato': 'animal_rato', 'Boi': 'animal_boi', 'Tigre': 'animal_tigre',
    'Coelho': 'animal_coelho', 'Dragão': 'animal_dragao', 'Serpente': 'animal_serpente',
    'Cavalo': 'animal_cavalo', 'Cabra': 'animal_cabra', 'Macaco': 'animal_macaco',
    'Galo': 'animal_galo', 'Cão': 'animal_cao', 'Porco': 'animal_porco',
}
ELEM_ICON_FILES = {
    'Água': 'elem_agua', 'Fogo': 'elem_fogo', 'Madeira': 'elem_madeira',
    'Terra': 'elem_terra', 'Metal': 'elem_metal',
}

@lru_cache(maxsize=256)
def _tinted_icon_reader(mask_name: str, hexcolor: str):
    """Carrega assets/icons/<mask_name>.png (mascara alpha-only) e devolve um
    ImageReader tingido na cor pedida, cacheado por (arquivo, cor) - evita
    reprocessar a mesma combinacao varias vezes no mesmo PDF."""
    if not _PIL_OK:
        return None
    path = os.path.join(ICON_DIR, f"{mask_name}.png")
    if not os.path.exists(path):
        return None
    try:
        mask = _PILImage.open(path).convert("RGBA")
        hexcolor = hexcolor.lstrip('#')
        r, g, b = int(hexcolor[0:2], 16), int(hexcolor[2:4], 16), int(hexcolor[4:6], 16)
        solid = _PILImage.new("RGBA", mask.size, (r, g, b, 0))
        solid.putalpha(mask.split()[3])
        buf = BytesIO()
        solid.save(buf, format="PNG")
        buf.seek(0)
        return ImageReader(buf)
    except Exception:
        return None

def draw_icon_png(c, mask_name, cx, cy, w, hexcolor):
    """Desenha um icone raster centralizado em (cx, cy) com largura w pt,
    preservando a proporcao original. Retorna True se desenhou, False se
    precisa cair pro fallback vetorial."""
    reader = _tinted_icon_reader(mask_name, hexcolor)
    if reader is None:
        return False
    iw, ih = reader.getSize()
    h = w * ih / iw
    c.drawImage(reader, cx - w/2, cy - h/2, width=w, height=h, mask='auto')
    return True

def icon_rato(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.ellipse(cx - s*0.8, cy - s*0.5, cx + s*0.5, cy + s*0.5, stroke=1, fill=0)
    c.circle(cx - s*0.55, cy + s*0.35, s*0.22, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx + s*0.5, cy)
    p.curveTo(cx + s*1.1, cy + s*0.3, cx + s*1.3, cy - s*0.2, cx + s*1.4, cy - s*0.5)
    c.drawPath(p, stroke=1, fill=0)

def icon_boi(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.ellipse(cx - s*0.55, cy - s*0.6, cx + s*0.55, cy + s*0.35, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx - s*0.5, cy + s*0.2)
    p.curveTo(cx - s*0.9, cy + s*0.5, cx - s*0.9, cy + s*0.9, cx - s*0.5, cy + s*0.85)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx + s*0.5, cy + s*0.2)
    p.curveTo(cx + s*0.9, cy + s*0.5, cx + s*0.9, cy + s*0.9, cx + s*0.5, cy + s*0.85)
    c.drawPath(p, stroke=1, fill=0)

def icon_tigre(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy, s*0.6, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx - s*0.45, cy + s*0.45); p.lineTo(cx - s*0.65, cy + s*0.95); p.lineTo(cx - s*0.15, cy + s*0.65)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx + s*0.45, cy + s*0.45); p.lineTo(cx + s*0.65, cy + s*0.95); p.lineTo(cx + s*0.15, cy + s*0.65)
    c.drawPath(p, stroke=1, fill=0)
    for dx in (-0.2, 0, 0.22):
        c.line(cx + s*dx - 3, cy - s*0.15, cx + s*dx + 3, cy - s*0.35)

def icon_coelho(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy - s*0.25, s*0.5, stroke=1, fill=0)
    c.ellipse(cx - s*0.35, cy + s*0.1, cx - s*0.1, cy + s*1.0, stroke=1, fill=0)
    c.ellipse(cx + s*0.1, cy + s*0.1, cx + s*0.35, cy + s*1.0, stroke=1, fill=0)

def icon_dragao(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0)
    p = c.beginPath()
    p.moveTo(cx - s*0.9, cy - s*0.5)
    p.curveTo(cx - s*0.3, cy + s*0.6, cx + s*0.3, cy - s*0.6, cx + s*0.9, cy + s*0.5)
    c.drawPath(p, stroke=1, fill=0)
    c.line(cx - s*0.9, cy - s*0.5, cx - s*1.05, cy - s*0.85)
    c.line(cx - s*0.9, cy - s*0.5, cx - s*0.65, cy - s*0.85)

def icon_serpente(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.1)
    p = c.beginPath()
    p.moveTo(cx - s*0.7, cy + s*0.5)
    p.curveTo(cx - s*0.1, cy + s*0.9, cx - s*0.1, cy + s*0.1, cx + s*0.4, cy)
    p.curveTo(cx + s*0.8, cy - s*0.08, cx + s*0.8, cy - s*0.6, cx + s*0.5, cy - s*0.75)
    c.drawPath(p, stroke=1, fill=0)

def icon_cavalo(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    p = c.beginPath()
    p.moveTo(cx - s*0.3, cy - s*0.8)
    p.curveTo(cx - s*0.55, cy - s*0.2, cx - s*0.5, cy + s*0.5, cx - s*0.15, cy + s*0.9)
    p.lineTo(cx + s*0.15, cy + s*0.9)
    p.curveTo(cx + s*0.35, cy + s*0.4, cx + s*0.5, cy, cx + s*0.35, cy - s*0.7)
    p.lineTo(cx - s*0.3, cy - s*0.8)
    c.drawPath(p, stroke=1, fill=0)
    for dx, dy in [(0.05, 0.75), (0.15, 0.55), (0.22, 0.35)]:
        c.line(cx + s*dx, cy + s*dy, cx + s*(dx+0.3), cy + s*(dy+0.1))

def icon_cabra(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.ellipse(cx - s*0.4, cy - s*0.5, cx + s*0.4, cy + s*0.3, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx - s*0.3, cy + s*0.2)
    p.curveTo(cx - s*0.7, cy + s*0.4, cx - s*0.8, cy + s*0.9, cx - s*0.55, cy + s)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx + s*0.3, cy + s*0.2)
    p.curveTo(cx + s*0.7, cy + s*0.4, cx + s*0.8, cy + s*0.9, cx + s*0.55, cy + s)
    c.drawPath(p, stroke=1, fill=0)

def icon_macaco(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy, s*0.55, stroke=1, fill=0)
    c.circle(cx - s*0.55, cy + s*0.25, s*0.2, stroke=1, fill=0)
    c.circle(cx + s*0.55, cy + s*0.25, s*0.2, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx + s*0.4, cy - s*0.4)
    p.curveTo(cx + s*0.9, cy - s*0.7, cx + s*1.0, cy - s*1.2, cx + s*0.7, cy - s*1.3)
    c.drawPath(p, stroke=1, fill=0)

def icon_galo(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy - s*0.1, s*0.45, stroke=1, fill=0)
    for dx in (-0.15, 0.05, 0.25):
        c.line(cx + s*dx, cy + s*0.3, cx + s*(dx-0.05), cy + s*0.65)
    p = c.beginPath(); p.moveTo(cx + s*0.4, cy - s*0.15); p.lineTo(cx + s*0.75, cy - s*0.05); p.lineTo(cx + s*0.4, cy + s*0.05)
    c.drawPath(p, stroke=1, fill=0)

def icon_cao(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy, s*0.5, stroke=1, fill=0)
    c.ellipse(cx - s*0.75, cy - s*0.1, cx - s*0.35, cy + s*0.6, stroke=1, fill=0)
    c.ellipse(cx + s*0.35, cy - s*0.1, cx + s*0.75, cy + s*0.6, stroke=1, fill=0)

def icon_porco(c, cx, cy, s=16, color=INK):
    c.setStrokeColor(color); c.setLineWidth(1.0); c.setFillColor(IVORY)
    c.circle(cx, cy, s*0.55, stroke=1, fill=0)
    c.ellipse(cx - s*0.22, cy - s*0.5, cx + s*0.22, cy - s*0.2, stroke=1, fill=0)
    c.circle(cx - s*0.1, cy - s*0.35, 1.3, stroke=0, fill=1)
    c.circle(cx + s*0.1, cy - s*0.35, 1.3, stroke=0, fill=1)
    p = c.beginPath(); p.moveTo(cx - s*0.4, cy + s*0.45); p.lineTo(cx - s*0.55, cy + s*0.75); p.lineTo(cx - s*0.2, cy + s*0.55)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(cx + s*0.4, cy + s*0.45); p.lineTo(cx + s*0.55, cy + s*0.75); p.lineTo(cx + s*0.2, cy + s*0.55)
    c.drawPath(p, stroke=1, fill=0)

ANIMAL_ICONS = {
    'Rato': icon_rato, 'Boi': icon_boi, 'Tigre': icon_tigre, 'Coelho': icon_coelho,
    'Dragão': icon_dragao, 'Serpente': icon_serpente, 'Cavalo': icon_cavalo,
    'Cabra': icon_cabra, 'Macaco': icon_macaco, 'Galo': icon_galo, 'Cão': icon_cao,
    'Porco': icon_porco,
}

# Os dez arquetipos (dez deuses / 十神) - enumeracao fixa e completa (nao vem
# do LLM: sao exatamente 10 possiveis, igual FRASES_MESTRE). Portado do
# gerador v4 (app/pdf/gerar_pdf.py), que ja tinha esse quadro - o v5 original
# nao tinha (pedido de revisao do Iva).
ARQUETIPOS = [
    ('RELAÇÕES DE IGUAL', [
        ('Companheiro', '比肩', 'autonomia e irmandade', 'você funciona como referência solitária'),
        ('Rival', '劫財', 'ousadia e competição', 'competição não te move')]),
    ('EXPRESSÃO CRIATIVA', [
        ('Deus do Alimento', '食神', 'criação serena e prazer', 'sua criação nasce de outra fonte'),
        ('Oficial Ferido', '傷官', 'o olhar que vê o que está errado — e como melhorar', 'a crítica não é seu motor')]),
    ('GERAÇÃO DE VALOR', [
        ('Riqueza Indireta', '偏財', 'o caçador de oportunidades', 'oportunidade não é seu chamado natural'),
        ('Riqueza Direta', '正財', 'renda estável e gestão', 'salário fixo não é seu caminho natural')]),
    ('ORDEM E AUTORIDADE', [
        ('Oficial Direto', '正官', 'ordem e responsabilidade', 'hierarquia não tem morada no seu mapa'),
        ('Oficial Indireto (Sete Matanças)', '偏官', 'coragem sob pressão', 'pressão externa não te comanda')]),
    ('SABER E AMPARO', [
        ('Selo Direto', '正印', 'o amparo do conhecimento', 'seu saber vem da experiência'),
        ('Selo Indireto', '偏印', 'intuição e caminhos alternativos', 'sua intuição atua discreta')]),
]

def pontos_intensidade(c, x, y, nivel, r=4.4, cor=ACCENT):
    c.setFillColor(cor); c.setStrokeColor(cor); c.setLineWidth(0.8)
    if nivel >= 2:
        c.circle(x, y, r, stroke=0, fill=1); c.circle(x + 2*r + 4, y, r, stroke=0, fill=1); return
    if nivel >= 1:
        c.circle(x, y, r, stroke=0, fill=1); return
    c.circle(x, y, r, stroke=1, fill=0)
    c.wedge(x - r, y - r, x + r, y + r, 90, 180, stroke=0, fill=1)

def _draw_mixed_line(c, x, y, text, base_font, size, color):
    """Desenha uma linha (sem quebra) misturando latim e hanja, retorna a largura."""
    text = _strip_emoji(text)
    cx = x
    for t, f, _s in _atoms(text, '', base_font):
        c.setFont(f, size); c.setFillColor(color); c.drawString(cx, y, t)
        cx += pdfmetrics.stringWidth(t, f, size)
    return cx - x

def _split_main_right(value: str):
    """'Mu, a Montanha (Terra Yang) - guardiao leal...' -> (main, descritor).
    O relatorio do LLM ja separa valor e descricao com '.' ou '-' (ver
    relatorios/prompts/leitura_premium.md, secao Resumo de bolso)."""
    for sep in (' · ', ' — '):
        if sep in value:
            i = value.index(sep)
            return value[:i].strip(), value[i + len(sep):].strip()
    return value.strip(), ''

# ----------------------------------------------------------------------------
# Leitura de dados / helpers de domínio
# ----------------------------------------------------------------------------

def mestre_chave(l: dict):
    m = (l.get('mestreDoDia') or '').split(' ')[0]
    return m if m in HANJA_MESTRE else None

def elemento_do_mestre(l: dict):
    m = l.get('mestreDoDia') or ''
    for e in ELEM_ORDER:
        if e in m: return e
    return None

def _pilar_parts(p):
    if not p:
        return None
    tronco = p.get('tronco') or ''
    ramo = p.get('ramo') or ''
    th = re.search(r'\((.+?)\)', tronco)
    rh = re.search(r'\((.+?)\)', ramo)
    top_ch = th.group(1) if th else ''
    bot_ch = rh.group(1) if rh else ''
    # "Tronco/Ramo" em vez de "Tronco do Ano/Ramo do Ano" - o cabeçalho da
    # coluna (ANO/MÊS/DIA/HORA) já diz de qual pilar se trata; repetir
    # deixava a legenda comprida demais pra caber nas 4 colunas.
    l1 = ('Tronco · ' + tronco.split('— ')[-1]) if tronco else ''
    l2 = ('Ramo · ' + ramo.split('— ')[-1]) if ramo else ''
    return top_ch, bot_ch, l1, l2

def animal_do_ramo(p):
    if not p:
        return None
    ramo = p.get('ramo') or ''
    tail = ramo.split('— ')[-1] if '— ' in ramo else ''
    animal = tail.split(',')[0].strip()
    return animal or None

def elemento_do_ramo(p):
    if not p:
        return None
    ramo = p.get('ramo') or ''
    tail = ramo.split('— ')[-1] if '— ' in ramo else ''
    parts = tail.split(',')
    if len(parts) > 1:
        e = parts[1].strip()
        return e if e in ELEM_ORDER else None
    return None

def elemento_do_tronco(p):
    """Formato do tronco é 'Jeong (丁) — Fogo Yin' (sem vírgula, diferente do
    ramo) - usado na página de estrutura/elementos (D19)."""
    if not p:
        return None
    tronco = p.get('tronco') or ''
    tail = tronco.split('— ')[-1] if '— ' in tronco else ''
    e = tail.split(' ')[0].strip()
    return e if e in ELEM_ORDER else None
# ----------------------------------------------------------------------------
# Parsing do relatório (markdown do LLM) em capítulos + resumo de bolso
# ----------------------------------------------------------------------------

def _split_paragraphs(body: str):
    body = body or ''
    paras = re.split(r'\n\s*\n', body.strip())
    return [p.strip() for p in paras if p.strip()]

def _split_md_sections(md: str):
    """Retorna lista ordenada de {level, heading, body} — level 0 = preâmbulo
    (texto antes do primeiro ##)."""
    lines = md.replace('\r\n', '\n').split('\n')
    sections = []
    cur = {'level': 0, 'heading': None, 'body_lines': []}
    for ln in lines:
        s = ln.strip()
        m3 = re.match(r'^###\s+(.*)$', s)
        m2 = re.match(r'^##\s+(.*)$', s) if not m3 else None
        m1 = re.match(r'^#\s+(.*)$', s) if not (m3 or m2) else None
        if m3:
            sections.append(cur); cur = {'level': 3, 'heading': m3.group(1).strip(), 'body_lines': []}
        elif m2:
            sections.append(cur); cur = {'level': 2, 'heading': m2.group(1).strip(), 'body_lines': []}
        elif m1:
            continue  # título de topo / H1 — não vira capítulo
        else:
            if s.startswith('>'):
                continue  # citação de demonstração — não faz parte do relatório real
            cur['body_lines'].append(ln)
    sections.append(cur)
    out = []
    for s in sections:
        body = '\n'.join(s['body_lines'])
        body = re.sub(r'^\s*-{3,}\s*$', '', body, flags=re.M).strip()
        out.append({'level': s['level'], 'heading': s['heading'], 'body': body})
    return out

def _classify_chapter(heading_lower: str):
    """Capítulos que ganham uma página de dados/gráfico própria ANTES da
    prosa (pedido de revisão: 'para ele entender precisa desse gráfico
    antes' — visão do todo antes do ponto a ponto)."""
    if re.search(r'ciclo|década|o mapa do tempo', heading_lower):
        return 'cycles'
    if re.search(r'núcleo|arquétipo|dez deuses|dez arquétipos', heading_lower):
        return 'archetypes'
    if re.search(r'animal|estrela', heading_lower):
        return 'animals'
    if re.search(r'estrutura', heading_lower):
        return 'structure'
    return None

def parse_relatorio(md: str):
    """-> (capitulos, resumo_rows, disclaimer_override)
    capitulos: [{'heading': str|None, 'paragraphs': [str], 'kind': str|None}]
    'kind' ∈ {'cycles','archetypes','animals',None} — dispara a página de
    dados correspondente antes da prosa (ver render_narrative).
    resumo_rows: [(label, valor)] extraído de '### ✦ ... 4 linhas' (ou similar)
    disclaimer_override: str|None (texto de nota final, se presente no relatório)
    """
    if not md or not md.strip():
        return [], [], None
    raw = _split_md_sections(md)
    chapters = []
    resumo_rows = []
    disclaimer = None
    preamble = ''
    for sec in raw:
        heading = sec['heading']; body = sec['body']
        if heading is None:
            preamble = body
            continue
        low = heading.lower()
        if sec['level'] == 3 and re.search(r'resumo|4 linhas|3 linhas|✦', low):
            paras = _split_paragraphs(body)
            if paras:
                for ln in paras[0].split('\n'):
                    m = re.match(r'^\*{0,2}([^*:]+?):\*{0,2}\s*(.+)$', ln.strip())
                    if m:
                        resumo_rows.append((m.group(1).strip(), m.group(2).strip()))
                if len(paras) > 1:
                    disclaimer = '\n\n'.join(paras[1:]).strip()
            continue
        if re.search(r'nota final|disclaimer', low):
            if body.strip():
                disclaimer = body.strip()
            continue
        paras = _split_paragraphs(body)
        if not paras:
            continue
        chapters.append({'heading': heading, 'paragraphs': paras, 'kind': _classify_chapter(low)})
    if preamble:
        if chapters:
            chapters[0]['paragraphs'] = [preamble] + chapters[0]['paragraphs']
        else:
            chapters.append({'heading': None, 'paragraphs': [preamble], 'kind': None})
    return chapters, resumo_rows, disclaimer

# ----------------------------------------------------------------------------
# PÁGINAS
# ----------------------------------------------------------------------------

CONTENT_X = MARGIN_X + 40
CONTENT_W = PAGE_W - 2*MARGIN_X - 80
BODY_BOTTOM = 92

def page_cover(c, dados):
    draw_bg(c)
    l = dados.get('leitura') or {}
    nome = dados.get('nome') or ''
    nasc = l.get('nascimento') or {}
    produto = dados.get('produto', 'premium')
    c.setStrokeColor(HAIRLINE); c.setLineWidth(0.6)
    L_ = 22; m = 46
    for (x, y, dx, dy) in [(m, PAGE_H-m,1,-1), (PAGE_W-m, PAGE_H-m,-1,-1), (m, m,1,1), (PAGE_W-m, m,-1,1)]:
        c.line(x, y, x + dx*L_, y); c.line(x, y, x, y + dy*L_)
    c.setFillColor(MUTED); c.setFont("Sans", 9)
    c.drawCentredString(PAGE_W/2, PAGE_H - 140, "S A J U   B R A S I L")
    hairline(c, PAGE_W/2 - 14, PAGE_H - 154, PAGE_W/2 + 14, PAGE_H - 154, MUTED)
    mk = mestre_chave(l)
    if mk and CJK:
        c.setFillColor(GHOST); c.setFont(CJK, 380)
        c.drawCentredString(PAGE_W/2, PAGE_H - 560, HANJA_MESTRE[mk])
    c.setFillColor(INK); c.setFont("Display", 30)
    if produto == 'premium':
        c.drawCentredString(PAGE_W/2, 260, "Leitura Personalizada")
        c.setFont("Display-It", 30)
        c.drawCentredString(PAGE_W/2, 232, "Premium")
    else:
        c.drawCentredString(PAGE_W/2, 246, "Sua Leitura de Saju")
    c.setFillColor(MUTED); c.setFont("Body-It", 11)
    c.drawCentredString(PAGE_W/2, 212, "um retrato dos seus padrões, pela tradição coreana dos Quatro Pilares")
    if nome:
        max_w_nome = PAGE_W - 2*MARGIN_X - 40
        size_nome = 34
        while size_nome > 16 and pdfmetrics.stringWidth(nome, "Display", size_nome) > max_w_nome:
            size_nome -= 2
        c.setFillColor(INK); c.setFont("Display", size_nome)
        c.drawCentredString(PAGE_W/2, 160, nome)
    data_str = nasc.get('data') or ''
    if data_str and '-' in data_str:
        data_str = '/'.join(reversed(data_str.split('-')))
    hora_str = nasc.get('hora') or ''
    cidade_str = (nasc.get('cidade') or '').upper()
    meta_parts = [p for p in [data_str, (hora_str.upper() if hora_str and hora_str != 'desconhecida' else None), cidade_str or None] if p]
    if meta_parts:
        c.setFillColor(MUTED); c.setFont("Sans", 9)
        c.drawCentredString(PAGE_W/2, 138, "     ·     ".join(meta_parts))
    motif_seal(c, PAGE_W/2, 110, "四柱", 10)
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, 76, "não é sobre prever sua vida — é sobre entender seus padrões para decidir melhor")

_MESES_PT = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho',
             'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

def _data_por_extenso(d=None):
    d = d or date.today()
    return f"{d.day} de {_MESES_PT[d.month - 1]} de {d.year}"

def page_colophon(c, dados):
    draw_bg(c)
    nome = dados.get('nome') or ''
    produto = dados.get('produto', 'premium')
    if CJK:
        c.setFillColor(ACCENT); c.setFont(CJK, 11)
        c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 60, "四 柱")
    c.setFillColor(INK); c.setFont("Display-It", 18)
    c.drawCentredString(PAGE_W/2, PAGE_H/2 + 20, "abra sem pressa.")
    c.drawCentredString(PAGE_W/2, PAGE_H/2 - 6, "este mapa é seu.")
    x = MARGIN_X; y = 160
    max_w = PAGE_W - 2*MARGIN_X
    c.setFillColor(MUTED); c.setFont("Sans", 8)
    linhas = [f"EDIÇÃO {'PREMIUM' if produto == 'premium' else 'ESSENCIAL'} · V.5", "BITNA SAJU"]
    if nome: linhas.append(_fit_line(f"IMPRESSO PARA {nome.upper()}", "Sans", 8, max_w))
    for line in linhas:
        c.drawString(x, y, line); y -= 12
    hairline(c, x, y+4, x+40, y+4, MUTED)
    y -= 12
    c.drawString(x, y, "TIRAGEM ÚNICA")
    y -= 14
    c.setFillColor(MUTED); c.setFont("Sans-It", 8)
    c.drawString(x, y, f"Tiragem única realizada em {_data_por_extenso()}")

def page_intro(c, ctx):
    """Página educativa fixa (não depende do mapa) — 'antes de ler o seu mapa'."""
    draw_bg(c); draw_top_hanja(c, "序")
    draw_chapter_header(c, "I", "Abertura", "Antes de ler", "o seu mapa",
                        "uma tradição de séculos, agora na sua mão")
    x = CONTENT_X; y = PAGE_H - 260; w = CONTENT_W
    p1 = ("Na Coreia, antes de um casamento, de uma sociedade ou de uma grande decisão, é "
          "comum consultar o **Saju** — os quatro pilares. A palavra vem do costume de ler o "
          "destino de uma pessoa a partir de quatro colunas: o ano, o mês, o dia e a hora em "
          "que ela nasceu. Cada pilar carrega dois caracteres; os oito juntos formam um "
          "retrato único — o seu.")
    p2 = ("O Saju não é religião, nem adivinhação. É um sistema de observação refinado por "
          "gerações de estudiosos, que lê o mundo através de **cinco elementos** — Madeira, "
          "Fogo, Terra, Metal e Água — e dos ritmos com que eles se alimentam e se contêm.")
    p3 = ("Não para saber \"o que vai acontecer\" — mas para entender **com que padrões estão "
          "jogando**. É assim que a Bitna Saju trabalha: *não é sobre prever sua vida — é sobre "
          "entender seus padrões para decidir melhor.*")
    y = draw_wrapped(c, p1, x, y, w); y -= 6
    y = draw_wrapped(c, p2, x, y, w); y -= 6
    y = draw_wrapped(c, p3, x, y, w)
    motif_bamboo(c, PAGE_W - MARGIN_X - 20, 160, 36, color=INK)
    draw_footer(c, "i · abertura", ctx['page'])

def page_method(c, ctx):
    draw_bg(c); draw_top_hanja(c, "讀")
    draw_chapter_header(c, "II", "Método", "Como ler", "o seu mapa", "o mapa em camadas")
    items = [
        ("i",   "Os Quatro Pilares", "ano (raízes e herança), mês (vida pública e carreira), dia (eu íntimo e vínculos) e hora (projetos e maturidade)."),
        ("ii",  "O Mestre do Dia",   "o caractere que rege o pilar do dia é o centro de tudo: o \"você essencial\". Todo o restante do mapa é lido em relação a ele."),
        ("iii", "Os Cinco Elementos","a contagem revela seus talentos naturais (o que transborda) e suas habilidades a cultivar (o que falta)."),
        ("iv",  "Os Dez Arquétipos", "dez padrões clássicos que descrevem como cada energia do mapa se relaciona com o seu centro."),
        ("v",   "Os Ciclos de Década","a vida avança em fases de dez anos — o clima de cada década: quando plantar, quando construir, quando colher."),
    ]
    y = PAGE_H - 275
    x_num = MARGIN_X + 60; x_txt = MARGIN_X + 100
    w = PAGE_W - MARGIN_X - x_txt
    for roman, title, desc in items:
        c.setFillColor(ACCENT); c.setFont("Display-It", 16)
        c.drawRightString(x_num, y, roman)
        c.setFillColor(INK); c.setFont("Display", 13)
        c.drawString(x_txt, y, title)
        yy = draw_wrapped(c, desc, x_txt, y - 16, w, size=9.8, leading=13.5, color=BODY)
        y = yy - 10
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    draw_wrapped(c, "Leia sem pressa, de preferência num momento só seu.", x_txt, y - 4, w, size=10, leading=14, base_family="Body", color=MUTED)
    draw_footer(c, "ii · método", ctx['page'])

PILAR_LABELS = [('ano','ANO','raízes · origem'), ('mes','MÊS','carreira · vida pública'),
                ('dia','DIA','eu íntimo · vínculos'), ('hora','HORA','projetos · maturidade')]

def page_pillars(c, dados, ctx):
    draw_bg(c); draw_top_hanja(c, "四")
    l = dados.get('leitura') or {}
    pilares = l.get('pilares') or {}
    cols_defs = [pl for pl in PILAR_LABELS if pl[0] in pilares] or PILAR_LABELS
    n = len(cols_defs)
    numeral_pt = {3: 'Os Três', 4: 'Os Quatro'}.get(n, 'Os')
    draw_chapter_header(c, "III", "Estrutura", numeral_pt, "Pilares",
                        "as energias do momento exato do seu nascimento")
    top_y = PAGE_H - 300
    col_w = (PAGE_W - 2*MARGIN_X) / n
    for i, (chave, label, sub) in enumerate(cols_defs):
        p = pilares.get(chave)
        parts = _pilar_parts(p)
        cx = MARGIN_X + col_w*(i + 0.5)
        c.setFillColor(ACCENT); c.setFont("Sans", 8)
        c.drawCentredString(cx, top_y, label)
        c.setFillColor(MUTED); c.setFont("Body-It", 8.5)
        c.drawCentredString(cx, top_y - 12, sub)
        if parts:
            top_ch, bot_ch, l1, l2 = parts
            if CJK and top_ch:
                c.setFillColor(INK); c.setFont(CJK, 56)
                c.drawCentredString(cx, top_y - 78, top_ch)
            if CJK and bot_ch:
                c.setFont(CJK, 56)
                c.drawCentredString(cx, top_y - 138, bot_ch)
            if i < n - 1:
                x_div = MARGIN_X + col_w*(i+1)
                hairline(c, x_div, top_y - 148, x_div, top_y - 30, HAIRLINE)
            c.setFillColor(ACCENT); c.setLineWidth(0.6)
            c.line(cx - 14, top_y - 168, cx - 4, top_y - 168)
            c.setFillColor(BODY)
            max_w = col_w - 10  # respiro entre colunas - texto varia de tamanho por pilar
            for txt, y_off in ((l1, 180), (l2, 192)):
                fsz = 8.0
                while fsz > 3.5 and pdfmetrics.stringWidth(txt, "Sans", fsz) > max_w:
                    fsz -= 0.5
                c.setFont("Sans", fsz)
                c.drawCentredString(cx, top_y - y_off, txt)
        else:
            c.setFillColor(MUTED); c.setFont("Body-It", 9.5)
            c.drawCentredString(cx, top_y - 100, "hora desconhecida")
    y = 220
    c.setFillColor(BODY); c.setFont("Body-It", 11)
    msg = "Oito caracteres · cinco elementos em jogo." if n == 4 else "Seis caracteres · três pilares (hora desconhecida)."
    c.drawCentredString(PAGE_W/2, y, msg)
    y -= 20
    mk = mestre_chave(l); mestre_txt = l.get('mestreDoDia') or ''
    if mk and CJK and mestre_txt:
        romaniz = mestre_txt.split(' (')[0]
        elemento = mestre_txt.split('— ')[-1] if '— ' in mestre_txt else ''
        parts = [(f"No centro, o seu Mestre do Dia: {romaniz} (", "Body-It"), (HANJA_MESTRE[mk], CJK), (f") — {elemento}.", "Body-It")]
        total = sum(pdfmetrics.stringWidth(t, f, 11) for t, f in parts)
        cx = (PAGE_W - total)/2
        for t, f in parts:
            c.setFont(f, 11); c.setFillColor(BODY); c.drawString(cx, y, t); cx += pdfmetrics.stringWidth(t, f, 11)
    motif_seal(c, PAGE_W/2, 150, "四柱", 9)
    draw_footer(c, "iii · estrutura", ctx['page'])

def page_elements(c, dados, ctx):
    draw_bg(c); draw_top_hanja(c, "五")
    l = dados.get('leitura') or {}
    draw_chapter_header(c, "IV", "Balança", "Os Cinco", "Elementos",
                        "o que transborda são talentos naturais · o que falta, habilidades a cultivar")
    cont = (l.get('elementos') or {}).get('contagem') or {}
    total = sum(cont.values()) or 1
    maxv = max([cont.get(e, 0) for e in ELEM_ORDER] + [0])
    cy = PAGE_H - 470
    step = (PAGE_W - 2*MARGIN_X) / 5
    for i, elem in enumerate(ELEM_ORDER):
        v = cont.get(elem, 0)
        cx = MARGIN_X + step*(i + 0.5)
        col = COR_ELEM[elem]
        r = 22
        dominante = maxv > 0 and v == maxv
        if dominante:
            c.setFillColor(col); c.setStrokeColor(col); c.circle(cx, cy, r, fill=1, stroke=0); c.setFillColor(IVORY)
        else:
            c.setFillColor(IVORY); c.setStrokeColor(col); c.setLineWidth(1.0); c.circle(cx, cy, r, fill=1, stroke=1); c.setFillColor(col)
        if CJK:
            c.setFont(CJK, 18); c.drawCentredString(cx, cy - 6, ELEM_CH[elem])
        c.setFillColor(ACCENT if dominante else MUTED); c.setFont("Sans", 8)
        c.drawCentredString(cx, cy - 40, elem.upper())
        c.setFillColor(col); c.setFont("Display", 22)
        c.drawCentredString(cx, cy - 66, str(v))
        pct = round(100*v/total) if total else 0
        c.setFillColor(MUTED); c.setFont("Sans", 7.5)
        c.drawCentredString(cx, cy - 80, f"{pct}%")
    dom = ', '.join((l.get('elementos') or {}).get('dominantes') or []) or '—'
    fra = ', '.join((l.get('elementos') or {}).get('fracos') or []) or '—'
    centered_ornament(c, PAGE_W/2, cy - 108)
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, cy - 128, f"Dominante: {dom}  ·  Ausente/fraco: {fra}")
    yons = l.get('yongsin') or {}
    if yons.get('elementoPrincipal'):
        c.setFillColor(INK); c.setFont("Display", 15)
        c.drawCentredString(PAGE_W/2, cy - 150, "Seu elemento de equilíbrio")
        c.setFillColor(ACCENT); c.setFont("Display-It", 22)
        extra = f"  (apoio: {yons['elementoSecundario']})" if yons.get('elementoSecundario') else ''
        c.drawCentredString(PAGE_W/2, cy - 176, yons['elementoPrincipal'] + extra)
    draw_footer(c, "iv · balança", ctx['page'])

def page_breath_mestre(c, dados, ctx):
    """Página-respiro com a frase do Mestre do Dia — cobre os 10 troncos possíveis."""
    draw_bg(c)
    l = dados.get('leitura') or {}
    mk = mestre_chave(l)
    frase = FRASES_MESTRE.get(mk, '')
    elem = elemento_do_mestre(l)
    y = PAGE_H/2 + 30
    if elem in MOTIF_ELEM:
        MOTIF_ELEM[elem](c, PAGE_W/2, y + 90, 34, INK)
    c.setFillColor(INK); c.setFont("Display-It", 22)
    partes = frase.split(' — ') if frase else ['']
    if len(partes) == 2:
        c.drawCentredString(PAGE_W/2, y, partes[0] + " —")
        c.drawCentredString(PAGE_W/2, y - 30, partes[1])
    elif frase:
        c.drawCentredString(PAGE_W/2, y, frase)
    if mk:
        c.setFillColor(MUTED); c.setFont("Body-It", 9)
        c.drawCentredString(PAGE_W/2, y - 70, f"{mk.upper()} · MESTRE DO DIA")
    draw_footer(c, "· respiro", ctx['page'])

def draw_running_head(c, roman, label):
    """Cabeçalho leve para a página de PROSA que continua um capítulo cuja
    abertura já foi outra página (gráfico/quadro) — sem repetir o título
    grande, só a etiqueta do capítulo (ver render_narrative)."""
    x = MARGIN_X; y = PAGE_H - 100
    c.setFillColor(MUTED); c.setFont("Sans", 8)
    c.drawString(x, y, f"{roman}  ·  {(label or '').upper()}")
    c.setStrokeColor(ACCENT); c.setLineWidth(0.8)
    c.line(x, y - 8, x + 60, y - 8)

def page_archetypes(c, dados, ctx, roman, label="Núcleo"):
    """Grade dos Dez Arquétipos (dez deuses) — existia no v4, faltava no v5
    (pedido de revisão do Ivã: dar a visão do todo antes do texto)."""
    draw_bg(c); draw_top_hanja(c, "心")
    l = dados.get('leitura') or {}
    nome = dados.get('nome') or ''
    dist = (l.get('dezDeuses') or {}).get('distribuicao') or {}
    draw_chapter_header(c, roman, label, "Os Dez", "Arquétipos",
                        (nome + ' · ' if nome else '') + 'como cada energia se relaciona com o seu centro')
    cw, ch, gapx, gapy = 240, 58, 22, 26
    x0 = (PAGE_W - 2*cw - gapx)/2; y = PAGE_H - 300
    for rotulo, par in ARQUETIPOS:
        c.setFillColor(ACCENT); c.setFont("Sans", 7.5)
        c.drawString(x0 + 2, y + 3, rotulo)
        c.setStrokeColor(HAIRLINE); c.setLineWidth(0.4)
        c.line(x0 + 2 + pdfmetrics.stringWidth(rotulo, "Sans", 7.5) + 8, y + 6, x0 + 2*cw + gapx, y + 6)
        for j, (nomeA, hanja, desc_a, desc_x) in enumerate(par):
            v = dist.get(nomeA, 0)
            x = x0 + j*(cw + gapx); yc = y - ch
            ativo = v > 0
            c.setStrokeColor(INK if ativo else HAIRLINE); c.setLineWidth(0.9 if ativo else 0.5)
            c.roundRect(x, yc, cw, ch, 4, stroke=1, fill=0)
            if v >= 1.5:
                c.setStrokeColor(ACCENT); c.setLineWidth(0.5)
                c.roundRect(x + 3.5, yc + 3.5, cw - 7, ch - 7, 3, stroke=1, fill=0)
            nome_curto = nomeA.replace(' (Sete Matanças)', '')
            txt = f'{nome_curto}  {hanja}'
            larg = _draw_mixed_line(c, x + 14, yc + ch - 21, txt, "Display" if ativo else "Body", 12, INK if ativo else MUTED)
            if ativo:
                pontos_intensidade(c, x + 14 + larg + 14, yc + ch - 16, 2 if v >= 1.5 else (1 if v >= 1 else 0.5))
            c.setFillColor(MUTED if ativo else HexColor('#bdb4a4')); c.setFont("Sans", 7.8)
            pref = 'DOMINANTE — ' if v >= 1.5 else ('presença leve — ' if 0 < v < 1 else ('' if ativo else 'ausente — '))
            desc_full = pref + (desc_a if ativo else desc_x)
            c.drawString(x + 14, yc + 13, _fit_line(desc_full, "Sans", 7.8, cw - 24))
        y -= ch + gapy
    itens = [(2, 'dominante'), (1, 'ativo'), (0.5, 'presença leve')]
    larguras = []
    for nv, rot in itens:
        wdots = (4*4.4 + 4) if nv >= 2 else 2*4.4
        larguras.append(wdots + 9 + pdfmetrics.stringWidth(rot, "Sans", 9))
    sep = 30
    xx = PAGE_W/2 - (sum(larguras) + sep*2)/2
    for (nv, rot), lg in zip(itens, larguras):
        pontos_intensidade(c, xx + 4.4, 90, nv, r=4.4)
        wdots = (4*4.4 + 4) if nv >= 2 else 2*4.4
        c.setFillColor(MUTED); c.setFont("Sans", 9)
        c.drawString(xx + wdots + 9, 86, rot)
        xx += lg + sep
    c.setFillColor(MUTED); c.setFont("Body-It", 9.5)
    c.drawCentredString(PAGE_W/2, 62, 'claro = ausente — e cada ausência também conta a sua história')
    draw_footer(c, f"{roman.lower()} · {label.lower()}", ctx['page'])

def page_structure_elements(c, dados, ctx, roman, label="Mapa"):
    """Página híbrida entre 'Os Quatro Pilares' (grade de colunas por pilar)
    e 'Seus Animais' (ícones raster grandes) - mas com foco nos elementos de
    cada caractere: elemento do tronco em cima, elemento do ramo embaixo.
    Abre o capítulo 'A estrutura do seu mapa' do LLM com uma visão do todo
    antes da prosa (pedido de revisão do Ivã, D19)."""
    draw_bg(c); draw_top_hanja(c, "構")
    l = dados.get('leitura') or {}
    draw_chapter_header(c, roman, label, "Seus elementos, ", "pilar a pilar",
                        "cada caractere carrega um elemento — a matéria-prima da sua estrutura")
    pilares = l.get('pilares') or {}
    cols_defs = [pl for pl in PILAR_LABELS if pl[0] in pilares] or PILAR_LABELS
    n = len(cols_defs)
    top_y = PAGE_H - 300
    col_w = (PAGE_W - 2*MARGIN_X) / n
    ICON_SZ = 56
    for i, (chave, plabel, sub) in enumerate(cols_defs):
        p = pilares.get(chave)
        cx = MARGIN_X + col_w*(i + 0.5)
        c.setFillColor(ACCENT); c.setFont("Sans", 8)
        c.drawCentredString(cx, top_y, plabel)
        c.setFillColor(MUTED); c.setFont("Body-It", 8.5)
        c.drawCentredString(cx, top_y - 12, sub)
        elem_t = elemento_do_tronco(p)
        elem_r = elemento_do_ramo(p)
        if elem_t:
            hexcol = HEX_ELEM.get(elem_t, HEX_INK)
            mask = ELEM_ICON_FILES.get(elem_t)
            drawn = draw_icon_png(c, mask, cx, top_y - 72, ICON_SZ, hexcol) if mask else False
            if not drawn:
                icon = ELEM_ICON.get(elem_t)
                if icon:
                    icon(c, cx, top_y - 72, 20, COR_ELEM.get(elem_t, INK))
            c.setFillColor(MUTED); c.setFont("Sans", 8)
            c.drawCentredString(cx, top_y - 114, elem_t.upper())
        if i < n - 1:
            x_div = MARGIN_X + col_w*(i + 1)
            hairline(c, x_div, top_y - 260, x_div, top_y - 30, HAIRLINE)
        if elem_r:
            hexcol = HEX_ELEM.get(elem_r, HEX_INK)
            mask = ELEM_ICON_FILES.get(elem_r)
            drawn = draw_icon_png(c, mask, cx, top_y - 188, ICON_SZ, hexcol) if mask else False
            if not drawn:
                icon = ELEM_ICON.get(elem_r)
                if icon:
                    icon(c, cx, top_y - 188, 20, COR_ELEM.get(elem_r, INK))
            c.setFillColor(MUTED); c.setFont("Sans", 8)
            c.drawCentredString(cx, top_y - 230, elem_r.upper())
    c.setFillColor(BODY); c.setFont("Body-It", 11)
    c.drawCentredString(PAGE_W/2, 150, "Tronco em cima, ramo embaixo — dois elementos por pilar, oito ao todo.")
    motif_seal(c, PAGE_W/2, 100, "四柱", 9)
    draw_footer(c, f"{roman.lower()} · {label.lower()}", ctx['page'])

def page_animals(c, dados, ctx, roman, label="Animais"):
    """Quadro dos animais dos ramos, no mesmo estilo cartão da página de
    Pilares — mas com ícones de traço fino no lugar do hanja (pedido de
    revisão do Ivã: uma gota para Água, um cãozinho para Cão etc.)."""
    draw_bg(c); draw_top_hanja(c, "獸")
    l = dados.get('leitura') or {}
    draw_chapter_header(c, roman, label, "Seus", "Animais",
                        "os animais dos seus ramos — um retrato de temperamento")
    pilares = l.get('pilares') or {}
    cols_defs = [pl for pl in PILAR_LABELS if pl[0] in pilares] or PILAR_LABELS
    n = len(cols_defs)
    top_y = PAGE_H - 300
    col_w = (PAGE_W - 2*MARGIN_X) / n
    ICON_SZ = 62  # animal e elemento no mesmo tamanho, pedido do Ivã
    for i, (chave, plabel, sub) in enumerate(cols_defs):
        p = pilares.get(chave)
        cx = MARGIN_X + col_w*(i + 0.5)
        c.setFillColor(ACCENT); c.setFont("Sans", 8)
        c.drawCentredString(cx, top_y, plabel)
        c.setFillColor(MUTED); c.setFont("Body-It", 8.5)
        c.drawCentredString(cx, top_y - 12, sub)
        animal = animal_do_ramo(p)
        elem = elemento_do_ramo(p)
        col = COR_ELEM.get(elem, INK)
        hexcol = HEX_ELEM.get(elem, HEX_INK)
        drawn = False
        mask_name = ANIMAL_ICON_FILES.get(animal)
        if mask_name:
            drawn = draw_icon_png(c, mask_name, cx, top_y - 78, ICON_SZ, hexcol)
        if not drawn:
            icon_fn = ANIMAL_ICONS.get(animal)
            if icon_fn:
                icon_fn(c, cx, top_y - 78, 28, col)
            elif animal is None:
                c.setFillColor(MUTED); c.setFont("Body-It", 9.5)
                c.drawCentredString(cx, top_y - 90, "hora desconhecida")
        if i < n - 1:
            x_div = MARGIN_X + col_w*(i + 1)
            hairline(c, x_div, top_y - 270, x_div, top_y - 30, HAIRLINE)
        if animal:
            c.setFillColor(INK); c.setFont("Display", 16)
            c.drawCentredString(cx, top_y - 134, animal)
        if elem:
            elem_mask = ELEM_ICON_FILES.get(elem)
            elem_drawn = draw_icon_png(c, elem_mask, cx, top_y - 200, ICON_SZ, hexcol) if elem_mask else False
            if not elem_drawn:
                icon = ELEM_ICON.get(elem)
                if icon:
                    icon(c, cx, top_y - 200, 24, col)
            c.setFillColor(MUTED); c.setFont("Sans", 8)
            c.drawCentredString(cx, top_y - 256, elem.upper())
    c.setFillColor(BODY); c.setFont("Body-It", 11)
    c.drawCentredString(PAGE_W/2, 150, "Cada animal é um temperamento em cena — o elemento do ramo colore o jeito de agir.")
    motif_seal(c, PAGE_W/2, 100, "四柱", 9)
    draw_footer(c, f"{roman.lower()} · {label.lower()}", ctx['page'])

def page_cycles(c, dados, ctx, roman, label="Tempo"):
    draw_bg(c); draw_top_hanja(c, "運")
    l = dados.get('leitura') or {}
    ciclos = l.get('ciclosDeDecada') or []
    idade = dados.get('idadeAproximada')
    draw_chapter_header(c, roman, label, "Seus ciclos ", "de década",
                        "o clima de cada fase — quando plantar, construir, colher")
    x_line = MARGIN_X + 90
    y_top = PAGE_H - 300
    rows = ciclos[:10]
    row_h = 42
    if rows:
        hairline(c, x_line, y_top - row_h*(len(rows)-1) - 8, x_line, y_top + 8, HAIRLINE, 0.6)
    for i, cic in enumerate(rows):
        faixa = cic.get('faixaEtaria') or ''
        nums = [int(n) for n in re.findall(r'\d+', faixa)[:2]]
        atual = idade is not None and len(nums) == 2 and nums[0] <= idade <= nums[1]
        y = y_top - i*row_h
        if atual:
            c.setFillColor(ACCENT); c.setStrokeColor(ACCENT); c.circle(x_line, y, 4, fill=1, stroke=0)
        else:
            c.setFillColor(IVORY); c.setStrokeColor(HAIRLINE); c.setLineWidth(0.8); c.circle(x_line, y, 3.5, fill=1, stroke=1)
        c.setFillColor(ACCENT if atual else INK); c.setFont("Display", 13)
        c.drawString(x_line + 18, y - 4, faixa)
        tronco = (cic.get('tronco') or '').split(' — ')[-1]
        ramo = cic.get('ramo') or ''
        desc = f"{tronco} sobre {ramo}" if tronco else ramo
        desc_font = "Body-It" if atual else "Body"
        # largura disponível pra descrição: reserva espaço pro ganji (canto
        # direito) e, na linha atual, também pro "você está aqui" - com a
        # fonte maior (D17) esses três elementos passaram a colidir sem essa
        # conta, sobretudo quando tronco/ramo do LLM vêm mais longos.
        right_edge = PAGE_W - MARGIN_X
        if CJK and cic.get('ganji'):
            right_edge -= pdfmetrics.stringWidth(ganji_para_hanja(cic['ganji']), CJK, 16) + 14
        if atual:
            right_edge -= pdfmetrics.stringWidth("você está aqui", "Body-It", 9) + 18
        max_desc_w = max(60, right_edge - (x_line + 100))
        c.setFillColor(ACCENT if atual else BODY); c.setFont(desc_font, 9.5)
        c.drawString(x_line + 100, y - 4, _fit_line(desc, desc_font, 9.5, max_desc_w))
        if atual:
            c.setFillColor(ACCENT); c.setFont("Body-It", 9)
            c.drawRightString(PAGE_W - MARGIN_X - 44, y - 4, "você está aqui")
        if CJK and cic.get('ganji'):
            c.setFillColor(ACCENT if atual else INK); c.setFont(CJK, 16)
            c.drawRightString(PAGE_W - MARGIN_X, y, ganji_para_hanja(cic['ganji']))
    y_q = y_top - row_h*max(len(rows), 1) - 20
    c.setFillColor(MUTED); c.setFont("Body-It", 10)
    c.drawCentredString(PAGE_W/2, y_q, '"a percepção de sorte aumenta quando comportamento e contexto estão alinhados."')
    draw_footer(c, f"{roman.lower()} · {label.lower()}", ctx['page'])

def page_synth(c, dados, resumo_rows, ctx, roman):
    draw_bg(c); draw_top_hanja(c, "定")
    l = dados.get('leitura') or {}
    nome = dados.get('nome') or ''
    produto = dados.get('produto', 'premium')
    draw_chapter_header(c, roman, "Síntese", "Seu Saju ", "em poucas linhas",
                        "o mapa condensado, para levar consigo")
    x = CONTENT_X; y = PAGE_H - 290; w = CONTENT_W
    rows = resumo_rows
    if not rows:
        yons = l.get('yongsin') or {}
        dom = ', '.join((l.get('elementos') or {}).get('dominantes') or [])
        mestre = l.get('mestreDoDia') or ''
        idade = dados.get('idadeAproximada')
        ciclo_atual = None
        for cic in (l.get('ciclosDeDecada') or []):
            nums = [int(n) for n in re.findall(r'\d+', cic.get('faixaEtaria', ''))[:2]]
            if idade is not None and len(nums) == 2 and nums[0] <= idade <= nums[1]:
                ciclo_atual = cic.get('faixaEtaria'); break
        rows = []
        if mestre: rows.append(('MESTRE DO DIA', mestre))
        if yons.get('elementoPrincipal'): rows.append(('ELEMENTO DE EQUILÍBRIO', yons['elementoPrincipal']))
        if dom: rows.append(('ELEMENTO DOMINANTE', dom))
        if ciclo_atual: rows.append(('CICLO ATUAL', ciclo_atual))
    for label, value in rows[:5]:
        main, right = _split_main_right(value)
        c.setFillColor(ACCENT); c.setFont("Sans", 7.5)
        c.drawString(x, y, label.upper())
        hairline(c, x, y - 4, x + w, y - 4, HAIRLINE)
        main_w = _draw_mixed_line(c, x, y - 26, main, "Display", 17, INK)
        if right:
            right_w = pdfmetrics.stringWidth(right, "Body-It", 9.5)
            c.setFillColor(MUTED); c.setFont("Body-It", 9.5)
            if x + main_w + 20 + right_w <= x + w:
                # cabe na mesma linha, alinhado à direita (layout original do v5)
                c.drawRightString(x + w, y - 23, right)
                y -= 46
            else:
                # texto do LLM veio mais longo do que o v5 original previa —
                # desce o descritor pra linha de baixo em vez de sobrepor
                y = draw_wrapped(c, right, x, y - 44, w, size=9.5, leading=13, base_family="Body-It", color=MUTED)
                y -= 12
        else:
            y -= 40
    centered_ornament(c, PAGE_W/2, y - 4)
    c.setFillColor(INK); c.setFont("Display-It", 13)
    c.drawCentredString(PAGE_W/2, y - 30, '"quando você entende seu padrão, deixa de reagir')
    c.drawCentredString(PAGE_W/2, y - 52, 'no automático e passa a agir com intenção."')
    motif_seal(c, PAGE_W/2, y - 90, "四柱", 9)
    marca = "BITNA SAJU" + (f"   ·   PARA {nome.upper()}" if nome else "") + f"   ·   EDIÇÃO {'PREMIUM' if produto == 'premium' else 'ESSENCIAL'} V.5   ·   BITNASAJU.COM.BR"
    # nome completo (D19) pode deixar essa linha mais longa que o normal -
    # encolhe a fonte em vez de deixar vazar a margem
    max_marca_w = PAGE_W - 2*MARGIN_X
    marca_size = 8.0
    while marca_size > 6.0 and pdfmetrics.stringWidth(marca, "Sans", marca_size) > max_marca_w:
        marca_size -= 0.5
    c.setFillColor(MUTED); c.setFont("Sans", marca_size)
    c.drawCentredString(PAGE_W/2, y - 150, marca)
    draw_footer(c, f"{roman.lower()} · síntese", ctx['page'])

def page_closing(c, dados, ctx, disclaimer_override=None):
    """Última página — TAREFA 1b: reinclui a frase de reanálise + selo vermelho."""
    draw_bg(c)
    l = dados.get('leitura') or {}
    yons_el = (l.get('yongsin') or {}).get('elementoPrincipal')
    motif_mountain(c, PAGE_W/2 - 20, PAGE_H/2 + 70, 40, INK)
    motif_bamboo(c, PAGE_W/2 + 30, PAGE_H/2 + 60, 30, INK)
    y = PAGE_H/2 - 20
    c.setFillColor(INK); c.setFont("Display-It", 20)
    if yons_el:
        c.drawCentredString(PAGE_W/2, y, f"o seu caminho pede {yons_el.lower()}.")
        c.setFillColor(MUTED); c.setFont("Body-It", 10)
        c.drawCentredString(PAGE_W/2, y - 24, "cultive-o um pouco por dia — e volte a este mapa quando precisar")
        c.drawCentredString(PAGE_W/2, y - 38, "se lembrar de quem você é.")
    else:
        c.drawCentredString(PAGE_W/2, y, "volte a este mapa quando precisar")
        c.setFillColor(MUTED); c.setFont("Body-It", 10)
        c.drawCentredString(PAGE_W/2, y - 24, "se lembrar de quem você é.")
    centered_ornament(c, PAGE_W/2, y - 62)
    c.setFillColor(ACCENT); c.setFont("Body-It", 11)
    c.drawCentredString(PAGE_W/2, y - 90, "recomendamos a reanálise da sua leitura em cerca de um ano.")
    motif_seal(c, PAGE_W/2, y - 128, "四柱", 10)
    y2 = 176
    linhas_disc = None
    if disclaimer_override:
        linhas_disc = [p.strip('* ').strip() for p in _split_paragraphs(disclaimer_override)]
    if not linhas_disc:
        linhas_disc = DISCLAIMER_DEFAULT
    c.setFillColor(MUTED)
    for line in linhas_disc[:4]:
        y2 = draw_wrapped(c, line, MARGIN_X + 40, y2, PAGE_W - 2*MARGIN_X - 80,
                          size=10, leading=15, base_family="Body-It", color=MUTED, align="center")
    c.setFillColor(MUTED); c.setFont("Sans", 7.5)
    c.drawCentredString(PAGE_W/2, 44, f"— {ctx['page']:02d} —")

# ----------------------------------------------------------------------------
# Capítulos narrativos (dinâmicos, a partir de dados['relatorio'])
# ----------------------------------------------------------------------------

_KIND_PAGE = {'cycles': page_cycles, 'archetypes': page_archetypes, 'animals': page_animals,
              'structure': page_structure_elements}

def render_narrative(c, ctx, dados, chapters, emit):
    """Desenha os capítulos do relatório com paginação automática. Retorna o
    próximo índice romano livre (para a página de síntese que vem depois).

    Capítulos com 'kind' (ciclos/arquétipos/animais) ganham a página de
    dados/gráfico ANTES da prosa — mesmo número romano e label, a prosa
    continua como página de continuação (sem repetir o título grande),
    como um capítulo de livro que abre com uma ilustração de página cheia."""
    roman_idx = 5  # I..IV já usados pelas páginas fixas/estruturais
    # rótulos já usados no livro (páginas fixas antes e a Síntese depois) -
    # evita que um capítulo do LLM repita o mesmo rótulo no rodapé/cabeçalho
    used_labels = {'abertura', 'método', 'metodo', 'estrutura', 'balança', 'balanca', 'respiro', 'síntese', 'sintese'}
    for hi, sec in enumerate(chapters):
        roman = to_roman(roman_idx); roman_idx += 1
        heading = sec['heading'] or 'Sua leitura'
        label = derive_label(heading, avoid=used_labels)
        used_labels.add(label.lower())
        chapter_tag = f"{roman.lower()} · {label.lower()}"
        kind = sec.get('kind')

        opener_drawn = False
        page_fn = _KIND_PAGE.get(kind)
        if page_fn:
            page_fn(c, dados, ctx, roman, label)
            emit()
            opener_drawn = True

        draw_bg(c)
        if opener_drawn:
            draw_running_head(c, roman, label)
            y = PAGE_H - 150
        else:
            hanja = HANJA_CYCLE[hi % len(HANJA_CYCLE)]
            draw_top_hanja(c, hanja)
            title_main, title_it = split_title(heading)
            draw_chapter_header(c, roman, label, title_main, title_it)
            y = PAGE_H - 260
        x = CONTENT_X; w = CONTENT_W

        def new_page(_tag=chapter_tag):
            draw_footer(c, _tag, ctx['page'])
            emit()
            draw_bg(c)
            return PAGE_H - 150

        for para in sec['paragraphs']:
            if y - 10.5 < BODY_BOTTOM:
                y = new_page()
            y = draw_wrapped_paginated(c, para, x, y, w, BODY_BOTTOM, new_page)
            y -= 8
        draw_footer(c, chapter_tag, ctx['page'])
        emit()
    return roman_idx

# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------

def gerar(entrada: str, saida: str) -> None:
    with open(entrada, encoding='utf-8') as f:
        dados = json.load(f)
    dados['leitura'] = dados.get('leitura') or {}
    relatorio_md = dados.get('relatorio') or ''
    nome = dados.get('nome') or ''
    produto = dados.get('produto', 'premium')

    c = canvas.Canvas(saida, pagesize=A4)
    c.setTitle(('Leitura Premium — ' if produto == 'premium' else 'Leitura de Saju — ') + (nome or 'Bitna Saju'))
    c.setAuthor('Bitna Saju')

    ctx = {'page': 1}
    def emit():
        c.showPage(); ctx['page'] += 1

    page_cover(c, dados); emit()
    page_colophon(c, dados); emit()
    page_intro(c, ctx); emit()
    page_method(c, ctx); emit()
    page_pillars(c, dados, ctx); emit()
    page_elements(c, dados, ctx); emit()
    if mestre_chave(dados['leitura']):
        page_breath_mestre(c, dados, ctx); emit()

    chapters, resumo_rows, disclaimer = parse_relatorio(relatorio_md)
    next_idx = 5
    if chapters:
        next_idx = render_narrative(c, ctx, dados, chapters, emit)

    page_synth(c, dados, resumo_rows, ctx, to_roman(next_idx)); emit()
    page_closing(c, dados, ctx, disclaimer); emit()

    c.save()
    print(f'ok: {saida} ({ctx["page"] - 1} páginas)')

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        gerar(sys.argv[1], sys.argv[2])
    else:
        print('Uso: python build_pdf.py entrada.json saida.pdf', file=sys.stderr)
        sys.exit(1)
