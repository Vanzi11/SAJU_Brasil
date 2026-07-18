import { formatInTimeZone } from 'date-fns-tz';
const { getAdjustedBirthInstantForSaju } = await import('../fortuneteller/dist/utils/date.js');
const { calculateSaju } = await import('../fortuneteller/dist/lib/saju.js');

const kst = d => formatInTimeZone(d, 'Asia/Seoul', 'yyyy-MM-dd HH:mm');
const show = (label, d) => console.log(label.padEnd(52), '→ solar:', kst(d));

// A. DST: São Paulo 01/01/1990 12:00 (horário de verão, UTC-2)
//    civil 12:00 → UTC 14:00 → solar = UTC - 187min = 10:53
show('A. SP 01/01/1990 12:00 (DST) espera 10:53', getAdjustedBirthInstantForSaju('1990-01-01','12:00','São Paulo'));

// B. Mesma data fora do DST: SP 15/03/1990 12:00 (UTC-3)
//    civil 12:00 → UTC 15:00 → solar 11:53
show('B. SP 15/03/1990 12:00 (sem DST) espera 11:53', getAdjustedBirthInstantForSaju('1990-03-15','12:00','São Paulo'));

// C. Manaus 01/07/1995 06:00 (UTC-4, lon -60.02 ≈ meridiano) espera 06:00
show('C. Manaus 01/07/1995 06:00 espera 06:00', getAdjustedBirthInstantForSaju('1995-07-01','06:00','Manaus'));

// D. Rio Branco 01/07/2000 12:00 (UTC-5, lon -67.81) espera 12:29
show('D. Rio Branco 01/07/2000 12:00 espera 12:29', getAdjustedBirthInstantForSaju('2000-07-01','12:00','Rio Branco'));

// E. Fortaleza 01/07/2000 12:00 (UTC-3, lon -38.54) espera 12:26
show('E. Fortaleza 01/07/2000 12:00 espera 12:26', getAdjustedBirthInstantForSaju('2000-07-01','12:00','Fortaleza'));

// F. Fronteira de ramo horário: SP 11:05 civil sem DST → solar 10:58 (사시), ignorar longitude daria 오시
const f = calculateSaju('1990-03-15','11:05','solar',false,'male','São Paulo');
console.log('F. SP 11:05 → pilar hora:', f.hour.branch, '(espera 사 = 09-11h)  cidade:', f.birthCity);

// G. Sem cidade (default Seul) — regressão do fluxo coreano
const g = calculateSaju('1990-03-15','10:30','solar',false,'male');
console.log('G. Regressão Seul:', g.year.stem+g.year.branch, g.month.stem+g.month.branch, g.day.stem+g.day.branch, g.hour.stem+g.hour.branch, '(espera 경오 기묘 기묘 기사)');

// H. Nascimento SP mesma hora civil que G — pilares podem divergir (instante real difere em ~12h)
const h = calculateSaju('1990-03-15','10:30','solar',false,'male','Sao Paulo'); // sem acento de propósito
console.log('H. SP 15/03/1990 10:30:', h.year.stem+h.year.branch, h.month.stem+h.month.branch, h.day.stem+h.day.branch, h.hour.stem+h.hour.branch, ' cidade:', h.birthCity);
