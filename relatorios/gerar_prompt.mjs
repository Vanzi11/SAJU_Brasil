#!/usr/bin/env node
/**
 * Bitna Saju — pipeline de geração de prompt para relatórios via LLM
 *
 * Uso:
 *   node gerar_prompt.mjs individual <data> <hora> <cidade> <sexo>
 *   node gerar_prompt.mjs sinastria <data1> <hora1> <cidade1> <sexo1> <data2> <hora2> <cidade2> <sexo2>
 *
 * Saída: JSON { system, user } pronto para enviar a qualquer API de LLM
 * (Claude, GPT etc.). O campo "user" contém os dados do mapa em pt-BR.
 *
 * Requisito: rodar com TZ=Asia/Seoul (ver docs/FASE1_FUSO_BRASIL.md).
 */
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath, pathToFileURL } from 'url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ENGINE = process.env.SAJU_ENGINE_DIST ?? join(HERE, '../fortuneteller/dist');

// No Windows, import() dinâmico exige URL file:// — pathToFileURL resolve nas duas plataformas
const importEngine = (rel) => import(pathToFileURL(join(ENGINE, rel)).href);

const { calculateSaju } = await importEngine('lib/saju.js');
const { calculateDaeUn } = await importEngine('lib/dae_un.js');
const { checkCompatibility } = await importEngine('lib/compatibility.js');
const { traduzirSaju, ELEMENTOS_PT, TRONCOS_PT, RAMOS_PT } = await importEngine('data/i18n/pt_br.js');

function traduzirDaeUn(periods) {
  return periods.slice(0, 10).map(p => ({
    faixaEtaria: p.startAge + '–' + p.endAge + ' anos',
    ganji: p.stem + p.branch,
    tronco: (TRONCOS_PT[p.stem]?.romanizacao ?? p.stem) + ' — ' + (ELEMENTOS_PT[p.stemElement] ?? p.stemElement),
    ramo: (RAMOS_PT[p.branch]?.romanizacao ?? p.branch) + ' — ' + (ELEMENTOS_PT[p.branchElement] ?? p.branchElement)
      + (RAMOS_PT[p.branch] ? ' (' + RAMOS_PT[p.branch].animal + ')' : ''),
  }));
}

function mapaCompleto(data, hora, cidade, sexo) {
  const saju = calculateSaju(data, hora, 'solar', false, sexo, cidade);
  const leitura = traduzirSaju(saju);
  leitura.ciclosDeDecada = traduzirDaeUn(calculateDaeUn(saju));
  return { saju, leitura };
}

const modo = process.argv[2];
let system, dados;

if (modo === 'individual') {
  const [data, hora, cidade, sexo] = process.argv.slice(3);
  system = readFileSync(join(HERE, 'prompts/leitura_individual.md'), 'utf8');
  const idade = new Date().getFullYear() - parseInt(data.slice(0, 4), 10);
  dados = { idadeAproximada: idade, ...mapaCompleto(data, hora, cidade, sexo).leitura };
} else if (modo === 'sinastria') {
  const [d1, h1, c1, s1, d2, h2, c2, s2] = process.argv.slice(3);
  system = readFileSync(join(HERE, 'prompts/sinastria.md'), 'utf8');
  const p1 = mapaCompleto(d1, h1, c1, s1);
  const p2 = mapaCompleto(d2, h2, c2, s2);
  const compat = checkCompatibility(p1.saju, p2.saju);
  dados = {
    pessoa1: p1.leitura,
    pessoa2: p2.leitura,
    analiseMotor: {
      score: compat.compatibilityScore,
      harmoniaElemental: compat.elementHarmony?.harmony,
    },
  };
} else {
  console.error('Modo inválido. Use: individual | sinastria');
  process.exit(1);
}

const user = 'Gere o relatório a partir destes dados calculados:\n\n```json\n'
  + JSON.stringify(dados, null, 2) + '\n```';

console.log(JSON.stringify({ system, user }, null, 2));

// O cache do motor mantém um setInterval sem unref(); encerramos explicitamente.
process.exit(0);
