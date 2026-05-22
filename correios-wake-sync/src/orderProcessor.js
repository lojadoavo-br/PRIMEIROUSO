'use strict';

/**
 * Processador principal.
 *
 * Fluxo:
 *   1. Busca pedidos no Bling (fonte dos rastreios)
 *   2. Para cada pedido: valida → consulta Correios → se entregue:
 *      a. Atualiza status no Bling
 *      b. Busca o pedido equivalente na Wake por número → atualiza status na Wake
 */

const logger = require('./logger');

// Padrão de código de rastreio dos Correios: ex. AA123456789BR
const REGEX_RASTREIO_CORREIOS = /^[A-Z]{2}\d{9}[A-Z]{2}$/;

// Palavras no nome da transportadora que identificam os Correios
const NOMES_CORREIOS = [
  'correios', 'correio', 'ect', 'empresa brasileira de correios',
  'sedex', 'pac',
];

// Situações/status que bloqueiam qualquer atualização
const STATUS_BLOQUEADOS = [
  'cancelado', 'devolvido', 'devolucao', 'devolução',
  'troca', 'reversa', 'logistica reversa', 'logística reversa',
  'contestacao', 'contestação', 'disputa', 'chargeback',
];

class OrdemProcessador {
  constructor({ blingApi, wakeApi, correiosApi, config }) {
    this.blingApi    = blingApi;
    this.wakeApi     = wakeApi;
    this.correiosApi = correiosApi;
    this.config      = config;

    this.stats = {
      totalAnalisados:    0,
      semRastreio:        0,
      naoCorreios:        0,
      statusBloqueado:    0,
      correiosErro:       0,
      emTransito:         0,
      entregues:          0,
      atualizadosBling:   0,
      atualizadosWake:    0,
      ignoradosDryRun:    0,
      errosBling:         0,
      errosWake:          0,
      pedidosAtualizados: [],
      pedidosIgnorados:   [],
      erros:              [],
    };
  }

  // ─── Orquestração principal ──────────────────────────────────────────────

  async processar() {
    const { isDryRun, bling, limites } = this.config;

    logger.info('═'.repeat(60));
    logger.info(`MODO: ${isDryRun ? '🔍 SIMULAÇÃO (nada será alterado)' : '⚡ PRODUÇÃO'}`);
    logger.info('Fonte de pedidos: Bling | Atualiza: Bling + Wake');
    logger.info('═'.repeat(60));

    // 1. Buscar pedidos no Bling
    const pedidos = await this.blingApi.buscarPedidosParaVerificar(
      bling.situacoesVerificar,
      bling.maxPedidos
    );

    this.stats.totalAnalisados = pedidos.length;
    logger.info(`\nTotal de pedidos encontrados no Bling: ${pedidos.length}`);

    if (pedidos.length === 0) {
      logger.info('Nenhum pedido para processar.');
      return this.stats;
    }

    // 2. Processar cada pedido
    for (let i = 0; i < pedidos.length; i++) {
      const pedido = pedidos[i];
      logger.info(`\n[${i + 1}/${pedidos.length}] Pedido Bling #${pedido.numero} | Rastreio: ${pedido.rastreio ?? 'ausente'} | Situação: ${pedido.situacaoNome}`);

      await this._processarPedido(pedido, isDryRun);

      if (i < pedidos.length - 1) {
        await sleep(limites.intervaloPedidosMs);
      }
    }

    return this.stats;
  }

  // ─── Processamento individual ────────────────────────────────────────────

  async _processarPedido(pedido, isDryRun) {
    // Regra: não processar sem rastreio
    if (!pedido.rastreio) {
      logger.info(`  → Ignorado: sem código de rastreio`);
      this.stats.semRastreio++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: 'sem_rastreio' });
      return;
    }

    // Regra: rastreio deve ter formato Correios
    if (!REGEX_RASTREIO_CORREIOS.test(pedido.rastreio)) {
      logger.info(`  → Ignorado: "${pedido.rastreio}" não é formato Correios`);
      this.stats.naoCorreios++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: 'rastreio_nao_correios' });
      return;
    }

    // Regra: verificar nome da transportadora (quando preenchido)
    if (pedido.transportadora && !this._ehCorreios(pedido.transportadora)) {
      logger.info(`  → Ignorado: transportadora "${pedido.transportadora}" não é Correios`);
      this.stats.naoCorreios++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: `transportadora_nao_correios:${pedido.transportadora}` });
      return;
    }

    // Regra: não processar situações bloqueadas (cancelado, devolvido, etc.)
    if (this._statusBloqueado(pedido.situacaoNome)) {
      logger.info(`  → Ignorado: situação bloqueada (${pedido.situacaoNome})`);
      this.stats.statusBloqueado++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: `situacao_bloqueada:${pedido.situacaoNome}` });
      return;
    }

    // Consultar Correios
    await sleep(this.config.limites.intervaloCorreiosMs);
    const rastreado = await this.correiosApi.rastrearObjeto(pedido.rastreio);

    if (!rastreado) {
      logger.warn(`  → Correios: falha ao rastrear — pedido ignorado nesta execução`);
      this.stats.correiosErro++;
      this.stats.erros.push({ pedido: pedido.numero, rastreio: pedido.rastreio, erro: 'Falha na API dos Correios' });
      return;
    }

    const ultimoEvento = rastreado.eventos[0] ?? {};
    logger.info(`  → Correios: [${ultimoEvento.tipo}] ${ultimoEvento.descricao} (${ultimoEvento.dtHrCriado ?? 'sem data'})`);

    if (!this.correiosApi.estaEntregue(rastreado)) {
      logger.info(`  → Em trânsito: nenhuma ação`);
      this.stats.emTransito++;
      this.stats.pedidosIgnorados.push({
        ...pedido,
        motivo:         'em_transito',
        ultimoEvento:   `[${ultimoEvento.tipo}] ${ultimoEvento.descricao}`,
        dtUltimoEvento: ultimoEvento.dtHrCriado,
      });
      return;
    }

    // Confirmado como entregue
    const dataEntrega = this.correiosApi.obterDataEntrega(rastreado);
    this.stats.entregues++;
    logger.info(`  → ENTREGUE em ${dataEntrega ?? 'data não informada'}`);

    if (isDryRun) {
      logger.info(`  → [SIMULAÇÃO] Seria atualizado no Bling e na Wake`);
      this.stats.ignoradosDryRun++;
      this.stats.pedidosAtualizados.push({
        pedido:           pedido.numero,
        rastreio:         pedido.rastreio,
        situacaoBling:    pedido.situacaoNome,
        statusCorreios:   `[${ultimoEvento.tipo}] ${ultimoEvento.descricao}`,
        dataEntrega,
        blingAtualizado:  'simulação',
        wakeAtualizado:   'simulação',
      });
      return;
    }

    // Modo produção
    const resultado = {
      pedido:           pedido.numero,
      rastreio:         pedido.rastreio,
      situacaoBling:    pedido.situacaoNome,
      statusCorreios:   `[${ultimoEvento.tipo}] ${ultimoEvento.descricao}`,
      dataEntrega,
      blingAtualizado:  false,
      wakeAtualizado:   false,
    };

    // Atualizar Bling
    try {
      await this.blingApi.marcarComoEntregue(
        pedido.id,
        this.config.bling.situacaoEntregueId,
        dataEntrega
      );
      resultado.blingAtualizado = true;
      this.stats.atualizadosBling++;
    } catch (erroBling) {
      logger.error(`  → Erro ao atualizar Bling: ${erroBling.message}`);
      this.stats.errosBling++;
      this.stats.erros.push({ pedido: pedido.numero, rastreio: pedido.rastreio, erro: `Bling: ${erroBling.message}` });
    }

    // Atualizar Wake (busca por número de pedido, pois o rastreio não está lá)
    try {
      const pedidoWake = await this.wakeApi.buscarPedidoPorNumero(pedido.numero);

      if (!pedidoWake) {
        logger.warn(`  → Wake: pedido #${pedido.numero} não encontrado — Wake não atualizado`);
        this.stats.erros.push({ pedido: pedido.numero, rastreio: pedido.rastreio, erro: 'Wake: pedido não encontrado por número' });
      } else if (this._statusBloqueado(pedidoWake.status) || pedidoWake.canceladoEm || pedidoWake.devolvidoEm) {
        logger.warn(`  → Wake: pedido #${pedido.numero} está em status bloqueado na Wake (${pedidoWake.status}) — Wake não atualizado`);
      } else {
        await this.wakeApi.marcarComoEntregue(pedidoWake.id, pedido.numero, dataEntrega);
        resultado.wakeAtualizado = true;
        this.stats.atualizadosWake++;
      }
    } catch (erroWake) {
      logger.error(`  → Erro ao atualizar Wake: ${erroWake.message}`);
      this.stats.errosWake++;
      this.stats.erros.push({ pedido: pedido.numero, rastreio: pedido.rastreio, erro: `Wake: ${erroWake.message}` });
    }

    this.stats.pedidosAtualizados.push(resultado);
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  _statusBloqueado(status) {
    if (!status) return false;
    const norm = status.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    return STATUS_BLOQUEADOS.some(b => norm.includes(b.normalize('NFD').replace(/[̀-ͯ]/g, '')));
  }

  _ehCorreios(transportadora) {
    const norm = transportadora.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    return NOMES_CORREIOS.some(n => norm.includes(n.normalize('NFD').replace(/[̀-ͯ]/g, '')));
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { OrdemProcessador };
