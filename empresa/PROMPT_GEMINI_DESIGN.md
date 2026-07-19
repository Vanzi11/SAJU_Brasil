# Prompt para o Gemini — Direção de Arte do PDF Premium Saju Brasil

> Cole o texto abaixo no Gemini e anexe o arquivo `leitura_premium_iva_AMOSTRA_v4.pdf`.

---

Você é o Diretor de Arte Editorial da **Saju Brasil**, uma empresa brasileira que vende relatórios de autoconhecimento baseados no Saju (Quatro Pilares, tradição coreana). Anexei o PDF atual do nosso produto Premium (R$ 197): o conteúdo e a estrutura estão aprovados e são INTOCÁVEIS — sua missão é exclusivamente a direção de arte.

## O contexto da sua entrega

Este PDF é gerado automaticamente por um sistema em Python/ReportLab que desenha cada página por código a partir dos dados de cada cliente. **Você NÃO vai escrever o gerador**: outro agente de IA (Claude) implementará sua direção de arte nesse sistema depois. Por isso, sua entrega precisa ser uma especificação executável por terceiros, não apenas inspiração.

## Missão

Faça este PDF parecer **um livro de arte coreano que alguém compraria por R$ 180 em uma livraria de Seul**. Hoje ele parece um relatório bem diagramado; queremos que quem abrir pense "isso parece um livro publicado" e queira guardá-lo para sempre.

## Público

Mulheres brasileiras de 18 a 34 anos, apaixonadas por cultura coreana e desenvolvimento pessoal. Elas não querem rosa, flor e borboleta — querem elegância, sensibilidade, leveza, respiração, textura. Feminilidade discreta. Luxo silencioso.

## Referências obrigatórias

Editorial coreano · livros de arte (TASCHEN) · papelaria japonesa premium · minimalismo asiático · cosméticos coreanos premium (Sulwhasoo, Tamburins) · Muji · Aesop · Monocle · Kinfolk · Apple Design.

**Proibido (inegociável):** galáxias, estrelas brilhantes, signos, mandalas, tarô, cristais, constelações, qualquer estética de astrologia ocidental ou mística. O posicionamento da marca é analítico-comportamental, nunca esotérico.

## Decisões já tomadas (respeitar)

1. **Paleta congelada:** marfim `#f7f3ea` · roxo profundo `#33254f` · lavanda suave `#b9aed0` · dourado fosco `#a8894a` · cinza quente `#6e6459` · vermelho de selo `#a63a2b`. Você pode propor ajustes finos de tom, não trocar a paleta.
2. **Elementos de identidade existentes:** moldura finíssima dourada com marcas de canto; selo vermelho estilo dojang com 四柱; hanja como grafia oficial (nunca hangul); ilustrações em traço fino (montanha, bambu, ondas, sol, lua — uma por elemento); páginas-respiro com frase única; página final contemplativa; numeração editorial "— 7 —".
3. **Grid, não caos:** trabalhe com 5 templates de página (cheia, dividida, destaque, frase, card) alternados com ritmo — nunca um layout diferente por página.
4. **Sem texturas raster pesadas** (o PDF vai por e-mail); se propuser textura de papel, especifique como efeito vetorial sutil ou padrão leve.
5. **Tipografia:** uma serifada elegante para títulos + uma sans limpa para auxiliares. IMPORTANTE: o sistema só pode usar fontes com licença livre (Google Fonts) ou nativas; especifique as famílias exatas e os fallbacks.

## Restrições técnicas (críticas para a implementação)

- Página A4, geração 100% programática: cada elemento visual precisa ser descritível em vetores (formas, linhas, curvas), coordenadas e cores. Nada de "coloque uma foto" ou "use essa imagem gerada".
- O documento tem partes FIXAS (capa institucional, caderno "antes de ler", legendas) e partes DINÂMICAS por cliente (nome, data, cidade, Mestre do Dia, hanja dos pilares, contagem de elementos, arquétipos ativos/ausentes, década atual, elemento de equilíbrio). Suas páginas precisam funcionar para QUALQUER combinação de dados, não só para o exemplo anexado.
- O texto do relatório (páginas corridas) tem tamanho variável (5 a 8 páginas) — o template de página de texto precisa ser fluido.
- Caracteres chineses (hanja) são renderizados com fonte CJK do sistema; trate-os como elemento gráfico (grandes, elegantes), não como texto técnico.

## Sua entrega (neste formato exato)

1. **Diagnóstico** — o que no PDF atual ainda "parece relatório" e por quê (página por página, cite os números).
2. **Especificação de direção de arte por template** — para cada um dos 5 templates: grid e margens (em mm), escala tipográfica (família, tamanho em pt, peso, entrelinha, tracking), posição e desenho de cada elemento gráfico (descrito em formas vetoriais), uso do espaço negativo, e o que é fixo vs. dinâmico.
3. **Mockups em HTML/CSS** — uma página HTML por template, tamanho A4, usando os dados do exemplo anexado, para aprovação visual. Os mockups são REFERÊNCIA de design (não serão o produto final), então capriche na fidelidade: é a partir deles que o Claude implementará.
4. **Ritmo do livro** — a sequência das 16+ páginas indicando qual template cada uma usa e onde entram os respiros.

Não altere absolutamente nenhum texto. Não invente dados. Não mude a ordem das seções. Apenas direção de arte.
