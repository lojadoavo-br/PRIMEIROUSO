'use strict';

/**
 * Cliente para a API v3 do Bling.
 *
 * Documentação: https://developer.bling.com.br/referencia
 *
 * Autenticação: OAuth2 com refresh_token.
 * Fluxo inicial (uma vez só, manual):
 *   1. Crie um app em: https://developer.bling.com.br
 *   2. Faça a autorização inicial e copie o refresh_token gerado
 *   3. Coloque o refresh_token no .env — a automação renova automaticamente
 */

const axios  = require('axios');
const logger = require('./logger');

// IDs de situação do Bling que indicam pedido "em rota" (verificar nos Correios)
// Confirme os IDs corretos em: Bling → Configurações → Situações de Pedido
const SITUACOES_PADRAO_VERIFICAR = [9, 12, 15]; // Em andamento, Atendido, Em aberto

class BlingApi {
  constructor(config) {
    this.apiUrl       = config.bling.apiUrl;
    this.clientId     = config.bling.clientId;
    this.clientSecret = config.bling.clientSecret;
    this.maxTentativas = config.limites.maxTentativas;

    // Refresh token — nunca logado
    this._refreshToken  = config.bling._refreshToken;
    this._accessToken   = null;
    this._tokenExpira   = null;

    this.client = axios.create({
      baseURL: this.apiUrl,
      timeout: 30_000,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  // ─── Autenticação OAuth2 ─────────────────────────────────────────────────

  async autenticar() {
    if (this._accessToken && this._tokenExpira && Date.now() < this._tokenExpira - 60_000) {
      return;
    }

    logger.info('Bling: renovando access token...');

    const credencialBase64 = Buffer
      .from(`${this.clientId}:${this.clientSecret}`)
      .toString('base64');

    try {
      const resposta = await axios.post(
        `${this.apiUrl}/oauth/token`,
        new URLSearchParams({
          grant_type:    'refresh_token',
          refresh_token: this._refreshToken,
        }).toString(),
        {
          headers: {
            'Authorization': `Basic ${credencialBase64}`,
            'Content-Type':  'application/x-www-form-urlencoded',
          },
        }
      );

      const dados = resposta.data;
      this._accessToken  = dados.access_token;
      // Bling retorna expires_in em segundos
      this._tokenExpira  = Date.now() + (dados.expires_in ?? 21600) * 1000;

      // Atualiza o refresh_token se vier um novo (rotação)
      if (dados.refresh_token) {
        this._refreshToken = dados.refresh_token;
      }

      logger.info('Bling: access token renovado com sucesso');

    } catch (erro) {
      const status = erro.response?.status;
      const msg    = erro.response?.data?.error_description
        || erro.response?.data?.message
        || erro.message;
      throw new Error(`Bling: falha na autenticação (HTTP ${status ?? 'sem resposta'}): ${msg}`);
    }
  }

  _authHeader() {
    return { Authorization: `Bearer ${this._accessToken}` };
  }

  // ─── Busca de pedidos ────────────────────────────────────────────────────

  /**
   * Retorna pedidos com as situações configuradas que tenham código de rastreio.
   * Pagina automaticamente até o limite configurado.
   */
  async buscarPedidosParaVerificar(situacoesIds, limite) {
    await this.autenticar();

    const pedidos = [];
    const porPagina = 100;
    let pagina = 1;
    let temMais = true;

    // Monta filtro de situações (Bling aceita múltiplos: &situacoes[]=9&situacoes[]=15)
    const paramSituacoes = situacoesIds
      .map(id => `situacoes[]=${id}`)
      .join('&');

    logger.info(`Bling: buscando pedidos com situações [${situacoesIds.join(', ')}]...`);

    while (temMais && pedidos.length < limite) {
      const url = `/pedidos/vendas?${paramSituacoes}&limite=${porPagina}&pagina=${pagina}`;

      const dados = await this._get(url);
      const items = dados?.data ?? [];

      for (const item of items) {
        if (pedidos.length >= limite) break;
        const normalizado = this._normalizarPedido(item);
        if (normalizado) pedidos.push(normalizado);
      }

      logger.info(`Bling: página ${pagina} — ${items.length} pedidos recebidos (total acumulado: ${pedidos.length})`);

      temMais = items.length === porPagina;
      pagina++;

      if (temMais && pedidos.length < limite) await sleep(400);
    }

    return pedidos;
  }

  // ─── Atualização de status ───────────────────────────────────────────────

  /**
   * Atualiza a situação do pedido no Bling para "Entregue".
   */
  async marcarComoEntregue(pedidoId, situacaoId, dataEntrega) {
    await this.autenticar();

    const body = {
      situacao: { id: situacaoId },
    };

    if (dataEntrega) {
      // Bling espera data no formato DD/MM/YYYY
      body.dataEntrega = this._formatarDataBling(dataEntrega);
    }

    await this._patch(`/pedidos/vendas/${pedidoId}`, body);
    logger.info(`Bling: pedido ${pedidoId} atualizado → situação ${situacaoId}`);
  }

  // ─── Helpers HTTP ────────────────────────────────────────────────────────

  async _get(url, tentativa = 1) {
    await this.autenticar();
    try {
      const resp = await this.client.get(url, { headers: this._authHeader() });
      return resp.data;
    } catch (erro) {
      return this._tratar(erro, () => this._get(url, tentativa + 1), tentativa);
    }
  }

  async _patch(url, body, tentativa = 1) {
    await this.autenticar();
    try {
      const resp = await this.client.patch(url, body, { headers: this._authHeader() });
      return resp.data;
    } catch (erro) {
      return this._tratar(erro, () => this._patch(url, body, tentativa + 1), tentativa);
    }
  }

  async _tratar(erro, retry, tentativa) {
    if (erro.response?.status === 401) {
      // Token expirou — forçar renovação
      this._accessToken = null;
    }
    if (this._ehReintentavel(erro) && tentativa < this.maxTentativas) {
      const espera = 1000 * Math.pow(2, tentativa - 1);
      logger.warn(`Bling: erro temporário (tentativa ${tentativa}/${this.maxTentativas}). Aguardando ${espera}ms...`);
      await sleep(espera);
      return retry();
    }
    const msg = erro.response?.data?.error?.message
      || erro.response?.data?.message
      || erro.message;
    throw new Error(`Bling API: ${msg}`);
  }

  _ehReintentavel(erro) {
    if (!erro.response) return true;
    return erro.response.status === 401 || erro.response.status === 429 || erro.response.status >= 500;
  }

  // ─── Normalização ────────────────────────────────────────────────────────

  _normalizarPedido(item) {
    if (!item) return null;

    // O rastreio fica em transporte.volumes[].numeracao
    const volumes   = item.transporte?.volumes ?? [];
    const rastreios = volumes
      .map(v => (v.numeracao ?? '').trim().toUpperCase())
      .filter(Boolean);

    // Pega o primeiro rastreio não vazio
    const rastreio = rastreios[0] ?? null;

    const transportadora = item.transporte?.transportadora?.nome
      || item.transporte?.nomeTransportadora
      || '';

    const situacao = item.situacao ?? {};

    return {
      id:            String(item.id),
      numero:        String(item.numero || item.id),
      situacaoId:    situacao.id ?? null,
      situacaoNome:  situacao.nome ?? '',
      rastreio,
      transportadora,
      dataPrevista:  item.dataPrevista ?? null,
    };
  }

  _formatarDataBling(isoDate) {
    // "2024-01-15T10:30:00-03:00" → "15/01/2024"
    const d = new Date(isoDate);
    if (isNaN(d.getTime())) return null;
    const dia = String(d.getDate()).padStart(2, '0');
    const mes = String(d.getMonth() + 1).padStart(2, '0');
    return `${dia}/${mes}/${d.getFullYear()}`;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { BlingApi, SITUACOES_PADRAO_VERIFICAR };
