const { calculateSaju } = await import('../fortuneteller/dist/lib/saju.js');
const { traduzirSaju } = await import('../fortuneteller/dist/data/i18n/pt_br.js');
const s = calculateSaju('1990-01-01','12:00','solar',false,'female','São Paulo');
const t = traduzirSaju(s);
console.log(JSON.stringify(t, null, 1));
// verificação de cobertura: hangul remanescente fora de 'ganji'
const json = JSON.stringify(t);
const semGanji = JSON.stringify(t, (k,v) => k === 'ganji' ? undefined : v);
const hangul = semGanji.match(/[가-힯]+/g);
console.log('\nHangul fora de ganji:', hangul ? hangul.join(',') : 'NENHUM ✓');
