'use strict';

/**
 * Cliente para a API Rastro dos Correios (v1).
 *
 * Documentação oficial: https://www.correios.com.br/atendimento/developers
 * Acesso à API Rastro requer contrato com os Correios e cartão de postagem.
 *
 * Fluxo de autenticação:
 *   1. POST /token/v1/autentica/cartaopostagem  → recebe token JWT
 *   2. GET  /rastro/v1/objetos?codObjeto=...    → eventos de rastreamento
 */

const axios  = require('axios');
const logger = require('./logger');

// Tipos de evento dos Correios que confirmam entrega ao destinatário
const TIPOS_ENTREGUE = new Set(['BDE', 'BDI', 'BDE01']);

// Palavras-chave na descrição que também indicam entrega (fallback)
const DESCRICOES_ENTREGUE = [
  'objeto entregue ao destinatário',
  'objeto entregue',
  'entregue ao destinatário',
];

// Tipos de evento que indicam pedido NÃO finalizado (nunca atualizar Wake)
const TIPOS_EM_TRANSITO = new Set([
  'BPR', // Objeto postado
  'OEC', // Saiu para entrega
  'IDC', // Tentativa de entrega
  'IDI', // Tentativa de entrega (internacional)
  'CDI', // Aguardando retirada
  'LDI', // Aguardando retirada
  'PMT', // Em processamento na unidade
  'RO',  // Em rota
]);

class CorreiosApi {
  constructor(config) {
    this.apiUrl          = config.correios.apiUrl;
    this.usuario         = config.correios.usuario;
    this.cartaoPostagem  = config.correios.cartaoPostagem;
    this.maxTentativas   = config.limites.maxTentativas;

    // Senha usada apenas no momento da autenticação — nunca logada
    this._senha = config.correios.senha;

    this._token       = null;
    this._tokenExpira = null;

    this.client = axios.create({
      baseURL: this.apiUrl,
      timeout: 20_000,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // ─── Autenticação ────────────────────────────────────────────────────────

  async autenticar() {
    // Reutiliza token válido (com 5 min de margem)
    if (this._token && this._tokenExpira && Date.now() < this._tokenExpira - 300_000) {
      return;
    }

    logger.info('Correios: autenticando na API Rastro...');

    const credencialBase64 = Buffer
      .from(`${this.usuario}:${this._senha}`)
      .toString('base64');

    try {
      const resposta = await this.client.post(
        '/token/v1/autentica/cartaopostagem',
        { numero: this.cartaoPostagem },
        {
          headers: {
            Authorization: `Basic ${credencialBase64}`,
          },
        }
      );

      const dados = resposta.data;

      if (!dados.token) {
        throw new Error('Token não retornado na resposta de autenticação');
      }

      this._token = dados.token;

      // Correios retorna "expiraEm" como "YYYY-MM-DD HH:mm:ss" (horário de Brasília)
      this._tokenExpira = dados.expiraEm
        ? new Date(dados.expiraEm.replace(' ', 'T') + '-03:00').getTime()
        : Date.now() + 60 * 60 * 1000; // fallback: 1 hora

      logger.info('Correios: autenticação bem-sucedida');

    } catch (erro) {
      // Nunca loga a senha — apenas o status do erro
      const status = erro.response?.status;
      const msg    = erro.response?.data?.msgs?.join('; ')
        || erro.response?.data?.message
        || erro.message;
      throw new Error(`Correios: falha na autenticação (HTTP ${status ?? 'sem resposta'}): ${msg}`);
    }
  }

  // ─── Rastreamento ────────────────────────────────────────────────────────

  /**
   * Rastreia um objeto. Retorna objeto normalizado ou null em caso de erro.
   * Nunca lança exceção — registra o erro e retorna null para que o
   * processador pule o pedido sem interromper os demais.
   */
  async rastrearObjeto(codigoRastreio, tentativa = 1) {
    await this.autenticar();

    try {
      const resposta = await this.client.get(
        `/rastro/v1/objetos`,
        {
          params: { codObjeto: codigoRastreio },
          headers: { Authorization: `Bearer ${this._token}` },
        }
      );

      const objetos = resposta.data?.objetos ?? [];

      if (objetos.length === 0) {
        logger.warn(`Correios: nenhum resultado para ${codigoRastreio}`);
        return null;
      }

      return this._normalizarObjeto(objetos[0]);

    } catch (erro) {
      const status = erro.response?.status;

      if (status === 401 || status === 403) {
        // Token expirou durante execução — forçar reautenticação e tentar uma vez
        if (tentativa === 1) {
          logger.warn(`Correios: token inválido para ${codigoRastreio}. Reautenticando...`);
          this._token = null;
          this._tokenExpira = null;
          return this.rastrearObjeto(codigoRastreio, 2);
        }
      }

      if (this._ehErroReintentavel(erro) && tentativa < this.maxTentativas) {
        const espera = 1000 * Math.pow(2, tentativa - 1);
        logger.warn(`Correios: erro temporário para ${codigoRastreio} (tentativa ${tentativa}/${this.maxTentativas}). Aguardando ${espera}ms...`);
        await sleep(espera);
        return this.rastrearObjeto(codigoRastreio, tentativa + 1);
      }

      const msgs = erro.response?.data?.msgs?.join('; ')
        || erro.response?.data?.message
        || erro.message;
      logger.error(`Correios: erro ao rastrear ${codigoRastreio}: ${msgs}`);
      return null;
    }
  }

  // ─── Interpretação de status ─────────────────────────────────────────────

  /**
   * Verifica se o objeto foi entregue ao destinatário.
   * Considera apenas o último evento (primeiro da lista, que é o mais recente).
   */
  estaEntregue(objetoRastreado) {
    if (!objetoRastreado || !objetoRastreado.eventos || objetoRastreado.eventos.length === 0) {
      return false;
    }

    const ultimoEvento = objetoRastreado.eventos[0];
    return this._eventoIndicaEntrega(ultimoEvento);
  }

  /**
   * Extrai a data de entrega do evento mais recente (se for entrega).
   * Retorna string ISO 8601 ou null.
   */
  obterDataEntrega(objetoRastreado) {
    if (!this.estaEntregue(objetoRastreado)) return null;

    const ultimoEvento = objetoRastreado.eventos[0];
    return ultimoEvento.dtHrCriado ?? null;
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  _eventoIndicaEntrega(evento) {
    if (!evento) return false;

    const tipo = (evento.tipo ?? '').trim().toUpperCase();
    if (TIPOS_ENTREGUE.has(tipo)) return true;

    // Fallback: verifica a descrição textual (normaliza acentos e caixa)
    const descricao = (evento.descricao ?? '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    return DESCRICOES_ENTREGUE.some(kw => descricao.includes(kw.normalize('NFD').replace(/[̀-ͯ]/g, '')));
  }

  _normalizarObjeto(obj) {
    return {
      codigo:   obj.codObjeto ?? null,
      eventos:  (obj.eventos ?? []).map(ev => ({
        tipo:        ev.tipo ?? '',
        status:      ev.status ?? '',
        descricao:   ev.descricao ?? '',
        detalhe:     ev.detalhe ?? '',
        dtHrCriado:  ev.dtHrCriado ?? null,
        unidade:     ev.unidade?.nome ?? '',
      })),
    };
  }

  _ehErroReintentavel(erro) {
    if (!erro.response) return true; // erro de rede/timeout
    const status = erro.response.status;
    return status === 429 || status >= 500;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { CorreiosApi, TIPOS_EM_TRANSITO, TIPOS_ENTREGUE };
