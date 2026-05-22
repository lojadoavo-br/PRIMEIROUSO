'use strict';

/**
 * Cliente para a API GraphQL da Wake Commerce.
 *
 * ATENÇÃO: A Wake pode atualizar o schema GraphQL. Caso ocorra erro de campo
 * não encontrado, consulte: https://api.wake.tech/graphql (introspection)
 * e ajuste as queries abaixo conforme necessário.
 */

const axios  = require('axios');
const logger = require('./logger');

// ─── Queries e Mutations ─────────────────────────────────────────────────────

/**
 * Busca pedidos com status que devem ser verificados nos Correios.
 * Filtra apenas pedidos com código de rastreio preenchido.
 *
 * Campos retornados que você pode precisar ajustar ao seu schema Wake:
 *   - shippingInfo.trackingCode   → pode ser tracking.code ou trackingCode
 *   - shippingInfo.carrierName    → pode ser carrier ou shippingMethod.name
 *   - status.value                → pode ser apenas status (string)
 *   - deliveredAt                 → pode ser deliveredDate
 */
const QUERY_PEDIDOS = `
  query GetPedidosParaVerificar($page: Int, $perPage: Int, $status: [String]) {
    orders(
      page: $page
      perPage: $perPage
      filter: { status: $status }
    ) {
      totalCount
      nodes {
        id
        number
        status
        shippingInfo {
          trackingCode
          carrierName
        }
        deliveredAt
        cancelledAt
        returnedAt
      }
    }
  }
`;

/**
 * Atualiza o status do pedido para Entregue na Wake.
 *
 * Ajuste o nome da mutation se necessário:
 *   - updateOrderStatus  (mais comum na Wake v2)
 *   - checkoutStatus     (variação legacy)
 *   - updateOrder        (variação alternativa)
 */
const MUTATION_ATUALIZAR_STATUS = `
  mutation AtualizarStatusEntregue($input: UpdateOrderStatusInput!) {
    updateOrderStatus(input: $input) {
      id
      status
    }
  }
`;

/**
 * Adiciona observação interna ao pedido.
 * Ajuste o nome da mutation se necessário (addOrderNote, createOrderNote, etc.)
 */
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
    this.apiUrl      = config.wake.apiUrl;
    this.accessToken = config.wake.accessToken;
    this.maxTentativas = config.limites.maxTentativas;

    this.client = axios.create({
      baseURL: this.apiUrl,
      timeout: 30_000,
      headers: {
        'Content-Type': 'application/json',
        // Wake aceita tanto "access-token" quanto "Authorization: token ..."
        // Ajuste o header se necessário para sua configuração:
        'access-token': this.accessToken,
        'Authorization': `token ${this.accessToken}`,
      },
    });
  }

  // ─── Execução de GraphQL ─────────────────────────────────────────────────

  async executarGraphQL(query, variables = {}, tentativa = 1) {
    try {
      const resposta = await this.client.post('', { query, variables });

      if (resposta.data.errors && resposta.data.errors.length > 0) {
        const erros = resposta.data.errors.map(e => e.message).join('; ');
        throw new Error(`Erro GraphQL Wake: ${erros}`);
      }

      return resposta.data.data;

    } catch (erro) {
      const reintentavel = this._ehErroReintentavel(erro);

      if (reintentavel && tentativa < this.maxTentativas) {
        const espera = 1000 * Math.pow(2, tentativa - 1);
        logger.warn(`Wake API: erro temporário (tentativa ${tentativa}/${this.maxTentativas}). Aguardando ${espera}ms...`);
        await sleep(espera);
        return this.executarGraphQL(query, variables, tentativa + 1);
      }

      throw this._envolverErro(erro, 'Wake API');
    }
  }

  // ─── Busca de pedidos ────────────────────────────────────────────────────

  /**
   * Retorna todos os pedidos que devem ser verificados nos Correios.
   * Faz paginação automática respeitando o limite configurado.
   */
  async buscarPedidosParaVerificar(statusVerificar, limite) {
    const pedidos = [];
    const porPagina = Math.min(50, limite);
    let pagina = 1;
    let totalPaginas = 1;

    logger.info(`Wake: buscando pedidos com status: ${statusVerificar.join(', ')}`);

    do {
      const dados = await this.executarGraphQL(QUERY_PEDIDOS, {
        page: pagina,
        perPage: porPagina,
        status: statusVerificar,
      });

      const nos = dados?.orders?.nodes ?? [];
      const total = dados?.orders?.totalCount ?? 0;
      totalPaginas = Math.ceil(total / porPagina);

      for (const pedido of nos) {
        if (pedidos.length >= limite) break;

        const normalizado = this._normalizarPedido(pedido);
        if (normalizado) pedidos.push(normalizado);
      }

      logger.info(`Wake: página ${pagina}/${totalPaginas} — ${pedidos.length}/${Math.min(total, limite)} pedidos carregados`);
      pagina++;

      if (pagina <= totalPaginas && pedidos.length < limite) {
        await sleep(300);
      }

    } while (pagina <= totalPaginas && pedidos.length < limite);

    return pedidos;
  }

  // ─── Atualização de pedido ───────────────────────────────────────────────

  /**
   * Atualiza o pedido para status Entregue com data e observação interna.
   */
  async marcarComoEntregue(pedidoId, statusEntregue, dataEntrega, nota) {
    // 1. Atualizar o status
    const inputStatus = {
      orderId:     pedidoId,
      status:      statusEntregue,
      deliveredAt: dataEntrega,
    };

    const dadosStatus = await this.executarGraphQL(MUTATION_ATUALIZAR_STATUS, {
      input: inputStatus,
    });

    logger.info(`Wake: pedido ${pedidoId} status atualizado → ${statusEntregue}`);

    // 2. Adicionar nota interna (erro aqui não interrompe — apenas loga)
    try {
      await this.executarGraphQL(MUTATION_ADICIONAR_NOTA, {
        orderId: pedidoId,
        message: nota,
      });
      logger.info(`Wake: nota interna adicionada ao pedido ${pedidoId}`);
    } catch (erroNota) {
      logger.warn(`Wake: não foi possível adicionar nota ao pedido ${pedidoId}: ${erroNota.message}`);
    }

    return dadosStatus?.updateOrderStatus ?? null;
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  _normalizarPedido(pedido) {
    if (!pedido) return null;

    // Suporte a diferentes estruturas de campo da Wake
    const rastreio = pedido.shippingInfo?.trackingCode
      || pedido.tracking?.code
      || pedido.trackingCode
      || null;

    const transportadora = pedido.shippingInfo?.carrierName
      || pedido.tracking?.carrier
      || pedido.shippingMethod?.name
      || pedido.carrier
      || '';

    const status = (typeof pedido.status === 'object')
      ? (pedido.status?.value || pedido.status?.name || '')
      : (pedido.status || '');

    return {
      id:            String(pedido.id),
      numero:        String(pedido.number || pedido.id),
      status:        status,
      rastreio:      rastreio ? rastreio.trim().toUpperCase() : null,
      transportadora: transportadora,
      entregueEm:    pedido.deliveredAt || null,
      canceladoEm:   pedido.cancelledAt || null,
      devolvidoEm:   pedido.returnedAt  || null,
    };
  }

  _ehErroReintentavel(erro) {
    if (!erro.response) return true; // erro de rede
    const status = erro.response.status;
    return status === 429 || status >= 500;
  }

  _envolverErro(erro, contexto) {
    const msg = erro.response?.data?.message
      || erro.response?.statusText
      || erro.message
      || 'Erro desconhecido';
    const novo = new Error(`${contexto}: ${msg}`);
    novo.statusHttp = erro.response?.status;
    novo.original   = erro;
    return novo;
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { WakeApi };
