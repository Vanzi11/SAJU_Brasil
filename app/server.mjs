#!/usr/bin/env node
/**
 * SAJU Brasil — backend HTTP (Fase 4)
 *
 * Endpoints:
 *   GET  /                  → UI de teste
 *   GET  /cidades?q=...     → autocomplete de cidades brasileiras
 *   POST /leitura           → { data, hora?, cidade, sexo, gerarRelatorio? }
 *   POST /sinastria         → { pessoa1: {...}, pessoa2: {...}, gerarRelatorio? }
 *   POST /diaria            → { data, hora, cidade, sexo, alvo }
 *
 * Sem dependências externas (Node >= 18). Se ANTHROPIC_API_KEY estiver
 * definida e gerarRelatorio=true, o relatório narrativo é gerado via API.
 */
process.env.TZ = 'Asia/Seoul'; // requisito do motor (ver docs/FASE1_FUSO_BRASIL.md)

import { createServer } from 'http';
import { readFileSync, writeFileSync, readFileSync as lerArquivo, unlinkSync } from 'fs';
import { spawn } from 'child_process';
import { tmpdir } from 'os';
import { dirname, join } from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ENGINE = process.env.SAJU_ENGINE_DIST ?? join(HERE, '../fortuneteller/dist');
const PROMPTS = process.env.SAJU_PROMPTS ?? join(HERE, '../relatorios/prompts');
const PORT = parseInt(process.env.PORT ?? '3333', 10);
const MODELO = process.env.SAJU_LLM_MODEL ?? 'claude-sonnet-5';

// No Windows, import() dinâmico exige URL file:// — pathToFileURL resolve nas duas plataformas
const importEngine = (rel) => import(pathToFileURL(join(ENGINE, rel)).href);

const { calculateSaju } = await importEngine('lib/saju.js');
const { calculateDaeUn } = await importEngine('lib/dae_un.js');
const { checkCompatibility } = await importEngine('lib/compatibility.js');
const { getDailyFortune } = await importEngine('lib/fortune.js');
const { BRAZIL_CITIES, normalizeBrazilCityName } = await importEngine('data/brazil_cities.js');
const { traduzirSaju, traduzirDiaria, ELEMENTOS_PT, TRONCOS_PT, RAMOS_PT } =
  await importEngine('data/i18n/pt_br.js');

const promptIndividual = readFileSync(join(PROMPTS, 'leitura_individual.md'), 'utf8');
const promptSinastria = readFileSync(join(PROMPTS, 'sinastria.md'), 'utf8');
const promptPremium = readFileSync(join(PROMPTS, 'leitura_premium.md'), 'utf8');
const indexHtml = readFileSync(join(HERE, 'public/index.html'), 'utf8');

function traduzirDaeUn(periods) {
  return periods.slice(0, 10).map((p) => ({
    faixaEtaria: `${p.startAge}–${p.endAge} anos`,
    ganji: p.stem + p.branch,
    tronco: `${TRONCOS_PT[p.stem]?.romanizacao ?? p.stem} — ${ELEMENTOS_PT[p.stemElement] ?? p.stemElement}`,
    ramo: `${RAMOS_PT[p.branch]?.romanizacao ?? p.branch} — ${ELEMENTOS_PT[p.branchElement] ?? p.branchElement}` +
      (RAMOS_PT[p.branch] ? ` (${RAMOS_PT[p.branch].animal})` : ''),
  }));
}

function montarLeitura({ data, hora, cidade, sexo }) {
  const horaDesconhecida = !hora;
  const horaEfetiva = hora || '12:00';
  const saju = calculateSaju(data, horaEfetiva, 'solar', false, sexo, cidade);
  const leitura = traduzirSaju(saju);
  leitura.ciclosDeDecada = traduzirDaeUn(calculateDaeUn(saju));
  if (horaDesconhecida) {
    // 3 pilares: sem hora confiável, o pilar da hora é omitido
    delete leitura.pilares.hora;
    leitura.horaDesconhecida = true;
    leitura.nascimento.hora = 'desconhecida';
  }
  return { saju, leitura };
}

async function gerarRelatorioLLM(system, user) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return null;
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'x-api-key': key,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: MODELO,
      max_tokens: 4000,
      system,
      messages: [{ role: 'user', content: user }],
    }),
  });
  if (!res.ok) throw new Error(`API LLM: HTTP ${res.status}: ${await res.text()}`);
  const json = await res.json();
  return json.content?.[0]?.text ?? null;
}

const montarUser = (dados) =>
  'Gere o relatório a partir destes dados calculados:\n\n```json\n' +
  JSON.stringify(dados, null, 2) + '\n```';

async function lerBody(req) {
  let body = '';
  for await (const chunk of req) body += chunk;
  return body ? JSON.parse(body) : {};
}

const json = (res, code, obj) => {
  res.writeHead(code, { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' });
  res.end(JSON.stringify(obj, null, 2));
};

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  try {
    if (req.method === 'GET' && url.pathname === '/') {
      res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
      return res.end(indexHtml);
    }

    if (req.method === 'GET' && url.pathname === '/cidades') {
      const q = normalizeBrazilCityName(url.searchParams.get('q') ?? '');
      const lista = BRAZIL_CITIES
        .filter((c) => !q || normalizeBrazilCityName(c.name).includes(q))
        .slice(0, 15)
        .map((c) => ({ nome: c.name, uf: c.state }));
      return json(res, 200, lista);
    }

    if (req.method === 'POST' && url.pathname === '/leitura') {
      const b = await lerBody(req);
      if (!b.data || !b.cidade || !b.sexo) return json(res, 400, { erro: 'Campos obrigatórios: data, cidade, sexo (hora é opcional)' });
      const { leitura } = montarLeitura(b);
      const idade = new Date().getFullYear() - parseInt(b.data.slice(0, 4), 10);
      const premium = b.produto === 'premium';
      const dados = { nome: b.nome || undefined, idadeAproximada: idade, ...leitura };
      if (premium && b.tipoSanguineo) dados.tipoSanguineo = b.tipoSanguineo;
      const sys = premium ? promptPremium : promptIndividual;
      const user = montarUser(dados);
      const resposta = { leitura, produto: premium ? 'premium' : 'essencial', llmDisponivel: !!process.env.ANTHROPIC_API_KEY, prompt: { system: sys, user } };
      if (b.gerarRelatorio) resposta.relatorio = await gerarRelatorioLLM(sys, user);
      return json(res, 200, resposta);
    }

    if (req.method === 'POST' && url.pathname === '/sinastria') {
      const b = await lerBody(req);
      if (!b.pessoa1 || !b.pessoa2) return json(res, 400, { erro: 'Campos obrigatórios: pessoa1, pessoa2' });
      const p1 = montarLeitura(b.pessoa1);
      const p2 = montarLeitura(b.pessoa2);
      const compat = checkCompatibility(p1.saju, p2.saju);
      const tiposValidos = ['amorosa', 'societaria', 'amizade', 'familiar'];
      const tipoRelacao = tiposValidos.includes(b.tipoRelacao) ? b.tipoRelacao : 'amorosa';
      const dados = {
        tipoRelacao,
        pessoa1: { nome: b.pessoa1.nome || undefined, ...p1.leitura },
        pessoa2: { nome: b.pessoa2.nome || undefined, ...p2.leitura },
        analiseMotor: { score: compat.compatibilityScore, harmoniaElemental: compat.elementHarmony?.harmony },
      };
      const user = montarUser(dados);
      const resposta = { dados, llmDisponivel: !!process.env.ANTHROPIC_API_KEY, prompt: { system: promptSinastria, user } };
      if (b.gerarRelatorio) resposta.relatorio = await gerarRelatorioLLM(promptSinastria, user);
      return json(res, 200, resposta);
    }

    if (req.method === 'POST' && url.pathname === '/diaria') {
      const b = await lerBody(req);
      if (!b.data || !b.hora || !b.cidade || !b.sexo) return json(res, 400, { erro: 'Campos obrigatórios: data, hora, cidade, sexo (alvo opcional = hoje)' });
      const saju = calculateSaju(b.data, b.hora, 'solar', false, b.sexo, b.cidade);
      const alvo = b.alvo ?? new Date().toISOString().slice(0, 10);
      return json(res, 200, { diaria: traduzirDiaria(getDailyFortune(saju, alvo)) });
    }

    if (req.method === 'POST' && url.pathname === '/pdf') {
      const b = await lerBody(req);
      if (!b.data || !b.cidade || !b.sexo) return json(res, 400, { erro: 'Campos obrigatórios: data, cidade, sexo' });
      const { leitura } = montarLeitura(b);
      const premium = b.produto === 'premium';
      const idade = new Date().getFullYear() - parseInt(b.data.slice(0, 4), 10);
      const dados = { nome: b.nome || undefined, idadeAproximada: idade, ...leitura };
      if (premium && b.tipoSanguineo) dados.tipoSanguineo = b.tipoSanguineo;
      let relatorio = b.relatorio ?? null; // texto pronto pode ser enviado (fluxo com revisão humana)
      if (!relatorio && b.gerarRelatorio) {
        relatorio = await gerarRelatorioLLM(premium ? promptPremium : promptIndividual, montarUser(dados));
      }
      const entrada = join(tmpdir(), `saju_pdf_${Date.now()}.json`);
      const saida = join(tmpdir(), `saju_pdf_${Date.now()}.pdf`);
      writeFileSync(entrada, JSON.stringify({ produto: premium ? 'premium' : 'essencial', nome: b.nome || null, idadeAproximada: idade, leitura, relatorio }));
      const py = process.platform === 'win32' ? 'python' : 'python3';
      await new Promise((ok, ruim) => {
        const pr = spawn(py, [join(HERE, 'pdf/gerar_pdf.py'), entrada, saida]);
        let err = ''; pr.stderr.on('data', d => err += d);
        pr.on('close', cod => cod === 0 ? ok() : ruim(new Error('gerar_pdf: ' + err.slice(0, 400))));
      });
      const pdf = lerArquivo(saida);
      try { unlinkSync(entrada); unlinkSync(saida); } catch {}
      res.writeHead(200, { 'content-type': 'application/pdf', 'content-disposition': 'attachment; filename="leitura-saju.pdf"' });
      return res.end(pdf);
    }

    return json(res, 404, { erro: 'Rota não encontrada' });
  } catch (e) {
    return json(res, 500, { erro: String(e.message ?? e) });
  }
});

server.listen(PORT, () => console.log(`SAJU Brasil backend em http://localhost:${PORT}`));
