'use strict';

/**
 * Cliente para a API GraphQL da Wake Commerce.
 * Neste fluxo a Wake é usada apenas para ATUALIZAR status por número de pedido.
 * Os pedidos e rastreios vêm do Bling.
 *
 * ATENÇÃO: Caso ocorra erro de campo não encontrado, inspecione o schema com:
 *   curl -s -X POST https://api.wake.tech/graphql \
 *     -H "access-token: SEU_TOKEN" \
 *     -H "Content-Type: application/json" \
 *     -d '{"query":"{ __schema { queryType { fields { name } } } }"}' | jq
 */

const axios  = require('axios');
const logger = require('./logger');

// ─── Queries e Mutations ─────────────────────────────────────────────────────

// Busca um pedido pelo número visível (ex.: "12345")
const QUERY_PEDIDO_POR_NUMERO = `
  query GetPedidoPorNumero($number: String) {
    orders(
      filter: { number: $number }
      perPage: 1
    ) {
      nodes {
        id
        number
        status
        cancelledAt
        returnedAt
      }
    }
  }
`;

// Atualiza status do pedido para Entregue
const MUTATION_ATUALIZAR_STATUS = `
  mutation AtualizarStatusEntregue($input: UpdateOrderStatusInput!) {
    updateOrderStatus(input: $input) {
      id
      status
    }
  }
`;

// Adiciona observação interna ao pedido
const MUTATION_ADICIONAR_NOTA = `
  mutation AdicionarNotaPedido($orderId: Long!, $message: String!) {
    addOrderNote(orderId: $orderId, message: $message) {
      id
    }
  }
`;

// ─── Classe cliente ──────────────────────────────────────────────────────────

class WakeApi {
  constructor(config) {
    this.apiUrl        = config.wake.apiUrl;
    this.accessToken   = config.wake.accessToken;
    this.statusEntregue = config.wake.statusEntregue;
    this.maxTentativas = config.limites.maxTentativas;

    this.client = axios.create({
      baseURL: this.apiUrl,
      timeout: 30_000,
      headers: {
        'Content-Type': 'application/json',
        'access-token': this.accessToken,
        'Authorization': `token ${this.accessToken}`,
      },
    });
  }

  // ─── Busca por número de pedido ──────────────────────────────────────────

  /**
   * Busca o ID interno Wake de um pedido pelo seu número visível.
   * Retorna null se não encontrado ou em caso de erro.
   */
  async buscarPedidoPorNumero(numeroPedido) {
    try {
      const dados = await this.executarGraphQL(QUERY_PEDIDO_POR_NUMERO, {
        number: String(numeroPedido),
      });

      const nos = dados?.orders?.nodes ?? [];
      if (nos.length === 0) {
        logger.warn(`Wake: pedido #${numeroPedido} não encontrado`);
        return null;
      }

      const pedido = nos[0];
      return {
        id:          String(pedido.id),
        numero:      String(pedido.number || pedido.id),
        status:      (typeof pedido.status === 'object')
          ? (pedido.status?.value || pedido.status?.name || '')
          : (pedido.status || ''),
        canceladoEm: pedido.cancelledAt || null,
        devolvidoEm: pedido.returnedAt  || null,
      };

    } catch (erro) {
      logger.error(`Wake: erro ao buscar pedido #${numeroPedido}: ${erro.message}`);
      return null;
    }
  }

  // ─── Atualização de pedido ───────────────────────────────────────────────

  /**
   * Atualiza o pedido Wake para status Entregue com data e observação interna.
   */
  async marcarComoEntregue(pedidoId, numeroPedido, dataEntrega) {
    const nota = 'Pedido atualizado automaticamente como entregue após confirmação no rastreamento dos Correios.';

    // 1. Atualizar status
    await this.executarGraphQL(MUTATION_ATUALIZAR_STATUS, {
      input: {
        orderId:     pedidoId,
        status:      this.statusEntregue,
        deliveredAt: dataEntrega,
      },
    });

    logger.info(`Wake: pedido #${numeroPedido} → ${this.statusEntregue}`);

    // 2. Adicionar nota interna (falha aqui não cancela o fluxo)
    try {
      await this.executarGraphQL(MUTATION_ADICIONAR_NOTA, {
        orderId: pedidoId,
        message: nota,
      });
    } catch (erroNota) {
      logger.warn(`Wake: não foi possível adicionar nota ao pedido #${numeroPedido}: ${erroNota.message}`);
    }
  }

  // ─── Execução de GraphQL ─────────────────────────────────────────────────

  async executarGraphQL(query, variables = {}, tentativa = 1) {
    try {
      const resposta = await this.client.post('', { query, variables });

      if (resposta.data.errors?.length) {
        const erros = resposta.data.errors.map(e => e.message).join('; ');
        throw new Error(`Erro GraphQL Wake: ${erros}`);
      }

      return resposta.data.data;

    } catch (erro) {
      if (this._ehReintentavel(erro) && tentativa < this.maxTentativas) {
        const espera = 1000 * Math.pow(2, tentativa - 1);
        logger.warn(`Wake: erro temporário (tentativa ${tentativa}/${this.maxTentativas}). Aguardando ${espera}ms...`);
        await sleep(espera);
        return this.executarGraphQL(query, variables, tentativa + 1);
      }
      throw this._envolverErro(erro);
    }
  }

  _ehReintentavel(erro) {
    if (!erro.response) return true;
    return erro.response.status === 429 || erro.response.status >= 500;
  }

  _envolverErro(erro) {
    const msg = erro.response?.data?.message
      || erro.response?.statusText
      || erro.message
      || 'Erro desconhecido';
    const novo = new Error(`Wake API: ${msg}`);
    novo.statusHttp = erro.response?.status;
    return novo;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { WakeApi };
