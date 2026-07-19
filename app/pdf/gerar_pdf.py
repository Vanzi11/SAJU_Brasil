#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SAJU Brasil — Gerador de PDF
Uso: python3 gerar_pdf.py entrada.json saida.pdf
entrada.json: { "produto": "essencial"|"premium", "nome": str|null,
                "leitura": {...}, "relatorio": "markdown"|null }
Dependências: pip install reportlab pypdf
"""
import sys, json, io, re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ---- fonte CJK (hanja/hangul); fallback: remover ideogramas ----
CJK_FONT = None
for cand, idx in [
    ('/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf', None),
    ('C:/Windows/Fonts/malgun.ttf', None),
    ('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc', 0),
    ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 0),
    ('C:/Windows/Fonts/malgun.ttf', None),
    ('C:/Windows/Fonts/msyh.ttc', 0),
    ('/System/Library/Fonts/PingFang.ttc', 0),
]:
    if os.path.exists(cand):
        try:
            pdfmetrics.registerFont(TTFont('CJK', cand) if idx is None else TTFont('CJK', cand, subfontIndex=idx))
            CJK_FONT = 'CJK'
            break
        except Exception:
            pass

CJK_RE = re.compile(r'[\u1100-\u11ff\u3000-\u30ff\u3130-\u318f\u4e00-\u9fff\uac00-\ud7af]')

def limpar_cjk(t):
    t = CJK_RE.sub('', t)
    return re.sub(r'\(\s*\)', '', t).replace('  ', ' ').strip()

def _runs(texto):
    runs, cur, cjk = [], '', None
    for ch in texto:
        e = bool(CJK_RE.match(ch))
        if cjk is None or e == cjk:
            cur += ch; cjk = e
        else:
            runs.append((cjk, cur)); cur, cjk = ch, e
    if cur: runs.append((cjk, cur))
    return runs

def draw_misto(c, x, y, texto, fonte, tam, align='l'):
    """Desenha texto misto latino+CJK; devolve largura total."""
    if CJK_FONT is None:
        texto = limpar_cjk(texto)
    runs = _runs(texto)
    def w(e, t): return pdfmetrics.stringWidth(t, CJK_FONT if (e and CJK_FONT) else fonte, tam)
    total = sum(w(e, t) for e, t in runs)
    if align == 'c': x -= total / 2
    elif align == 'r': x -= total
    for e, t in runs:
        f = CJK_FONT if (e and CJK_FONT) else fonte
        c.setFont(f, tam); c.drawString(x, y, t)
        x += w(e, t)
    return total

def bolinhas(c, x, y, nivel, r=4.2, cor=None):
    """Indicador de intensidade desenhado: 2=dominante, 1=ativo, 0.5=leve."""
    from reportlab.lib.colors import white
    cor = cor or white
    c.setFillColor(cor); c.setStrokeColor(cor); c.setLineWidth(1)
    if nivel >= 2:
        c.circle(x, y, r, stroke=0, fill=1); c.circle(x + 2*r + 3, y, r, stroke=0, fill=1)
        return 4*r + 3
    if nivel >= 1:
        c.circle(x, y, r, stroke=0, fill=1)
        return 2*r
    c.circle(x, y, r, stroke=1, fill=0)
    c.wedge(x-r, y-r, x+r, y+r, 90, 180, stroke=0, fill=1)
    return 2*r

def estrela(c, cx, cy, r, cor):
    c.setFillColor(cor)
    p = c.beginPath()
    pts = [(0,-r),(r*.22,-r*.22),(r,0),(r*.22,r*.22),(0,r),(-r*.22,r*.22),(-r,0),(-r*.22,-r*.22)]
    p.moveTo(cx+pts[0][0], cy+pts[0][1])
    for dx, dy in pts[1:]: p.lineTo(cx+dx, cy+dy)
    p.close(); c.drawPath(p, stroke=0, fill=1)

W, H = A4
ROXO, ROXO2, ROXO3 = HexColor('#5b3a8f'), HexColor('#8a63c9'), HexColor('#9d7fd1')
LILAS, CINZA, TXT = HexColor('#a58cc6'), HexColor('#b0a6c4'), HexColor('#2a2135')
SUB = HexColor('#8a7ba3')
COR_ELEM = {'Madeira': HexColor('#5a9e6f'), 'Fogo': HexColor('#d96c6c'),
            'Terra': HexColor('#c9a24b'), 'Metal': HexColor('#9aa2ad'), 'Água': HexColor('#5b87c5')}
GRAD_TOP, GRAD_MID, GRAD_BOT = (0.992, 0.953, 0.973), (0.969, 0.937, 0.988), (0.933, 0.941, 0.988)

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

def gradiente(c, passos=120):
    faixa = H / passos
    for i in range(passos):
        t = i / passos
        if t < 0.55:
            k = t / 0.55
            cor = tuple(GRAD_TOP[j] + (GRAD_MID[j] - GRAD_TOP[j]) * k for j in range(3))
        else:
            k = (t - 0.55) / 0.45
            cor = tuple(GRAD_MID[j] + (GRAD_BOT[j] - GRAD_MID[j]) * k for j in range(3))
        c.setFillColorRGB(*cor)
        c.rect(0, H - (i + 1) * faixa, W, faixa + 1, stroke=0, fill=1)
    c.setFillColorRGB(0.953, 0.851, 0.918); c.setFillAlpha(0.35)
    c.circle(W - 40, H - 40, 70, stroke=0, fill=1)
    c.circle(45, 40, 85, stroke=0, fill=1)
    c.setFillAlpha(1)

def titulo_pagina(c, texto, sub=None):
    c.setFillColor(ROXO); c.setFont('Times-Bold', 24)
    c.drawCentredString(W/2, H-70, texto)
    if sub:
        c.setFillColor(SUB); c.setFont('Helvetica', 10.5)
        c.drawCentredString(W/2, H-90, sub)

def pagina_capa(c, dados):
    gradiente(c)
    l = dados['leitura']; nome = dados.get('nome') or ''
    premium = dados.get('produto') == 'premium'
    c.setFillColor(ROXO); c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(W/2, H-110, 'S A J U   B R A S I L')
    c.setFillColor(SUB); c.setFont('Helvetica', 9.5)
    c.drawCentredString(W/2, H-126, 'autoconhecimento pela tradição coreana dos Quatro Pilares')
    c.setFillColor(ROXO); c.setFont('Times-Bold', 34)
    c.drawCentredString(W/2, H-320, 'Leitura Personalizada Premium' if premium else 'Sua Leitura de Saju')
    if nome:
        c.setFillColor(TXT); c.setFont('Times-Bold', 22)
        c.drawCentredString(W/2, H-370, nome)
    n = l['nascimento']
    c.setFillColor(SUB); c.setFont('Helvetica', 11)
    c.drawCentredString(W/2, H-395, f"{'/'.join(reversed(n['data'].split('-')))} às {n['hora']} · {n['cidade']}")
    c.setStrokeColor(LILAS); c.setLineWidth(0.8)
    c.line(W/2-90, H-430, W/2+90, H-430)
    c.setFillColor(ROXO2)
    draw_misto(c, W/2, H-470, f"Mestre do Dia: {l.get('mestreDoDia','')}", 'Times-Bold', 16, align='c')
    c.setFillColor(SUB); c.setFont('Times-Italic', 12.5)
    c.drawCentredString(W/2, 120, '"Não é sobre prever sua vida —')
    c.drawCentredString(W/2, 103, 'é sobre entender seus padrões para decidir melhor."')
    c.showPage()

def card(c, x, y, w, h, fill, stroke):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(1)
    c.roundRect(x, y, w, h, 10, stroke=1, fill=1)

def pagina_pilares(c, dados):
    gradiente(c)
    l = dados['leitura']
    titulo_pagina(c, 'Os Quatro Pilares', 'as energias do momento exato do seu nascimento')
    papeis = {'ano': ('ANO', 'raízes · família · origem'), 'mes': ('MÊS', 'carreira · vida pública'),
              'dia': ('DIA', 'eu íntimo · vínculos'), 'hora': ('HORA', 'projetos · maturidade')}
    cw, ch, gap = 240, 130, 20
    x0, y0 = (W - 2*cw - gap)/2, H - 180
    pos = [('ano', x0, y0-ch), ('mes', x0+cw+gap, y0-ch), ('dia', x0, y0-2*ch-gap), ('hora', x0+cw+gap, y0-2*ch-gap)]
    for chave, x, y in pos:
        p = l['pilares'].get(chave)
        rot, sub = papeis[chave]
        if not p:
            card(c, x, y, cw, ch, HexColor('#ffffff'), HexColor('#e6dcf3'))
            c.setFillColor(CINZA); c.setFont('Helvetica-Bold', 11)
            c.drawString(x+16, y+ch-28, rot)
            c.setFont('Helvetica', 10)
            c.drawString(x+16, y+ch-52, 'hora desconhecida — leitura pelos 3 pilares')
            continue
        card(c, x, y, cw, ch, HexColor('#ffffff'), HexColor('#e6dcf3'))
        c.setFillColor(ROXO); c.setFont('Helvetica-Bold', 11)
        c.drawString(x+16, y+ch-26, rot)
        c.setFillColor(LILAS); c.setFont('Helvetica', 8.5)
        c.drawString(x+70, y+ch-26, sub)
        c.setFillColor(TXT)
        draw_misto(c, x+16, y+ch-52, p['tronco'], 'Times-Roman', 12.5)
        draw_misto(c, x+16, y+ch-72, p['ramo'], 'Times-Roman', 12.5)
        c.setFillColor(ROXO2)
        draw_misto(c, x+cw-16, y+18, p.get('ganji',''), 'Times-Bold', 20, align='r')
    if l.get('horaDesconhecida'):
        c.setFillColor(SUB); c.setFont('Helvetica-Oblique', 9.5)
        c.drawCentredString(W/2, y0-2*ch-gap-24, 'Hora de nascimento desconhecida: leitura realizada pelos três pilares — prática tradicional.')
    c.setFillColor(SUB); c.setFont('Times-Italic', 11.5)
    c.drawCentredString(W/2, 70, '"Seu mapa mostra tendências de funcionamento, não definições fixas."')
    c.showPage()

def pagina_elementos(c, dados):
    gradiente(c)
    l = dados['leitura']; cont = l['elementos']['contagem']
    titulo_pagina(c, 'Seus Cinco Elementos', 'o que transborda são talentos naturais · o que falta, habilidades a cultivar')
    total = sum(cont.values()) or 1
    bw, gap = 74, 24
    x0 = (W - 5*bw - 4*gap)/2; base = H/2 - 40; alt_max = 190
    for i, elem in enumerate(['Madeira', 'Fogo', 'Terra', 'Metal', 'Água']):
        v = cont.get(elem, 0); x = x0 + i*(bw+gap)
        h = max(10, alt_max * v / max(cont.values() or [1]))
        c.setFillColor(COR_ELEM[elem]); c.setFillAlpha(0.25 if v == 0 else 1)
        c.roundRect(x, base, bw, h, 8, stroke=0, fill=1); c.setFillAlpha(1)
        c.setFillColor(TXT); c.setFont('Helvetica-Bold', 15)
        c.drawCentredString(x+bw/2, base+h+12, str(v))
        c.setFillColor(COR_ELEM[elem]); c.setFont('Helvetica-Bold', 11)
        c.drawCentredString(x+bw/2, base-22, elem)
        c.setFillColor(SUB); c.setFont('Helvetica', 8.5)
        c.drawCentredString(x+bw/2, base-36, f'{round(100*v/total)}%')
    dom = ', '.join(l['elementos'].get('dominantes') or ['—'])
    fra = ', '.join(l['elementos'].get('fracos') or ['—'])
    yons = l.get('yongsin') or {}
    c.setFillColor(TXT); c.setFont('Times-Roman', 12)
    c.drawCentredString(W/2, base-90, f'Dominante: {dom}   ·   Ausente ou fraco: {fra}')
    if yons:
        c.setFillColor(ROXO); c.setFont('Times-Bold', 13.5)
        c.drawCentredString(W/2, base-115, f"Seu elemento de equilíbrio: {yons.get('elementoPrincipal','—')}"
                            + (f" (apoio: {yons['elementoSecundario']})" if yons.get('elementoSecundario') else ''))
    c.showPage()

def pagina_arquetipos(c, dados):
    gradiente(c)
    l = dados['leitura']; nome = dados.get('nome') or ''
    dist = (l.get('dezDeuses') or {}).get('distribuicao', {})
    titulo_pagina(c, 'Os 10 Arquétipos do seu mapa',
                  (nome + ' · ' if nome else '') + 'como cada energia se relaciona com o seu centro')
    cw, ch, gapx, gapy = 246, 62, 18, 30
    x0 = (W - 2*cw - gapx)/2; y = H - 150
    for rotulo, par in ARQUETIPOS:
        c.setFillColor(LILAS); c.setFont('Helvetica-Oblique', 9)
        c.drawString(x0, y+4, rotulo)
        for j, (nomeA, hanja, desc_ativo, desc_ausente) in enumerate(par):
            v = dist.get(nomeA, 0)
            x = x0 + j*(cw+gapx); yc = y - ch
            if v >= 1.5: fill, borda, tcor, simb, dsc = ROXO, HexColor('#43296b'), HexColor('#ffffff'), '●●', 'DOMINANTE — '+desc_ativo
            elif v >= 1: fill, borda, tcor, simb, dsc = ROXO2, HexColor('#6d47ab'), HexColor('#ffffff'), '●', desc_ativo
            elif v > 0: fill, borda, tcor, simb, dsc = ROXO3, HexColor('#7c5cb8'), HexColor('#ffffff'), '◐', 'presença leve — '+desc_ativo
            else: fill, borda, tcor, simb, dsc = HexColor('#ffffff'), HexColor('#e6dcf3'), CINZA, '', 'ausente — '+desc_ausente
            card(c, x, yc, cw, ch, fill, borda)
            nome_curto = nomeA.replace(' (Sete Matanças)', '')
            c.setFillColor(tcor)
            larg = draw_misto(c, x+14, yc+ch-22, f'{nome_curto} {hanja}', 'Helvetica-Bold' if v > 0 else 'Helvetica', 11.5)
            if v > 0:
                bolinhas(c, x+14+larg+10, yc+ch-18, 2 if v >= 1.5 else (1 if v >= 1 else 0.5))
            c.setFillColor(tcor if v > 0 else HexColor('#c4bad6')); c.setFont('Helvetica', 8.3)
            c.drawString(x+14, yc+ch-40, dsc[:58])
        y -= ch + gapy
    lx = W/2 - 250
    bolinhas(c, lx, 59, 2, r=3.6, cor=LILAS)
    c.setFillColor(LILAS); c.setFont('Helvetica', 9); c.drawString(lx+20, 56, 'dominante ·')
    bolinhas(c, lx+78, 59, 1, r=3.6, cor=LILAS)
    c.drawString(lx+88, 56, 'ativo ·')
    bolinhas(c, lx+125, 59, 0.5, r=3.6, cor=LILAS)
    c.drawString(lx+135, 56, 'presença leve · claro = ausente — e cada ausência também conta a sua história')
    c.showPage()

def pagina_ciclos(c, dados):
    gradiente(c)
    l = dados['leitura']; ciclos = l.get('ciclosDeDecada') or []
    if not ciclos: return
    idade = dados.get('idadeAproximada') or l.get('idadeAproximada')
    titulo_pagina(c, 'Seus Ciclos de Década', 'o clima de cada fase — quando plantar, construir e colher')
    y = H - 150; alt = 56
    for cic in ciclos[:10]:
        faixa = cic['faixaEtaria']
        ini, fim = [int(x) for x in re.findall(r'\d+', faixa)[:2]]
        atual = idade is not None and ini <= idade <= fim
        if atual:
            card(c, 70, y-alt+12, W-140, alt-6, ROXO, HexColor('#43296b'))
            c.setFillColor(HexColor('#ffffff'))
        else:
            c.setFillColor(TXT)
        c.setFont('Helvetica-Bold', 11)
        c.drawString(86, y-16, faixa + ('   ← você está aqui' if atual else ''))
        c.setFont('Times-Roman', 11)
        c.setFillColor(HexColor('#f0e8fc') if atual else SUB)
        tronco = cic['tronco'].split(' — ')[-1]; ramo = cic['ramo']
        c.drawString(86, y-34, f'{tronco} sobre {ramo}')
        c.setFillColor(HexColor('#ffffff') if atual else ROXO2)
        draw_misto(c, W-86, y-26, cic.get('ganji',''), 'Times-Bold', 13, align='r')
        y -= alt
    c.setFillColor(SUB); c.setFont('Times-Italic', 11)
    c.drawCentredString(W/2, 60, '"A percepção de sorte aumenta quando comportamento e contexto estão alinhados."')
    c.showPage()

def pagina_card_final(c, dados):
    gradiente(c)
    l = dados['leitura']; nome = dados.get('nome') or ''
    card(c, 70, H/2-160, W-140, 300, HexColor('#ffffff'), LILAS)
    estrela(c, W/2-118, H/2+106, 9, ROXO)
    c.setFillColor(ROXO); c.setFont('Times-Bold', 20)
    c.drawCentredString(W/2+10, H/2+100, 'Seu Saju em 4 linhas')
    linhas = [f"Mestre do Dia: {l.get('mestreDoDia','')}"]
    pv = l.get('padraoDeVida') or {}
    if pv: linhas.append(f"Padrão de vida: {pv.get('nome','')} — {pv.get('essencia','')}")
    yons = l.get('yongsin') or {}
    if yons: linhas.append(f"Elemento de equilíbrio: {yons.get('elementoPrincipal','')}")
    dom = ', '.join(l['elementos'].get('dominantes') or [])
    linhas.append(f"Elemento dominante: {dom}")
    y = H/2 + 55
    for ln in linhas[:4]:
        c.setFillColor(TXT)
        draw_misto(c, W/2, y, ln[:88], 'Times-Roman', 12.5, align='c'); y -= 30
    if nome:
        c.setFillColor(SUB); c.setFont('Helvetica', 10)
        c.drawCentredString(W/2, H/2-75, nome)
    c.setFillColor(LILAS); c.setFont('Helvetica', 9)
    c.drawCentredString(W/2, H/2-105, 'sajubrasil.com.br')
    c.setFillColor(SUB); c.setFont('Helvetica', 7.8)
    c.drawCentredString(W/2, 60, 'Este relatório é uma ferramenta de autoconhecimento baseada na tradição coreana do Saju.')
    c.drawCentredString(W/2, 49, 'Ele não substitui acompanhamento médico ou psicológico, e nenhum mapa decide por você: o caminho é sempre seu.')
    c.showPage()

CADERNO = [
    ('Antes de ler o seu mapa', 'Uma tradição de séculos, agora na sua mão', [
        'Na Coreia, antes de um casamento, de uma sociedade ou de uma grande decisão, é comum consultar o <b>Saju</b> (사주) — os "quatro pilares". A palavra vem do costume de ler o destino de uma pessoa a partir de quatro colunas: o ano, o mês, o dia e a hora em que ela nasceu. Cada pilar carrega dois caracteres; os oito juntos formam um retrato único — o seu.',
        'O Saju não é religião, nem adivinhação. É um sistema de observação refinado por gerações de estudiosos, que lê o mundo através de <b>cinco elementos</b> — Madeira, Fogo, Terra, Metal e Água — e dos ritmos com que eles se alimentam e se contêm. Na Coreia de hoje, ele convive naturalmente com a vida moderna: universitárias consultam o Saju antes de escolher carreira, casais antes do casamento, empreendedores antes de abrir negócios.',
        'Não para saber "o que vai acontecer" — mas para entender <b>com que padrões estão jogando</b>. É assim que a Saju Brasil trabalha: <i>não é sobre prever sua vida — é sobre entender seus padrões para decidir melhor.</i>']),
    ('Como ler o seu mapa', 'O mapa em camadas', [
        '<b>Os Quatro Pilares</b> — ano (suas raízes e herança), mês (sua vida pública e carreira), dia (seu eu íntimo e seus vínculos) e hora (seus projetos e sua maturidade).',
        '<b>O Mestre do Dia</b> — o caractere que rege o seu pilar do dia é o centro de tudo: o "você essencial". Todo o restante do mapa é lido em relação a ele.',
        '<b>Os Cinco Elementos</b> — a contagem revela seus talentos naturais (o que transborda) e suas habilidades a cultivar (o que falta). Não existe mapa perfeito: existe mapa compreendido.',
        '<b>Os 10 Arquétipos</b> — dez padrões clássicos que descrevem como cada energia do mapa se relaciona com o seu centro. Os que acendem — e os que se apagam — desenham seu jeito único de funcionar.',
        '<b>Os Ciclos de Década</b> — a vida avança em fases de dez anos. Elas não determinam o que acontece: indicam o clima de cada década — quando plantar, quando construir, quando colher.',
        'Leia sem pressa, de preferência num momento só seu. Marque o que fizer sentido — e também o que incomodar: costuma ser onde mora o crescimento.'])
]

def paginas_caderno(c):
    for titulo, subt, pars in CADERNO:
        gradiente(c)
        titulo_pagina(c, titulo, subt)
        y = H - 140
        estilo = ParagraphStyle('cad', fontName='Times-Roman', fontSize=11.5, leading=17,
                                textColor=TXT, alignment=TA_JUSTIFY)
        for ptxt in pars:
            if CJK_FONT:
                ptxt = CJK_RE.sub(lambda m: f'<font name="CJK">{m.group(0)}</font>', ptxt)
            else:
                ptxt = limpar_cjk(ptxt)
            p = Paragraph(ptxt, estilo)
            wp, hp = p.wrap(W-160, 600)
            p.drawOn(c, 80, y-hp)
            y -= hp + 14
        c.showPage()

def md_para_flowables(md_texto, nome):
    estilos = {
        'h2': ParagraphStyle('h2', fontName='Times-Bold', fontSize=17, leading=21, textColor=ROXO,
                             spaceBefore=18, spaceAfter=6),
        'h3': ParagraphStyle('h3', fontName='Times-Bold', fontSize=13.5, leading=17, textColor=ROXO2,
                             spaceBefore=12, spaceAfter=4),
        'p': ParagraphStyle('p', fontName='Times-Roman', fontSize=11.5, leading=17.5, textColor=TXT,
                            alignment=TA_JUSTIFY, spaceAfter=8),
        'quote': ParagraphStyle('q', fontName='Times-Italic', fontSize=11, leading=16, textColor=SUB,
                                leftIndent=18, spaceAfter=8),
    }
    def inline(t):
        t = t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', t)
        if CJK_FONT:
            t = CJK_RE.sub(lambda m: f'<font name="CJK">{m.group(0)}</font>', t)
        else:
            t = limpar_cjk(t)
        return t
    flow = []
    blocos = re.split(r'\n\s*\n', md_texto.strip())
    for b in blocos:
        b = b.strip()
        if not b: continue
        if b.startswith('---'): flow.append(HRFlowable(width='40%', color=LILAS, spaceBefore=10, spaceAfter=10)); continue
        if b.startswith('> '): continue  # blocos de nota de demonstração são omitidos
        if b.startswith('### '): flow.append(Paragraph(inline(b[4:]), estilos['h3'])); continue
        if b.startswith('## '): flow.append(Paragraph(inline(b[3:]), estilos['h2'])); continue
        if b.startswith('# '): continue  # título do documento já está na capa
        linhas = b.split('\n')
        for ln in linhas:
            ln = ln.strip()
            if not ln: continue
            if ln.startswith('### '): flow.append(Paragraph(inline(ln[4:]), estilos['h3']))
            elif ln.startswith('## '): flow.append(Paragraph(inline(ln[3:]), estilos['h2']))
            elif ln.startswith('- ') or ln.startswith('* '):
                flow.append(Paragraph('•&nbsp;&nbsp;' + inline(ln[2:]), estilos['p']))
            else:
                flow.append(Paragraph(inline(ln), estilos['p']))
    return flow

def pdf_texto(md_texto, nome):
    buf = io.BytesIO()
    def fundo(canv, doc):
        canv.saveState(); gradiente(canv)
        canv.setFillColor(LILAS); canv.setFont('Helvetica', 8)
        canv.drawCentredString(W/2, 30, f'Saju Brasil · {nome}' if nome else 'Saju Brasil')
        canv.restoreState()
    doc = BaseDocTemplate(buf, pagesize=A4, leftMargin=80, rightMargin=80, topMargin=70, bottomMargin=60)
    frame = Frame(80, 60, W-160, H-130, id='corpo')
    doc.addPageTemplates([PageTemplate(id='texto', frames=[frame], onPage=fundo)])
    doc.build(md_para_flowables(md_texto, nome))
    buf.seek(0)
    return buf

def gerar(entrada, saida):
    dados = json.load(open(entrada, encoding='utf-8'))
    premium = dados.get('produto') == 'premium'
    nome = dados.get('nome') or ''
    fixo = io.BytesIO()
    c = rl_canvas.Canvas(fixo, pagesize=A4)
    c.setTitle(('Leitura Premium — ' if premium else 'Leitura de Saju — ') + (nome or 'Saju Brasil'))
    pagina_capa(c, dados)
    if premium: paginas_caderno(c)
    pagina_pilares(c, dados)
    pagina_elementos(c, dados)
    if premium:
        pagina_arquetipos(c, dados)
        pagina_ciclos(c, dados)
    c.save(); fixo.seek(0)

    partes = [PdfReader(fixo)]
    if dados.get('relatorio'):
        partes.append(PdfReader(pdf_texto(dados['relatorio'], nome)))
    card_buf = io.BytesIO()
    c2 = rl_canvas.Canvas(card_buf, pagesize=A4)
    pagina_card_final(c2, dados)
    c2.save(); card_buf.seek(0)
    partes.append(PdfReader(card_buf))

    w = PdfWriter()
    for parte in partes:
        for pg in parte.pages: w.add_page(pg)
    with open(saida, 'wb') as f: w.write(f)
    print(f'ok: {saida} ({sum(len(p.pages) for p in partes)} páginas)')

if __name__ == '__main__':
    gerar(sys.argv[1], sys.argv[2])
