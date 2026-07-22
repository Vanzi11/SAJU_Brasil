#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bitna Saju — Gerador de PDF · Direção de arte v2 "Livraria de Seul"
Paleta: marfim, lavanda suave, roxo profundo, dourado, cinza quente + selo vermelho.
Uso: python3 gerar_pdf.py entrada.json saida.pdf
"""
import sys, json, io, re, os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

W, H = A4
MARFIM   = HexColor('#f7f3ea')   # cream do Premium (não usado aqui — Essencial é fundo branco)
MARFIM2  = HexColor('#f2ede1')
BRANCO   = HexColor('#fdfcf9')   # fundo da Edição Essencial — diferencia do cream ornamentado do Premium
ROXO     = HexColor('#242a46')   # navy profundo — identidade própria da Essencial (Premium é roxo/plum)
ROXO_MED = HexColor('#49527a')
LAVANDA  = HexColor('#aab3cf')
DOURADO  = HexColor('#a8894a')
DOURADO2 = HexColor('#c4aa6e')
CINZA    = HexColor('#6e6459')   # cinza quente
TXT      = HexColor('#22242f')
SELO     = HexColor('#a63a2b')   # vermelho de carimbo (não usado na capa da Essencial)
COR_ELEM = {'Madeira': HexColor('#647d5c'), 'Fogo': HexColor('#a35c4b'),
            'Terra': HexColor('#b19458'), 'Metal': HexColor('#847f79'), 'Água': HexColor('#5b7186')}

CJK_FONT = None
for cand, idx in [
    ('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', None),
    ('C:/Windows/Fonts/malgun.ttf', None),
    ('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc', 0),
    ('/System/Library/Fonts/PingFang.ttc', 0),
]:
    if os.path.exists(cand):
        try:
            pdfmetrics.registerFont(TTFont('CJK', cand) if idx is None else TTFont('CJK', cand, subfontIndex=idx))
            CJK_FONT = 'CJK'; break
        except Exception:
            pass

HANGUL_HANJA = {
    '갑':'甲','을':'乙','병':'丙','정':'丁','무':'戊','기':'己','경':'庚','신':'辛','임':'壬','계':'癸',
    '자':'子','축':'丑','인':'寅','묘':'卯','진':'辰','사':'巳','오':'午','미':'未','유':'酉','술':'戌','해':'亥',
}
def hangul_para_hanja(t):
    return ''.join(HANGUL_HANJA.get(ch, ch) for ch in t)

CJK_RE = re.compile(r'[ᄀ-ᇿ　-ヿ㄰-㆏一-鿿가-힯]')

def limpar_cjk(t):
    t = CJK_RE.sub('', t)
    return re.sub(r'\(\s*\)', '', t).replace('  ', ' ').strip()

def _runs(texto):
    runs, cur, cjk = [], '', None
    for ch in texto:
        e = bool(CJK_RE.match(ch))
        if cjk is None or e == cjk: cur += ch; cjk = e
        else: runs.append((cjk, cur)); cur, cjk = ch, e
    if cur: runs.append((cjk, cur))
    return runs

def draw_misto(c, x, y, texto, fonte, tam, align='l'):
    texto = hangul_para_hanja(texto)
    if CJK_FONT is None: texto = limpar_cjk(texto)
    runs = _runs(texto)
    def wd(e, t): return pdfmetrics.stringWidth(t, CJK_FONT if (e and CJK_FONT) else fonte, tam)
    total = sum(wd(e, t) for e, t in runs)
    if align == 'c': x -= total/2
    elif align == 'r': x -= total
    for e, t in runs:
        f = CJK_FONT if (e and CJK_FONT) else fonte
        c.setFont(f, tam); c.drawString(x, y, t)
        x += wd(e, t)
    return total

# ---------- elementos de identidade ----------
def fundo(c, cor=BRANCO):
    c.setFillColor(cor); c.rect(0, 0, W, H, stroke=0, fill=1)

def moldura(c):
    """Edição Essencial: sem moldura ornamentada de propósito — o branco da página
    já é o que diferencia do cream com cantos dourados do Premium (pedido do Ivã, item 3)."""
    pass

def rastreado(t):
    """Letter-spacing manual pra rótulos pequenos em caixa-alta (o reportlab não faz tracking nativo)."""
    return ' '.join(list(t))

def quebrar_linhas(texto, fonte, tam, max_w, max_linhas=None):
    palavras = texto.split(' ')
    linhas, atual = [], ''
    for p in palavras:
        teste = (atual + ' ' + p).strip()
        if pdfmetrics.stringWidth(teste, fonte, tam) <= max_w or not atual:
            atual = teste
        else:
            linhas.append(atual); atual = p
    if atual: linhas.append(atual)
    return linhas[:max_linhas] if max_linhas else linhas

def marca_hanja(c, x, y, texto='四柱', tam=15, cor=None, align='l'):
    """Marca discreta em hanja — substitui o carimbo vermelho na capa/encerramento da Essencial."""
    if not CJK_FONT: return
    c.setFillColor(cor or DOURADO); c.setFont(CJK_FONT, tam)
    w = pdfmetrics.stringWidth(texto, CJK_FONT, tam)
    xx = x - w if align == 'r' else (x - w/2 if align == 'c' else x)
    c.drawString(xx, y, texto)

def selo(c, cx, cy, lado=38, texto='四柱'):
    """Carimbo vermelho tradicional (dojang)."""
    c.setFillColor(SELO)
    c.roundRect(cx-lado/2, cy-lado/2, lado, lado, 4, stroke=0, fill=1)
    c.setStrokeColor(MARFIM); c.setLineWidth(0.6)
    c.roundRect(cx-lado/2+2.5, cy-lado/2+2.5, lado-5, lado-5, 3, stroke=1, fill=0)
    c.setFillColor(MARFIM)
    if CJK_FONT:
        c.setFont(CJK_FONT, lado*0.44)
        c.drawCentredString(cx, cy+lado*0.05, texto[0])
        if len(texto) > 1: c.drawCentredString(cx, cy-lado*0.42, texto[1])
    else:
        c.setFont('Times-Bold', lado*0.4); c.drawCentredString(cx, cy-lado*0.14, 'SB')

# ---------- ilustrações em traço fino (pintura oriental minimalista) ----------
def _tra(c, cor, lw):
    c.setStrokeColor(cor); c.setLineWidth(lw); c.setFillColor(cor)

def il_montanha(c, cx, cy, esc=1.0, cor=None):
    cor = cor or ROXO_MED
    _tra(c, cor, 1.1)
    p = c.beginPath()
    p.moveTo(cx-90*esc, cy-30*esc)
    p.curveTo(cx-60*esc, cy+10*esc, cx-40*esc, cy+42*esc, cx-18*esc, cy+46*esc)
    p.curveTo(cx-2*esc, cy+48*esc, cx+8*esc, cy+30*esc, cx+22*esc, cy+8*esc)
    c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath()
    p.moveTo(cx-34*esc, cy-30*esc)
    p.curveTo(cx-6*esc, cy+4*esc, cx+16*esc, cy+26*esc, cx+38*esc, cy+22*esc)
    p.curveTo(cx+58*esc, cy+18*esc, cx+74*esc, cy-8*esc, cx+90*esc, cy-30*esc)
    c.drawPath(p, stroke=1, fill=0)
    _tra(c, DOURADO, 0.8)
    c.circle(cx+52*esc, cy+40*esc, 8*esc, stroke=1, fill=0)

def il_bambu(c, cx, cy, esc=1.0, cor=None):
    cor = cor or ROXO_MED
    _tra(c, cor, 1.2)
    for dx, alt in [(-16, 88), (14, 70)]:
        x = cx + dx*esc
        c.line(x, cy-40*esc, x, cy-40*esc + alt*esc)
        for frac in (0.33, 0.66):
            yn = cy-40*esc + alt*esc*frac
            c.line(x-2.5*esc, yn, x+2.5*esc, yn)
    _tra(c, cor, 0.9)
    for (x0, y0, x1, y1) in [(-16, 30, -46, 44), (-16, 12, -40, 2), (14, 22, 42, 34), (14, 4, 38, -8)]:
        p = c.beginPath()
        p.moveTo(cx+x0*esc, cy+y0*esc)
        p.curveTo(cx+(x0+x1)/2*esc, cy+(y0+y1)/2*esc+6*esc, cx+x1*esc, cy+y1*esc, cx+x1*esc, cy+y1*esc)
        c.drawPath(p, stroke=1, fill=0)

def il_ondas(c, cx, cy, esc=1.0, cor=None):
    cor = cor or ROXO_MED
    for fila, (dy, larg) in enumerate([(28, 70), (0, 90), (-28, 60)]):
        _tra(c, cor if fila == 1 else DOURADO, 1.0 if fila == 1 else 0.8)
        x = cx - larg*esc; y = cy + dy*esc
        p = c.beginPath(); p.moveTo(x, y)
        seg = 28*esc
        while x < cx + larg*esc - seg:
            p.curveTo(x+seg*0.3, y+12*esc, x+seg*0.7, y+12*esc, x+seg, y)
            x += seg
        c.drawPath(p, stroke=1, fill=0)

def il_sol(c, cx, cy, esc=1.0, cor=None):
    cor = cor or ROXO_MED
    _tra(c, cor, 1.1)
    c.circle(cx, cy, 30*esc, stroke=1, fill=0)
    _tra(c, DOURADO, 0.9)
    import math
    for ang in range(0, 360, 30):
        a = math.radians(ang)
        c.line(cx+42*esc*math.cos(a), cy+42*esc*math.sin(a), cx+54*esc*math.cos(a), cy+54*esc*math.sin(a))

def il_lua(c, cx, cy, esc=1.0, cor=None):
    cor = cor or ROXO_MED
    _tra(c, cor, 1.1)
    p = c.beginPath()
    p.moveTo(cx+12*esc, cy+40*esc)
    p.curveTo(cx-34*esc, cy+26*esc, cx-34*esc, cy-26*esc, cx+12*esc, cy-40*esc)
    p.curveTo(cx-12*esc, cy-22*esc, cx-12*esc, cy+22*esc, cx+12*esc, cy+40*esc)
    c.drawPath(p, stroke=1, fill=0)
    _tra(c, DOURADO, 0.8)
    for (dx, dy) in [(34, 18), (44, -6), (30, -26)]:
        c.circle(cx+dx*esc, cy+dy*esc, 1.4*esc, stroke=0, fill=1)

IL_ELEM = {'Madeira': il_bambu, 'Fogo': il_sol, 'Terra': il_montanha, 'Metal': il_lua, 'Água': il_ondas}

def elemento_do_mestre(l):
    m = (l.get('mestreDoDia') or '')
    for e in IL_ELEM:
        if e in m: return e
    return None

def linha_dourada(c, y, larg=120):
    c.setStrokeColor(DOURADO); c.setLineWidth(0.7)
    c.line(W/2-larg/2, y, W/2+larg/2, y)
    c.setFillColor(DOURADO); c.circle(W/2, y, 1.6, stroke=0, fill=1)

def cabecalho(c, eyebrow, headline):
    """Estilo editorial da Essencial: rótulo pequeno (categoria) acima, título grande
    em itálico serifado abaixo — inverte o peso visual do Premium (que usa título bold reto)."""
    c.setFillColor(CINZA); c.setFont('Helvetica', 8.5)
    c.drawCentredString(W/2, H-64, 'S A J U   B R A S I L')
    c.setFillColor(DOURADO); c.setFont('Helvetica-Bold', 8.2)
    c.drawCentredString(W/2, H-90, rastreado(eyebrow.upper()))
    linhas = quebrar_linhas(headline, 'Times-Italic', 22, W-220, max_linhas=2)
    c.setFillColor(ROXO); c.setFont('Times-Italic', 22)
    y = H-122
    for ln in linhas:
        c.drawCentredString(W/2, y, ln)
        y -= 27
    linha_dourada(c, y - 3)

FRASES_MESTRE = {
    'Gap': 'O carvalho não pede licença para crescer.',
    'Eul': 'A hera encontra caminho onde não há porta.',
    'Byeong': 'O sol não escolhe o que iluminar.',
    'Jeong': 'A vela não compete com o sol — ela acende o que está perto.',
    'Mu': 'A montanha ama como montanha.',
    'Gi': 'O jardim não tem pressa.',
    'Gyeong': 'A espada se faz no fogo que ela não escolheu.',
    'Sin': 'A joia é pequena porque é preciosa.',
    'Im': 'O rio não discute com a pedra: contorna.',
    'Gye': 'O orvalho chega em silêncio e alimenta tudo.',
}
HANJA_MESTRE = {'Gap':'甲','Eul':'乙','Byeong':'丙','Jeong':'丁','Mu':'戊','Gi':'己','Gyeong':'庚','Sin':'辛','Im':'壬','Gye':'癸'}

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

def pontos_intensidade(c, x, y, nivel, r=3.4, cor=DOURADO):
    c.setFillColor(cor); c.setStrokeColor(cor); c.setLineWidth(0.8)
    if nivel >= 2:
        c.circle(x, y, r, stroke=0, fill=1); c.circle(x+2*r+4, y, r, stroke=0, fill=1); return
    if nivel >= 1:
        c.circle(x, y, r, stroke=0, fill=1); return
    c.circle(x, y, r, stroke=1, fill=0)
    c.wedge(x-r, y-r, x+r, y+r, 90, 180, stroke=0, fill=1)

PAG = {'n': 0}
def numero(c, mostrar=True):
    PAG['n'] += 1
    if mostrar and PAG['n'] > 1:
        c.setFillColor(CINZA); c.setFont('Times-Roman', 9)
        c.drawCentredString(W/2, 36, f"— {PAG['n']} —")

# ---------- páginas ----------
def mestre_chave(l):
    m = (l.get('mestreDoDia') or '').split(' ')[0]
    return m if m in HANJA_MESTRE else None

def pagina_capa(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']; nome = dados.get('nome') or ''
    premium = dados.get('produto') == 'premium'
    c.setFillColor(CINZA); c.setFont('Helvetica', 9.5)
    c.drawCentredString(W/2, H-90, 'S A J U   B R A S I L')
    if not premium:
        marca_hanja(c, W-70, H-95, tam=15, align='r')
    linha_dourada(c, H-104, 60)
    if premium:
        mk = mestre_chave(l)
        if mk and CJK_FONT:
            c.setFillColor(HexColor('#e7e0d0'))
            c.setFont(CJK_FONT, 300)
            c.drawCentredString(W/2, H/2-70, HANJA_MESTRE[mk])
    else:
        c.setFillColor(DOURADO); c.setFont('Helvetica-Bold', 9)
        c.drawCentredString(W/2, H-172, rastreado('EDIÇÃO ESSENCIAL'))
    c.setFillColor(ROXO)
    if premium:
        c.setFont('Times-Bold', 30)
        c.drawCentredString(W/2, H-260, 'Leitura Personalizada Premium')
    else:
        c.setFont('Times-Italic', 30)
        c.drawCentredString(W/2, H-224, 'Leitura Personalizada')
        c.drawCentredString(W/2, H-258, 'Essencial')
    c.setFillColor(CINZA); c.setFont('Times-Italic', 12)
    c.drawCentredString(W/2, H-284, 'um retrato dos seus padrões, pela tradição coreana dos Quatro Pilares')
    if nome:
        c.setFillColor(TXT); c.setFont('Times-Bold', 21)
        c.drawCentredString(W/2, 250, nome)
    n = l['nascimento']
    c.setFillColor(CINZA); c.setFont('Helvetica', 10)
    c.drawCentredString(W/2, 228, f"{'/'.join(reversed(n['data'].split('-')))} às {n['hora']} · {n['cidade']}")
    c.setFillColor(ROXO_MED)
    draw_misto(c, W/2, 200, f"Mestre do Dia · {l.get('mestreDoDia','')}", 'Times-Roman', 12, align='c')
    if premium:
        selo(c, W/2, 140, 34)
    c.setFillColor(CINZA); c.setFont('Times-Italic', 10.5)
    c.drawCentredString(W/2, 92, '"Não é sobre prever sua vida — é sobre entender seus padrões para decidir melhor."')
    numero(c, mostrar=False)
    c.showPage()

def pagina_frase(c, dados):
    """Página-respiro: uma frase só, como livro."""
    l = dados['leitura']; mk = mestre_chave(l)
    if not mk: return
    fundo(c); moldura(c)
    elem = elemento_do_mestre(l)
    if elem:
        IL_ELEM[elem](c, W/2, H/2+130, 1.15)
    frase = FRASES_MESTRE[mk]
    c.setFillColor(ROXO); c.setFont('Times-Italic', 24)
    partes = frase.split(' — ')
    if len(frase) > 42 and ' — ' in frase:
        c.drawCentredString(W/2, H/2-20, partes[0] + ' —')
        c.drawCentredString(W/2, H/2-52, partes[1])
    else:
        c.drawCentredString(W/2, H/2-30, frase)
    linha_dourada(c, H/2-90, 80)
    c.setFillColor(CINZA); c.setFont('Helvetica', 8.5)
    c.drawCentredString(W/2, H/2-112, mk.upper() + ' · ' + ('MESTRE DO DIA'))
    numero(c)
    c.showPage()

def carta_pilar(c, x, y, wc, hc, rotulo, sub, p):
    """Pilar como carta elegante: borda dupla fina, hanja ao centro."""
    c.setStrokeColor(DOURADO2); c.setLineWidth(0.8)
    c.roundRect(x, y, wc, hc, 6, stroke=1, fill=0)
    c.setLineWidth(0.4)
    c.roundRect(x+5, y+5, wc-10, hc-10, 4, stroke=1, fill=0)
    c.setFillColor(ROXO); c.setFont('Helvetica-Bold', 10)
    c.drawCentredString(x+wc/2, y+hc-26, rotulo)
    c.setFillColor(CINZA); c.setFont('Helvetica', 7)
    c.drawCentredString(x+wc/2, y+hc-38, sub.upper())
    if p is None:
        c.setFillColor(CINZA); c.setFont('Times-Italic', 9.5)
        c.drawCentredString(x+wc/2, y+hc/2, 'hora desconhecida')
        return
    tronco_h = re.search(r'\((.)\)', p.get('tronco','')); ramo_h = re.search(r'\((.)\)', p.get('ramo',''))
    if CJK_FONT and tronco_h and ramo_h:
        c.setFillColor(TXT); c.setFont(CJK_FONT, 44)
        c.drawCentredString(x+wc/2, y+hc/2+16, tronco_h.group(1))
        c.drawCentredString(x+wc/2, y+hc/2-38, ramo_h.group(1))
    c.setFillColor(ROXO_MED); c.setFont('Times-Roman', 9.5)
    c.drawCentredString(x+wc/2, y+40, p['tronco'].split(' (')[0] + ' · ' + p['tronco'].split('— ')[-1])
    c.drawCentredString(x+wc/2, y+27, p['ramo'].split(' (')[0] + ' · ' + p['ramo'].split('— ')[-1])

def pagina_pilares(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']
    cabecalho(c, 'Os Quatro Pilares', 'as energias do momento exato do seu nascimento')
    papeis = [('ano','ANO','raízes · origem'), ('mes','MÊS','carreira · vida pública'),
              ('dia','DIA','eu íntimo · vínculos'), ('hora','HORA','projetos · maturidade')]
    wc, hc, gap = 112, 235, 16
    x0 = (W - 4*wc - 3*gap)/2; y0 = H/2 - 90
    for i, (chave, rot, sub) in enumerate(papeis):
        carta_pilar(c, x0 + i*(wc+gap), y0, wc, hc, rot, sub, l['pilares'].get(chave))
    if l.get('horaDesconhecida'):
        c.setFillColor(CINZA); c.setFont('Times-Italic', 9.5)
        c.drawCentredString(W/2, y0-26, 'Sem a hora de nascimento, a leitura é feita pelos três pilares — prática tradicional.')
    c.setFillColor(CINZA); c.setFont('Times-Italic', 10.5)
    c.drawCentredString(W/2, 78, '"Seu mapa mostra tendências de funcionamento, não definições fixas."')
    numero(c)
    c.showPage()

def pagina_elementos(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']; cont = l['elementos']['contagem']
    cabecalho(c, 'Os Cinco Elementos', 'o que transborda são talentos naturais · o que falta, habilidades a cultivar')
    total = sum(cont.values()) or 1
    maxv = max(list(cont.values()) or [1])
    passo = (W - 180) / 4
    cy = H/2 + 30
    for i, elem in enumerate(['Madeira', 'Fogo', 'Terra', 'Metal', 'Água']):
        v = cont.get(elem, 0); cx = 90 + i*passo
        r = 14 + 34 * (v / maxv) if v else 13
        cor = COR_ELEM[elem]
        if v == 0:
            c.setStrokeColor(cor); c.setLineWidth(1); c.setFillColor(MARFIM)
            c.circle(cx, cy, r, stroke=1, fill=0)
        else:
            c.setFillColor(cor); c.circle(cx, cy, r, stroke=0, fill=1)
            c.setStrokeColor(MARFIM2); c.setLineWidth(1.2)
            c.circle(cx, cy, r-4, stroke=1, fill=0)
        c.setFillColor(TXT); c.setFont('Times-Bold', 15)
        c.drawCentredString(cx, cy-r-24, str(v))
        c.setFillColor(cor); c.setFont('Helvetica', 8.5)
        c.drawCentredString(cx, cy-r-38, elem.upper())
        c.setFillColor(CINZA); c.setFont('Helvetica', 7.5)
        c.drawCentredString(cx, cy-r-50, f'{round(100*v/total)}%')
    dom = ', '.join(l['elementos'].get('dominantes') or ['—'])
    fra = ', '.join(l['elementos'].get('fracos') or ['—'])
    c.setFillColor(TXT); c.setFont('Times-Roman', 11.5)
    c.drawCentredString(W/2, 180, f'Dominante: {dom}   ·   Ausente ou fraco: {fra}')
    yons = l.get('yongsin') or {}
    if yons:
        linha_dourada(c, 160, 60)
        c.setFillColor(ROXO); c.setFont('Times-Bold', 12.5)
        c.drawCentredString(W/2, 136, f"Seu elemento de equilíbrio: {yons.get('elementoPrincipal','—')}"
                            + (f"  (apoio: {yons['elementoSecundario']})" if yons.get('elementoSecundario') else ''))
    numero(c)
    c.showPage()

def pagina_arquetipos(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']; nome = dados.get('nome') or ''
    dist = (l.get('dezDeuses') or {}).get('distribuicao', {})
    cabecalho(c, 'Os Dez Arquétipos', (nome + ' · ' if nome else '') + 'como cada energia se relaciona com o seu centro')
    cw, ch, gapx, gapy = 240, 58, 22, 28
    x0 = (W - 2*cw - gapx)/2; y = H - 172
    for rotulo, par in ARQUETIPOS:
        c.setFillColor(DOURADO); c.setFont('Helvetica', 7.5)
        c.drawString(x0+2, y+3, rotulo)
        c.setStrokeColor(DOURADO2); c.setLineWidth(0.4)
        c.line(x0 + 2 + pdfmetrics.stringWidth(rotulo, 'Helvetica', 7.5) + 8, y+6, x0 + 2*cw + gapx, y+6)
        for j, (nomeA, hanja, desc_a, desc_x) in enumerate(par):
            v = dist.get(nomeA, 0)
            x = x0 + j*(cw+gapx); yc = y - ch
            ativo = v > 0
            c.setStrokeColor(ROXO_MED if ativo else HexColor('#d8d0c0')); c.setLineWidth(0.9 if ativo else 0.5)
            c.roundRect(x, yc, cw, ch, 4, stroke=1, fill=0)
            if v >= 1.5:
                c.setStrokeColor(DOURADO); c.setLineWidth(0.5)
                c.roundRect(x+3.5, yc+3.5, cw-7, ch-7, 3, stroke=1, fill=0)
            nome_curto = nomeA.replace(' (Sete Matanças)', '')
            c.setFillColor(ROXO if ativo else HexColor('#a99f90'))
            larg = draw_misto(c, x+14, yc+ch-21, f'{nome_curto}  {hanja}', 'Times-Bold' if ativo else 'Times-Roman', 12)
            if ativo:
                pontos_intensidade(c, x+14+larg+14, yc+ch-16, 2 if v >= 1.5 else (1 if v >= 1 else 0.5), r=4.6)
            c.setFillColor(CINZA if ativo else HexColor('#bdb4a4')); c.setFont('Helvetica', 7.8)
            pref = 'DOMINANTE — ' if v >= 1.5 else ('presença leve — ' if 0 < v < 1 else ('' if ativo else 'ausente — '))
            c.drawString(x+14, yc+13, (pref + (desc_a if ativo else desc_x))[:62])
        y -= ch + gapy
    itens = [(2, 'dominante'), (1, 'ativo'), (0.5, 'presença leve')]
    larguras = []
    for nv, rot in itens:
        wdots = (4*4.4+4) if nv >= 2 else 2*4.4
        larguras.append(wdots + 9 + pdfmetrics.stringWidth(rot, 'Helvetica', 11))
    sep = 30
    x = W/2 - (sum(larguras) + sep*2)/2
    for (nv, rot), lg in zip(itens, larguras):
        pontos_intensidade(c, x+4.4, 86, nv, r=4.4)
        wdots = (4*4.4+4) if nv >= 2 else 2*4.4
        c.setFillColor(CINZA); c.setFont('Helvetica', 11)
        c.drawString(x + wdots + 9, 82, rot)
        x += lg + sep
    c.setFillColor(CINZA); c.setFont('Times-Italic', 11)
    c.drawCentredString(W/2, 62, 'claro = ausente — e cada ausência também conta a sua história')
    numero(c)
    c.showPage()

def pagina_ciclos(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']; ciclos = l.get('ciclosDeDecada') or []
    if not ciclos: return
    idade = dados.get('idadeAproximada')
    cabecalho(c, 'Seus Ciclos de Década', 'o clima de cada fase — quando plantar, construir e colher')
    lx = 120; y = H - 175; alt = 52
    c.setStrokeColor(DOURADO2); c.setLineWidth(0.6)
    c.line(lx, y - alt*min(len(ciclos),10) + 30, lx, y + 6)
    for cic in ciclos[:10]:
        faixa = cic['faixaEtaria']
        nums = [int(n) for n in re.findall(r'\d+', faixa)[:2]]
        atual = idade is not None and len(nums) == 2 and nums[0] <= idade <= nums[1]
        if atual:
            c.setFillColor(SELO); c.circle(lx, y-10, 4.5, stroke=0, fill=1)
        else:
            c.setStrokeColor(DOURADO); c.setLineWidth(0.9); c.setFillColor(MARFIM)
            c.circle(lx, y-10, 3.2, stroke=1, fill=1)
        c.setFillColor(ROXO if atual else TXT)
        c.setFont('Times-Bold' if atual else 'Times-Roman', 12.5 if atual else 11.5)
        c.drawString(lx+24, y-8, faixa)
        c.setFillColor(ROXO_MED if atual else CINZA); c.setFont('Times-Roman', 10.5)
        tronco = cic['tronco'].split(' — ')[-1]
        c.drawString(lx+24, y-24, f"{tronco} sobre {cic['ramo']}")
        if atual:
            c.setFillColor(SELO); c.setFont('Times-Italic', 10)
            c.drawString(lx+250, y-8, 'você está aqui')
        c.setFillColor(DOURADO)
        draw_misto(c, W-110, y-16, cic.get('ganji',''), 'Times-Roman', 12, align='r')
        y -= alt
    c.setFillColor(CINZA); c.setFont('Times-Italic', 10.5)
    c.drawCentredString(W/2, 66, '"A percepção de sorte aumenta quando comportamento e contexto estão alinhados."')
    numero(c)
    c.showPage()

def pagina_card_final(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']; nome = dados.get('nome') or ''
    c.setStrokeColor(DOURADO2); c.setLineWidth(0.7)
    c.roundRect(90, H/2-150, W-180, 300, 6, stroke=1, fill=0)
    c.setLineWidth(0.35); c.roundRect(97, H/2-143, W-194, 286, 5, stroke=1, fill=0)
    selo(c, W/2, H/2+108, 30)
    c.setFillColor(ROXO); c.setFont('Times-Bold', 19)
    c.drawCentredString(W/2, H/2+64, 'Seu Saju em quatro linhas')
    linha_dourada(c, H/2+48, 70)
    linhas = [f"Mestre do Dia · {l.get('mestreDoDia','')}"]
    premium = dados.get('produto') == 'premium'
    pv = l.get('padraoDeVida') or {}
    # nome técnico do padrão de vida (ex.: "Padrão do Deus do Alimento") é jargão —
    # só pode aparecer por nome no Premium; no produto de entrada, usamos a essência em linguagem simples
    if pv and premium:
        linhas.append(f"Padrão de vida · {pv.get('nome','')}")
    elif pv and pv.get('essencia'):
        linhas.append(f"Traço central · {pv['essencia']}")
    yons = l.get('yongsin') or {}
    if yons: linhas.append(f"Elemento de equilíbrio · {yons.get('elementoPrincipal','')}")
    dom = ', '.join(l['elementos'].get('dominantes') or [])
    linhas.append(f"Elemento dominante · {dom}")
    y = H/2 + 14
    for ln in linhas[:4]:
        c.setFillColor(TXT)
        draw_misto(c, W/2, y, ln[:80], 'Times-Roman', 12, align='c'); y -= 28
    if nome:
        c.setFillColor(CINZA); c.setFont('Times-Italic', 10)
        c.drawCentredString(W/2, H/2-118, nome)
    c.setFillColor(DOURADO); c.setFont('Helvetica', 8)
    c.drawCentredString(W/2, H/2-136, 'S A J U B R A S I L . C O M . B R')
    c.setFillColor(CINZA); c.setFont('Helvetica', 7.5)
    c.drawCentredString(W/2, 62, 'Este relatório é uma ferramenta de autoconhecimento baseada na tradição coreana do Saju.')
    c.drawCentredString(W/2, 51, 'Ele não substitui acompanhamento médico ou psicológico, e nenhum mapa decide por você: o caminho é sempre seu.')
    numero(c)
    c.showPage()

CADERNO = [
    ('Antes de ler o seu mapa', 'Uma tradição de séculos, agora na sua mão', [
        'Na Coreia, antes de um casamento, de uma sociedade ou de uma grande decisão, é comum consultar o <b>Saju</b> (四柱) — os "quatro pilares". A palavra vem do costume de ler o destino de uma pessoa a partir de quatro colunas: o ano, o mês, o dia e a hora em que ela nasceu. Cada pilar carrega dois caracteres; os oito juntos formam um retrato único — o seu.',
        'O Saju não é religião, nem adivinhação. É um sistema de observação refinado por gerações de estudiosos, que lê o mundo através de <b>cinco elementos</b> — Madeira, Fogo, Terra, Metal e Água — e dos ritmos com que eles se alimentam e se contêm. Na Coreia de hoje, ele convive naturalmente com a vida moderna: universitárias consultam o Saju antes de escolher carreira, casais antes do casamento, empreendedores antes de abrir negócios.',
        'Não para saber "o que vai acontecer" — mas para entender <b>com que padrões estão jogando</b>. É assim que a Bitna Saju trabalha: <i>não é sobre prever sua vida — é sobre entender seus padrões para decidir melhor.</i>']),
    ('Como ler o seu mapa', 'O mapa em camadas', [
        '<b>Os Quatro Pilares</b> — ano (suas raízes e herança), mês (sua vida pública e carreira), dia (seu eu íntimo e seus vínculos) e hora (seus projetos e sua maturidade).',
        '<b>O Mestre do Dia</b> — o caractere que rege o seu pilar do dia é o centro de tudo: o "você essencial". Todo o restante do mapa é lido em relação a ele.',
        '<b>Os Cinco Elementos</b> — a contagem revela seus talentos naturais (o que transborda) e suas habilidades a cultivar (o que falta). Não existe mapa perfeito: existe mapa compreendido.',
        '<b>Os Dez Arquétipos</b> — dez padrões clássicos que descrevem como cada energia do mapa se relaciona com o seu centro. Os que acendem — e os que se apagam — desenham seu jeito único de funcionar.',
        '<b>Os Ciclos de Década</b> — a vida avança em fases de dez anos. Elas não determinam o que acontece: indicam o clima de cada década — quando plantar, quando construir, quando colher.',
        'Leia sem pressa, de preferência num momento só seu. Marque o que fizer sentido — e também o que incomodar: costuma ser onde mora o crescimento.'])
]

def paginas_caderno(c, itens=None):
    for titulo, subt, pars in (itens if itens is not None else CADERNO):
        fundo(c); moldura(c)
        cabecalho(c, subt, titulo)
        y = H - 190
        estilo = ParagraphStyle('cad', fontName='Times-Roman', fontSize=11.5, leading=19,
                                textColor=TXT, alignment=TA_JUSTIFY)
        for ptxt in pars:
            if CJK_FONT: ptxt = CJK_RE.sub(lambda m: f'<font name="CJK">{m.group(0)}</font>', ptxt)
            else: ptxt = limpar_cjk(ptxt)
            p = Paragraph(ptxt, estilo)
            wp, hp = p.wrap(W-220, 600)
            p.drawOn(c, 110, y-hp)
            y -= hp + 16
        numero(c)
        c.showPage()

def md_para_flowables(md_texto):
    estilos = {
        'h2': ParagraphStyle('h2', fontName='Times-Bold', fontSize=16.5, leading=21, textColor=ROXO,
                             spaceBefore=22, spaceAfter=8, alignment=TA_CENTER),
        'h3': ParagraphStyle('h3', fontName='Times-Bold', fontSize=13, leading=17, textColor=ROXO_MED,
                             spaceBefore=14, spaceAfter=5),
        'p': ParagraphStyle('p', fontName='Times-Roman', fontSize=11.3, leading=18.5, textColor=TXT,
                            alignment=TA_JUSTIFY, spaceAfter=9),
    }
    def inline(t):
        t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)
        if CJK_FONT: t = CJK_RE.sub(lambda m: f'<font name="CJK">{m.group(0)}</font>', t)
        else: t = limpar_cjk(t)
        return t
    flow = []
    for b in re.split(r'\n\s*\n', md_texto.strip()):
        b = b.strip()
        if not b or b.startswith('> '): continue
        if b.startswith('---'):
            flow.append(HRFlowable(width=90, color=DOURADO, thickness=0.6, spaceBefore=14, spaceAfter=14, hAlign='CENTER')); continue
        if b.startswith('### '): flow.append(Paragraph(inline(b[4:]), estilos['h3'])); continue
        if b.startswith('## '): flow.append(Paragraph(inline(b[3:]), estilos['h2'])); continue
        if b.startswith('# '): continue
        for ln in b.split('\n'):
            ln = ln.strip()
            if not ln: continue
            if ln.startswith('### '): flow.append(Paragraph(inline(ln[4:]), estilos['h3']))
            elif ln.startswith('## '): flow.append(Paragraph(inline(ln[3:]), estilos['h2']))
            elif ln.startswith('- ') or ln.startswith('* '):
                flow.append(Paragraph('—&nbsp;&nbsp;' + inline(ln[2:]), estilos['p']))
            else:
                flow.append(Paragraph(inline(ln), estilos['p']))
    return flow

def extrair_secoes_especiais(md):
    """Separa Síntese (+ resumo de bolso aninhado) e Nota final do corpo corrido —
    a Essencial dá página própria pra cada uma (pedido do Ivã, item 4), em vez de
    deixá-las fluindo junto com o resto do texto no meio da paginação dinâmica."""
    blocos = re.split(r'(?m)^##\s+', md.strip())
    preamb, blocos = blocos[0], blocos[1:]
    corpo, sintese_txt, resumo_pares, nota_txt = [], '', [], ''
    for b in blocos:
        partes_titulo = b.split('\n', 1)
        titulo = partes_titulo[0].strip()
        resto = partes_titulo[1] if len(partes_titulo) > 1 else ''
        tl = titulo.lower()
        if 'sintese' in tl or 'síntese' in tl:
            sub = re.split(r'(?m)^###\s+', resto)
            sintese_txt = sub[0].strip()
            if len(sub) > 1:
                for ln in sub[1].split('\n'):
                    m = re.match(r'\*\*(.+?):\*\*\s*(.+)', ln.strip())
                    if m: resumo_pares.append((m.group(1).strip(), m.group(2).strip()))
        elif 'resumo' in tl or 'bolso' in tl or '4 linhas' in tl or 'poucas linhas' in tl:
            for ln in resto.split('\n'):
                m = re.match(r'\*\*(.+?):\*\*\s*(.+)', ln.strip())
                if m: resumo_pares.append((m.group(1).strip(), m.group(2).strip()))
        elif 'nota final' in tl or 'disclaimer' in tl or tl == 'nota':
            nota_txt = resto.strip()
        else:
            corpo.append('## ' + b)
    corpo_md = (preamb + '\n\n' if preamb.strip() else '') + '\n\n'.join(corpo)
    return corpo_md, sintese_txt, resumo_pares, nota_txt

def linha_editorial(c, x, y, largura, label, valor, tam_label=8.2, tam_valor=12.5):
    """Uma linha rótulo-pequeno / valor-itálico com friso fino embaixo — o novo visual
    do resumo final (pedido do Ivã, item 5: 'tá muito simples')."""
    c.setFillColor(DOURADO); c.setFont('Helvetica-Bold', tam_label)
    c.drawString(x, y, rastreado(label.upper()))
    linhas = quebrar_linhas(valor, 'Times-Italic', tam_valor, largura)
    c.setFillColor(ROXO); c.setFont('Times-Italic', tam_valor)
    yy = y - 18
    for ln in linhas:
        c.drawString(x, yy, ln)
        yy -= tam_valor + 5
    c.setStrokeColor(HexColor('#e3ddcd')); c.setLineWidth(0.5)
    c.line(x, yy - 3, x + largura, yy - 3)
    return yy - 24

def pdf_texto(md_texto, nome):
    buf = io.BytesIO()
    def fundo_pg(canv, doc):
        canv.saveState()
        fundo(canv); moldura(canv)
        canv.setFillColor(CINZA); canv.setFont('Helvetica', 7.5)
        canv.drawCentredString(W/2, 50, ('S A J U   B R A S I L' + ('   ·   ' + nome if nome else '')))
        canv.setFillColor(CINZA); canv.setFont('Times-Roman', 9)
        canv.drawCentredString(W/2, 36, f"— {PAG['n'] + doc.page} —")
        canv.restoreState()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=95, rightMargin=95, topMargin=80, bottomMargin=70)
    frame = Frame(95, 70, W-190, H-150, id='corpo')
    doc.addPageTemplates([PageTemplate(id='texto', frames=[frame], onPage=fundo_pg)])
    doc.build(md_para_flowables(md_texto))
    buf.seek(0)
    return buf

def pagina_contemplativa(c, dados):
    fundo(c); moldura(c)
    l = dados['leitura']
    yons = (l.get('yongsin') or {}).get('elementoPrincipal')
    elem = yons if yons in IL_ELEM else elemento_do_mestre(l)
    if elem:
        IL_ELEM[elem](c, W/2, H/2+60, 1.3)
    c.setFillColor(ROXO); c.setFont('Times-Italic', 17)
    if yons:
        c.drawCentredString(W/2, H/2-60, f'O seu caminho pede {yons}.')
        c.setFillColor(CINZA); c.setFont('Times-Italic', 11.5)
        c.drawCentredString(W/2, H/2-86, 'Cultive-o um pouco por dia — e volte a este mapa quando precisar se lembrar de quem você é.')
    else:
        c.drawCentredString(W/2, H/2-60, 'Volte a este mapa quando precisar se lembrar de quem você é.')
    c.setFillColor(ROXO_MED); c.setFont('Times-Italic', 11.5)
    c.drawCentredString(W/2, H/2-114, 'Recomendamos a reanálise da sua leitura em cerca de um ano.')
    linha_dourada(c, H/2-140, 70)
    selo(c, W/2, H/2-184, 32)
    numero(c)
    c.showPage()

def pagina_sintese(c, dados, texto, resumo_pares):
    """Folha própria pra Síntese + resumo de bolso — separada do corpo corrido (item 4)."""
    fundo(c); moldura(c)
    nome = dados.get('nome') or ''
    c.setFillColor(CINZA); c.setFont('Helvetica', 8.5)
    c.drawCentredString(W/2, H-64, 'S A J U   B R A S I L')
    c.setFillColor(DOURADO); c.setFont('Helvetica-Bold', 8.2)
    c.drawCentredString(W/2, H-90, rastreado('SÍNTESE'))
    c.setFillColor(ROXO); c.setFont('Times-Italic', 22)
    c.drawCentredString(W/2, H-122, 'O que fica, no fim das contas')
    linha_dourada(c, H-138, 60)
    y = H-186
    if texto:
        corpo = texto
        if CJK_FONT: corpo = CJK_RE.sub(lambda m: f'<font name="CJK">{m.group(0)}</font>', corpo)
        else: corpo = limpar_cjk(corpo)
        estilo = ParagraphStyle('sint', fontName='Times-Roman', fontSize=11.8, leading=19.5,
                                textColor=TXT, alignment=TA_JUSTIFY)
        p = Paragraph(corpo, estilo)
        wp, hp = p.wrap(W-220, 380)
        p.drawOn(c, 110, y-hp)
        y -= hp + 42
    if resumo_pares:
        c.setFillColor(DOURADO); c.setFont('Helvetica-Bold', 8)
        c.drawString(110, y, rastreado('✦ SEU SAJU EM POUCAS LINHAS'))
        y -= 28
        for label, valor in resumo_pares[:4]:
            y = linha_editorial(c, 110, y, W-220, label, valor)
    if nome:
        c.setFillColor(CINZA); c.setFont('Times-Italic', 9.5)
        c.drawCentredString(W/2, 56, nome)
    numero(c)
    c.showPage()

def pagina_nota(c, dados, texto):
    """Folha própria pra Nota final — separada da Síntese (item 4)."""
    fundo(c); moldura(c)
    texto = texto or ('Este relatório é uma ferramenta de autoconhecimento baseada na tradição coreana '
                       'do Saju. Ele não substitui acompanhamento médico ou psicológico, e nenhum mapa '
                       'decide por você: o caminho é sempre seu.')
    if CJK_FONT: texto = CJK_RE.sub(lambda m: f'<font name="CJK">{m.group(0)}</font>', texto)
    else: texto = limpar_cjk(texto)
    c.setFillColor(DOURADO); c.setFont('Helvetica-Bold', 8.2)
    c.drawCentredString(W/2, H/2+96, rastreado('NOTA'))
    estilo = ParagraphStyle('nota', fontName='Times-Italic', fontSize=12.5, leading=20.5,
                            textColor=ROXO_MED, alignment=TA_CENTER)
    p = Paragraph(texto, estilo)
    wp, hp = p.wrap(W-280, 300)
    p.drawOn(c, 140, H/2+64-hp)
    numero(c)
    c.showPage()

UPSELL_ITENS = [
    'o bloqueio central do seu mapa — o padrão que mais te trava hoje, nomeado com precisão e cuidado',
    'os dez arquétipos completos do seu mapa, nome técnico e tradução em comportamento',
    'seus animais e suas estrelas (sinsais), cada um com instrução de uso',
    'a jornada inteira pelos ciclos de década — o que passou, o presente em detalhe e o que vem a seguir',
]

def pagina_upsell(c, dados):
    """Fecho com ar de 'quero saber mais': deixa claro que esta é a Essencial e existe
    uma versão mais completa — pedido geral do Ivã, sem tom de venda pesada."""
    fundo(c); moldura(c)
    marca_hanja(c, W/2, H/2+206, tam=20, align='c')
    c.setFillColor(ROXO); c.setFont('Times-Italic', 19)
    c.drawCentredString(W/2, H/2+150, 'Isto foi a Edição Essencial')
    c.drawCentredString(W/2, H/2+122, 'do seu mapa.')
    linha_dourada(c, H/2+100, 60)
    c.setFillColor(TXT); c.setFont('Times-Roman', 10.8)
    c.drawCentredString(W/2, H/2+72, 'A Edição Premium aprofunda cada camada. Ela inclui, entre outras coisas:')
    y = H/2 + 42
    estilo = ParagraphStyle('ups', fontName='Times-Roman', fontSize=10, leading=15, textColor=TXT)
    for item in UPSELL_ITENS:
        p = Paragraph(item, estilo)
        wp, hp = p.wrap(W-300, 60)
        c.setFillColor(DOURADO); c.circle(126, y-4, 1.6, stroke=0, fill=1)
        p.drawOn(c, 140, y-hp)
        y -= hp + 13
    c.setFillColor(ROXO_MED); c.setFont('Times-Italic', 10.5)
    c.drawCentredString(W/2, y-14, 'saiba mais em bitnasaju.com.br')
    numero(c)
    c.showPage()

def gerar(entrada, saida):
    PAG['n'] = 0
    dados = json.load(open(entrada, encoding='utf-8'))
    premium = dados.get('produto') == 'premium'
    nome = dados.get('nome') or ''
    fixo = io.BytesIO()
    c = rl_canvas.Canvas(fixo, pagesize=A4)
    c.setTitle(('Leitura Premium — ' if premium else 'Leitura Essencial — ') + (nome or 'Bitna Saju'))
    pagina_capa(c, dados)
    if premium:
        paginas_caderno(c)
        pagina_frase(c, dados)
    else:
        # "Antes de ler o seu mapa" acompanha toda leitura Essencial, sempre como página 2 (item 2)
        paginas_caderno(c, CADERNO[:1])
    pagina_pilares(c, dados)
    pagina_elementos(c, dados)
    if premium:
        pagina_arquetipos(c, dados)
        pagina_ciclos(c, dados)
    c.save(); fixo.seek(0)
    partes = [PdfReader(fixo)]

    relatorio_md = dados.get('relatorio') or ''
    sintese_txt, resumo_pares, nota_txt = '', [], ''
    if relatorio_md:
        if premium:
            corpo_md = relatorio_md
        else:
            corpo_md, sintese_txt, resumo_pares, nota_txt = extrair_secoes_especiais(relatorio_md)
        parte_texto = PdfReader(pdf_texto(corpo_md, nome))
        partes.append(parte_texto)
        PAG['n'] += len(parte_texto.pages)

    cauda = io.BytesIO()
    c2 = rl_canvas.Canvas(cauda, pagesize=A4)
    if premium:
        pagina_card_final(c2, dados)
        pagina_contemplativa(c2, dados)
    else:
        # Síntese e Nota final em folhas próprias, separadas do corpo corrido (item 4)
        pagina_sintese(c2, dados, sintese_txt, resumo_pares)
        pagina_nota(c2, dados, nota_txt)
        pagina_upsell(c2, dados)
    c2.save(); cauda.seek(0)
    partes.append(PdfReader(cauda))

    w = PdfWriter()
    for parte in partes:
        for pg in parte.pages: w.add_page(pg)
    with open(saida, 'wb') as f: w.write(f)
    print(f'ok: {saida} ({sum(len(p.pages) for p in partes)} páginas)')

if __name__ == '__main__':
    gerar(sys.argv[1], sys.argv[2])
