/**
 * Cidades brasileiras — longitude e timezone IANA para cálculo de Saju
 * (SAJU Brasil — adaptação do motor para nascimentos no Brasil)
 *
 * A timezone IANA carrega todo o histórico de horário de verão brasileiro
 * (1931–2019, com variações por estado), essencial para converter a hora
 * civil registrada no nascimento em instante UTC correto.
 *
 * Longitude: graus decimais, negativa a oeste de Greenwich.
 * Fonte das coordenadas: sedes municipais (IBGE, aproximação de centro urbano).
 */

export interface BrazilCityInfo {
  /** Nome canônico da cidade */
  name: string;
  /** UF */
  state: string;
  /** Longitude em graus decimais (negativa a oeste) */
  longitude: number;
  /** Timezone IANA (inclui histórico de horário de verão) */
  timezone: string;
}

export const BRAZIL_CITIES: BrazilCityInfo[] = [
  // Capitais (27)
  { name: 'São Paulo', state: 'SP', longitude: -46.6333, timezone: 'America/Sao_Paulo' },
  { name: 'Rio de Janeiro', state: 'RJ', longitude: -43.1729, timezone: 'America/Sao_Paulo' },
  { name: 'Brasília', state: 'DF', longitude: -47.8825, timezone: 'America/Sao_Paulo' },
  { name: 'Belo Horizonte', state: 'MG', longitude: -43.9378, timezone: 'America/Sao_Paulo' },
  { name: 'Curitiba', state: 'PR', longitude: -49.2733, timezone: 'America/Sao_Paulo' },
  { name: 'Porto Alegre', state: 'RS', longitude: -51.2300, timezone: 'America/Sao_Paulo' },
  { name: 'Florianópolis', state: 'SC', longitude: -48.5482, timezone: 'America/Sao_Paulo' },
  { name: 'Vitória', state: 'ES', longitude: -40.3376, timezone: 'America/Sao_Paulo' },
  { name: 'Goiânia', state: 'GO', longitude: -49.2539, timezone: 'America/Sao_Paulo' },
  { name: 'Salvador', state: 'BA', longitude: -38.5108, timezone: 'America/Bahia' },
  { name: 'Fortaleza', state: 'CE', longitude: -38.5434, timezone: 'America/Fortaleza' },
  { name: 'Recife', state: 'PE', longitude: -34.8770, timezone: 'America/Recife' },
  { name: 'Natal', state: 'RN', longitude: -35.2110, timezone: 'America/Fortaleza' },
  { name: 'João Pessoa', state: 'PB', longitude: -34.8631, timezone: 'America/Fortaleza' },
  { name: 'Maceió', state: 'AL', longitude: -35.7353, timezone: 'America/Maceio' },
  { name: 'Aracaju', state: 'SE', longitude: -37.0731, timezone: 'America/Maceio' },
  { name: 'Teresina', state: 'PI', longitude: -42.8019, timezone: 'America/Fortaleza' },
  { name: 'São Luís', state: 'MA', longitude: -44.3028, timezone: 'America/Fortaleza' },
  { name: 'Belém', state: 'PA', longitude: -48.5044, timezone: 'America/Belem' },
  { name: 'Macapá', state: 'AP', longitude: -51.0664, timezone: 'America/Belem' },
  { name: 'Palmas', state: 'TO', longitude: -48.3603, timezone: 'America/Araguaina' },
  { name: 'Cuiabá', state: 'MT', longitude: -56.0966, timezone: 'America/Cuiaba' },
  { name: 'Campo Grande', state: 'MS', longitude: -54.6462, timezone: 'America/Campo_Grande' },
  { name: 'Manaus', state: 'AM', longitude: -60.0217, timezone: 'America/Manaus' },
  { name: 'Boa Vista', state: 'RR', longitude: -60.6733, timezone: 'America/Boa_Vista' },
  { name: 'Porto Velho', state: 'RO', longitude: -63.9004, timezone: 'America/Porto_Velho' },
  { name: 'Rio Branco', state: 'AC', longitude: -67.8099, timezone: 'America/Rio_Branco' },

  // Grandes cidades não-capitais
  { name: 'Guarulhos', state: 'SP', longitude: -46.5333, timezone: 'America/Sao_Paulo' },
  { name: 'Campinas', state: 'SP', longitude: -47.0626, timezone: 'America/Sao_Paulo' },
  { name: 'São Bernardo do Campo', state: 'SP', longitude: -46.5646, timezone: 'America/Sao_Paulo' },
  { name: 'Santo André', state: 'SP', longitude: -46.5384, timezone: 'America/Sao_Paulo' },
  { name: 'Osasco', state: 'SP', longitude: -46.7916, timezone: 'America/Sao_Paulo' },
  { name: 'Sorocaba', state: 'SP', longitude: -47.4581, timezone: 'America/Sao_Paulo' },
  { name: 'Ribeirão Preto', state: 'SP', longitude: -47.8103, timezone: 'America/Sao_Paulo' },
  { name: 'Santos', state: 'SP', longitude: -46.3336, timezone: 'America/Sao_Paulo' },
  { name: 'São José dos Campos', state: 'SP', longitude: -45.8869, timezone: 'America/Sao_Paulo' },
  { name: 'São José do Rio Preto', state: 'SP', longitude: -49.3794, timezone: 'America/Sao_Paulo' },
  { name: 'Uberlândia', state: 'MG', longitude: -48.2772, timezone: 'America/Sao_Paulo' },
  { name: 'Juiz de Fora', state: 'MG', longitude: -43.3503, timezone: 'America/Sao_Paulo' },
  { name: 'Contagem', state: 'MG', longitude: -44.0537, timezone: 'America/Sao_Paulo' },
  { name: 'Montes Claros', state: 'MG', longitude: -43.8647, timezone: 'America/Sao_Paulo' },
  { name: 'Londrina', state: 'PR', longitude: -51.1628, timezone: 'America/Sao_Paulo' },
  { name: 'Maringá', state: 'PR', longitude: -51.9386, timezone: 'America/Sao_Paulo' },
  { name: 'Cascavel', state: 'PR', longitude: -53.4552, timezone: 'America/Sao_Paulo' },
  { name: 'Joinville', state: 'SC', longitude: -48.8487, timezone: 'America/Sao_Paulo' },
  { name: 'Blumenau', state: 'SC', longitude: -49.0713, timezone: 'America/Sao_Paulo' },
  { name: 'Caxias do Sul', state: 'RS', longitude: -51.1794, timezone: 'America/Sao_Paulo' },
  { name: 'Pelotas', state: 'RS', longitude: -52.3376, timezone: 'America/Sao_Paulo' },
  { name: 'Niterói', state: 'RJ', longitude: -43.1034, timezone: 'America/Sao_Paulo' },
  { name: 'São Gonçalo', state: 'RJ', longitude: -43.0539, timezone: 'America/Sao_Paulo' },
  { name: 'Duque de Caxias', state: 'RJ', longitude: -43.3117, timezone: 'America/Sao_Paulo' },
  { name: 'Nova Iguaçu', state: 'RJ', longitude: -43.4511, timezone: 'America/Sao_Paulo' },
  { name: 'Campos dos Goytacazes', state: 'RJ', longitude: -41.3297, timezone: 'America/Sao_Paulo' },
  { name: 'Vila Velha', state: 'ES', longitude: -40.2925, timezone: 'America/Sao_Paulo' },
  { name: 'Serra', state: 'ES', longitude: -40.3078, timezone: 'America/Sao_Paulo' },
  { name: 'Aparecida de Goiânia', state: 'GO', longitude: -49.2439, timezone: 'America/Sao_Paulo' },
  { name: 'Anápolis', state: 'GO', longitude: -48.9528, timezone: 'America/Sao_Paulo' },
  { name: 'Feira de Santana', state: 'BA', longitude: -38.9663, timezone: 'America/Bahia' },
  { name: 'Vitória da Conquista', state: 'BA', longitude: -40.8394, timezone: 'America/Bahia' },
  { name: 'Jaboatão dos Guararapes', state: 'PE', longitude: -35.0148, timezone: 'America/Recife' },
  { name: 'Olinda', state: 'PE', longitude: -34.8555, timezone: 'America/Recife' },
  { name: 'Caruaru', state: 'PE', longitude: -35.9761, timezone: 'America/Recife' },
  { name: 'Campina Grande', state: 'PB', longitude: -35.8811, timezone: 'America/Fortaleza' },
  { name: 'Caucaia', state: 'CE', longitude: -38.6531, timezone: 'America/Fortaleza' },
  { name: 'Juazeiro do Norte', state: 'CE', longitude: -39.3153, timezone: 'America/Fortaleza' },
  { name: 'Imperatriz', state: 'MA', longitude: -47.4917, timezone: 'America/Fortaleza' },
  { name: 'Ananindeua', state: 'PA', longitude: -48.3719, timezone: 'America/Belem' },
  { name: 'Santarém', state: 'PA', longitude: -54.7083, timezone: 'America/Santarem' },
  { name: 'Marabá', state: 'PA', longitude: -49.1178, timezone: 'America/Belem' },
  { name: 'Dourados', state: 'MS', longitude: -54.8058, timezone: 'America/Campo_Grande' },
  { name: 'Rondonópolis', state: 'MT', longitude: -54.6356, timezone: 'America/Cuiaba' },
  { name: 'Fernando de Noronha', state: 'PE', longitude: -32.4297, timezone: 'America/Noronha' },
];

/**
 * Normaliza nome de cidade: minúsculas, sem acentos, espaços colapsados.
 */
export function normalizeBrazilCityName(name: string): string {
  return name
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ');
}

const BRAZIL_CITY_INDEX: Map<string, BrazilCityInfo> = new Map();
for (const city of BRAZIL_CITIES) {
  BRAZIL_CITY_INDEX.set(normalizeBrazilCityName(city.name), city);
  // alias "cidade-UF" (ex.: "sao paulo-sp")
  BRAZIL_CITY_INDEX.set(`${normalizeBrazilCityName(city.name)}-${city.state.toLowerCase()}`, city);
}

/**
 * Busca dados de uma cidade brasileira (aceita variações de acento/caixa).
 * @returns info da cidade ou undefined se não reconhecida
 */
export function getBrazilCityInfo(name?: string): BrazilCityInfo | undefined {
  if (!name) return undefined;
  return BRAZIL_CITY_INDEX.get(normalizeBrazilCityName(name));
}

/**
 * Verifica se o nome corresponde a uma cidade brasileira conhecida.
 */
export function isBrazilBirthCity(name?: string): boolean {
  return getBrazilCityInfo(name) !== undefined;
}
