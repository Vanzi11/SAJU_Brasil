/**
 * SAJU Brasil — i18n pt-BR
 *
 * Tradução determinística dos termos estruturais emitidos pelo motor.
 * Textos interpretativos longos (frases em coreano) NÃO são traduzidos aqui:
 * por decisão de arquitetura, eles são substituídos pela camada LLM que gera
 * o relatório em português a partir do JSON estruturado.
 */

export interface StemPt {
  hanja: string;
  romanizacao: string;
  elemento: string;
  polaridade: 'Yang' | 'Yin';
}

/** Troncos celestes (천간, 天干) */
export const TRONCOS_PT: Record<string, StemPt> = {
  갑: { hanja: '甲', romanizacao: 'Gap', elemento: 'Madeira', polaridade: 'Yang' },
  을: { hanja: '乙', romanizacao: 'Eul', elemento: 'Madeira', polaridade: 'Yin' },
  병: { hanja: '丙', romanizacao: 'Byeong', elemento: 'Fogo', polaridade: 'Yang' },
  정: { hanja: '丁', romanizacao: 'Jeong', elemento: 'Fogo', polaridade: 'Yin' },
  무: { hanja: '戊', romanizacao: 'Mu', elemento: 'Terra', polaridade: 'Yang' },
  기: { hanja: '己', romanizacao: 'Gi', elemento: 'Terra', polaridade: 'Yin' },
  경: { hanja: '庚', romanizacao: 'Gyeong', elemento: 'Metal', polaridade: 'Yang' },
  신: { hanja: '辛', romanizacao: 'Sin', elemento: 'Metal', polaridade: 'Yin' },
  임: { hanja: '壬', romanizacao: 'Im', elemento: 'Água', polaridade: 'Yang' },
  계: { hanja: '癸', romanizacao: 'Gye', elemento: 'Água', polaridade: 'Yin' },
};

export interface BranchPt {
  hanja: string;
  romanizacao: string;
  animal: string;
  elemento: string;
  horario: string;
}

/** Ramos terrestres (지지, 地支) */
export const RAMOS_PT: Record<string, BranchPt> = {
  자: { hanja: '子', romanizacao: 'Ja', animal: 'Rato', elemento: 'Água', horario: '23h–01h' },
  축: { hanja: '丑', romanizacao: 'Chuk', animal: 'Boi', elemento: 'Terra', horario: '01h–03h' },
  인: { hanja: '寅', romanizacao: 'In', animal: 'Tigre', elemento: 'Madeira', horario: '03h–05h' },
  묘: { hanja: '卯', romanizacao: 'Myo', animal: 'Coelho', elemento: 'Madeira', horario: '05h–07h' },
  진: { hanja: '辰', romanizacao: 'Jin', animal: 'Dragão', elemento: 'Terra', horario: '07h–09h' },
  사: { hanja: '巳', romanizacao: 'Sa', animal: 'Serpente', elemento: 'Fogo', horario: '09h–11h' },
  오: { hanja: '午', romanizacao: 'O', animal: 'Cavalo', elemento: 'Fogo', horario: '11h–13h' },
  미: { hanja: '未', romanizacao: 'Mi', animal: 'Cabra', elemento: 'Terra', horario: '13h–15h' },
  신: { hanja: '申', romanizacao: 'Sin', animal: 'Macaco', elemento: 'Metal', horario: '15h–17h' },
  유: { hanja: '酉', romanizacao: 'Yu', animal: 'Galo', elemento: 'Metal', horario: '17h–19h' },
  술: { hanja: '戌', romanizacao: 'Sul', animal: 'Cão', elemento: 'Terra', horario: '19h–21h' },
  해: { hanja: '亥', romanizacao: 'Hae', animal: 'Porco', elemento: 'Água', horario: '21h–23h' },
};

/** Cinco elementos (오행, 五行) */
export const ELEMENTOS_PT: Record<string, string> = {
  목: 'Madeira',
  화: 'Fogo',
  토: 'Terra',
  금: 'Metal',
  수: 'Água',
};

export const POLARIDADE_PT: Record<string, string> = { 양: 'Yang', 음: 'Yin' };

export interface DezDeusesPt {
  hanja: string;
  nome: string;
  significado: string;
}

/** Dez deuses (십성, 十星) */
export const DEZ_DEUSES_PT: Record<string, DezDeusesPt> = {
  비견: { hanja: '比肩', nome: 'Companheiro', significado: 'Autonomia, irmandade, autoafirmação' },
  겁재: { hanja: '劫財', nome: 'Rival', significado: 'Competição, ousadia, disputa por recursos' },
  식신: { hanja: '食神', nome: 'Deus do Alimento', significado: 'Criatividade tranquila, sustento, prazer' },
  상관: { hanja: '傷官', nome: 'Oficial Ferido', significado: 'Expressão, crítica, talento inconformado' },
  편재: { hanja: '偏財', nome: 'Riqueza Indireta', significado: 'Ganhos variáveis, oportunidade, generosidade' },
  정재: { hanja: '正財', nome: 'Riqueza Direta', significado: 'Renda estável, poupança, prudência' },
  편관: { hanja: '偏官', nome: 'Oficial Indireto (Sete Matanças)', significado: 'Pressão, coragem, autoridade conquistada' },
  정관: { hanja: '正官', nome: 'Oficial Direto', significado: 'Ordem, responsabilidade, reconhecimento' },
  편인: { hanja: '偏印', nome: 'Selo Indireto', significado: 'Intuição, conhecimento não convencional' },
  정인: { hanja: '正印', nome: 'Selo Direto', significado: 'Estudo, proteção, legitimidade' },
};

export interface SinsalPt {
  hanja: string;
  nome: string;
  significado: string;
}

/** Sinsal (신살, 神殺) — 15 estrelas */
export const SINSAL_PT: Record<string, SinsalPt> = {
  cheon_eul_gwi_in: { hanja: '天乙貴人', nome: 'Nobre Celestial', significado: 'Proteção e ajuda de benfeitores nos momentos difíceis' },
  cheon_deok_gwi_in: { hanja: '天德貴人', nome: 'Virtude Celestial', significado: 'Proteção moral; dissolve adversidades' },
  wol_deok_gwi_in: { hanja: '月德貴人', nome: 'Virtude Lunar', significado: 'Bondade e apoio das pessoas ao redor' },
  mun_chang_gwi_in: { hanja: '文昌貴人', nome: 'Nobre da Literatura', significado: 'Talento acadêmico e clareza intelectual' },
  hak_dang_gwi_in: { hanja: '學堂貴人', nome: 'Salão dos Estudos', significado: 'Aptidão para aprender e ensinar' },
  geum_yeo_rok: { hanja: '金輿祿', nome: 'Carruagem de Ouro', significado: 'Conforto material; apoio do cônjuge/família' },
  hwa_gae_sal: { hanja: '華蓋殺', nome: 'Dossel Floral', significado: 'Espiritualidade, arte, refinamento solitário' },
  yang_in_sal: { hanja: '羊刃殺', nome: 'Lâmina Yang', significado: 'Energia intensa; força que exige domínio' },
  do_hwa_sal: { hanja: '桃花殺', nome: 'Flor de Pessegueiro', significado: 'Charme, magnetismo pessoal, atração' },
  baek_ho_sal: { hanja: '白虎殺', nome: 'Tigre Branco', significado: 'Energia abrupta; atenção a acidentes' },
  yeok_ma_sal: { hanja: '驛馬殺', nome: 'Cavalo das Estações', significado: 'Viagens, mudanças, vida em movimento' },
  gwa_suk_sal: { hanja: '孤宿殺', nome: 'Estrela da Solidão', significado: 'Tendência ao isolamento; independência emocional' },
  gong_mang: { hanja: '空亡', nome: 'Vazio', significado: 'Áreas da vida que pedem desapego' },
  won_jin_sal: { hanja: '元辰殺', nome: 'Rancor Oculto', significado: 'Atritos e antipatias inexplicáveis' },
  gwi_mun_gwan_sal: { hanja: '鬼門關殺', nome: 'Portal dos Espíritos', significado: 'Sensibilidade aguçada; imaginação intensa' },
};

/** Gyeokguk (격국, 格局) — padrões de mapa */
export const GYEOKGUK_PT: Record<string, string> = {
  정관격: 'Padrão do Oficial Direto — retidão, senso de dever',
  정재격: 'Padrão da Riqueza Direta — estabilidade e gestão',
  식신격: 'Padrão do Deus do Alimento — criatividade serena',
  정인격: 'Padrão do Selo Direto — erudição e amparo',
  상관격: 'Padrão do Oficial Ferido — expressão crítica e originalidade',
  편인격: 'Padrão do Selo Indireto — intuição e caminhos alternativos',
  편재격: 'Padrão da Riqueza Indireta — empreendedorismo',
  칠살격: 'Padrão das Sete Matanças — coragem sob pressão',
  비견격: 'Padrão do Companheiro — independência',
  겁재격: 'Padrão do Rival — competitividade',
  종왕격: 'Padrão de Seguir o Forte — potência concentrada',
  종살격: 'Padrão de Seguir o Poder — adaptação à autoridade',
  종재격: 'Padrão de Seguir a Riqueza — foco em resultados',
  중화격: 'Padrão Equilibrado — harmonia entre os elementos',
};

/** 24 termos solares (절기, 節氣) — nomes do hemisfério norte */
export const TERMOS_SOLARES_PT: Record<string, string> = {
  입춘: 'Início da Primavera (Ipchun)', 우수: 'Água das Chuvas (Usu)',
  경칩: 'Despertar dos Insetos (Gyeongchip)', 춘분: 'Equinócio de Primavera (Chunbun)',
  청명: 'Claridade Pura (Cheongmyeong)', 곡우: 'Chuva dos Grãos (Gogu)',
  입하: 'Início do Verão (Ipha)', 소만: 'Pequena Plenitude (Soman)',
  망종: 'Grão na Espiga (Mangjong)', 하지: 'Solstício de Verão (Haji)',
  소서: 'Pequeno Calor (Soseo)', 대서: 'Grande Calor (Daeseo)',
  입추: 'Início do Outono (Ipchu)', 처서: 'Fim do Calor (Cheoseo)',
  백로: 'Orvalho Branco (Baengno)', 추분: 'Equinócio de Outono (Chubun)',
  한로: 'Orvalho Frio (Hallo)', 상강: 'Descida da Geada (Sanggang)',
  입동: 'Início do Inverno (Ipdong)', 소설: 'Pequena Neve (Soseol)',
  대설: 'Grande Neve (Daeseol)', 동지: 'Solstício de Inverno (Dongji)',
  소한: 'Pequeno Frio (Sohan)', 대한: 'Grande Frio (Daehan)',
};

export const NIVEL_FORCA_PT: Record<string, string> = {
  very_weak: 'muito fraco', weak: 'fraco', medium: 'médio',
  strong: 'forte', very_strong: 'muito forte',
};

/** Formata um pilar do motor em pt-BR */
export function formatarPilarPt(pilar: { stem: string; branch: string }): {
  ganji: string;
  tronco: string;
  ramo: string;
  animal: string;
  elementoTronco: string;
  elementoRamo: string;
} {
  const t = TRONCOS_PT[pilar.stem];
  const r = RAMOS_PT[pilar.branch];
  return {
    ganji: pilar.stem + pilar.branch,
    tronco: t ? t.romanizacao + ' (' + t.hanja + ') — ' + t.elemento + ' ' + t.polaridade : pilar.stem,
    ramo: r ? r.romanizacao + ' (' + r.hanja + ') — ' + r.animal + ', ' + r.elemento : pilar.branch,
    animal: r ? r.animal : '',
    elementoTronco: t ? t.elemento : '',
    elementoRamo: r ? r.elemento : '',
  };
}

/**
 * Traduz o JSON do analyze_saju (tipo basic) para estrutura pt-BR.
 * Campos textuais coreanos longos são omitidos (camada LLM cuida deles).
 */
export function traduzirSaju(saju: any): any {
  const contagem: Record<string, number> = {};
  for (const [k, v] of Object.entries(saju.wuxingCount ?? {})) {
    contagem[ELEMENTOS_PT[k] ?? k] = v as number;
  }
  const distribuicao: Record<string, number> = {};
  for (const [k, v] of Object.entries(saju.tenGodsDistribution ?? {})) {
    const d = DEZ_DEUSES_PT[k];
    distribuicao[d ? d.nome : k] = v as number;
  }
  return {
    nascimento: {
      data: saju.birthDate,
      hora: saju.birthTime,
      cidade: saju.birthCity,
      calendario: saju.calendar === 'solar' ? 'solar (gregoriano)' : 'lunar',
      sexo: saju.gender === 'male' ? 'masculino' : 'feminino',
    },
    pilares: {
      ano: formatarPilarPt(saju.year),
      mes: formatarPilarPt(saju.month),
      dia: formatarPilarPt(saju.day),
      hora: formatarPilarPt(saju.hour),
    },
    mestreDoDia: (() => {
      const t = TRONCOS_PT[saju.day?.stem];
      return t ? t.romanizacao + ' (' + t.hanja + ') — ' + t.elemento + ' ' + t.polaridade : saju.day?.stem;
    })(),
    elementos: {
      contagem,
      dominantes: (saju.dominantElements ?? []).map((e: string) => ELEMENTOS_PT[e] ?? e),
      fracos: (saju.weakElements ?? []).map((e: string) => ELEMENTOS_PT[e] ?? e),
    },
    dezDeuses: {
      porPilar: (saju.tenGods ?? []).map((g: string) => {
        const d = DEZ_DEUSES_PT[g];
        return d ? d.nome + ' (' + d.hanja + ')' : g;
      }),
      distribuicao,
    },
    sinsal: (saju.sinSals ?? []).map((s: string) => {
      const i = SINSAL_PT[s];
      return i ? { id: s, nome: i.nome, hanja: i.hanja, significado: i.significado } : { id: s };
    }),
    forcaDoMestre: saju.dayMasterStrength
      ? {
          nivel: NIVEL_FORCA_PT[saju.dayMasterStrength.level] ?? saju.dayMasterStrength.level,
          pontuacao: saju.dayMasterStrength.score,
        }
      : undefined,
    padraoDeVida: saju.gyeokGuk
      ? (() => {
          const desc = GYEOKGUK_PT[saju.gyeokGuk.name];
          return {
            nome: desc ? desc.split(' — ')[0] : saju.gyeokGuk.name,
            hanja: saju.gyeokGuk.hanja,
            essencia: desc ? desc.split(' — ')[1] : undefined,
          };
        })()
      : undefined,
    yongsin: saju.yongSin
      ? {
          elementoPrincipal: ELEMENTOS_PT[saju.yongSin.primaryYongSin] ?? saju.yongSin.primaryYongSin,
          elementoSecundario: ELEMENTOS_PT[saju.yongSin.secondaryYongSin] ?? saju.yongSin.secondaryYongSin,
        }
      : undefined,
  };
}

/** Cores da sorte (오행 → cores) */
export const CORES_PT: Record<string, string> = {
  청색: 'azul', 녹색: 'verde', 적색: 'vermelho', 주황색: 'laranja',
  분홍색: 'rosa', 황색: 'amarelo', 갈색: 'marrom', 백색: 'branco',
  금색: 'dourado', 은색: 'prateado', 흑색: 'preto', 남색: 'azul-marinho',
};

/** Direções da sorte */
export const DIRECOES_PT: Record<string, string> = {
  동: 'leste', 서: 'oeste', 남: 'sul', 북: 'norte', 중앙: 'centro',
  동쪽: 'leste', 서쪽: 'oeste', 남쪽: 'sul', 북쪽: 'norte',
};

/** Traduz a saída do getDailyFortune para pt-BR (conselho coreano é omitido — camada LLM) */
export function traduzirDiaria(d: any): any {
  return {
    data: d.date,
    sorteGeral: d.overallLuck,
    riqueza: d.wealthLuck,
    carreira: d.careerLuck,
    saude: d.healthLuck,
    amor: d.loveLuck,
    corDaSorte: CORES_PT[d.luckyColor] ?? d.luckyColor,
    direcaoDaSorte: DIRECOES_PT[d.luckyDirection] ?? d.luckyDirection,
  };
}
