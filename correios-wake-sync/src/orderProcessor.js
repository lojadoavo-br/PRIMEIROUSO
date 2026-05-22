'use strict';

const logger = require('./logger');

// Padrões de código de rastreio dos Correios (ex.: AA123456789BR, RR123456789BR)
const REGEX_RASTREIO_CORREIOS = /^[A-Z]{2}\d{9}[A-Z]{2}$/;

// Palavras-chave no nome da transportadora que identificam os Correios
const NOMES_CORREIOS = [
  'correios', 'correio', 'ect', 'empresa brasileira de correios',
  'sedex', 'pac', 'carta', 'encomenda',
];

// Status de pedido Wake que bloqueiam qualquer atualização
const STATUS_BLOQUEADOS = [
  'cancelado', 'devolvido', 'devolucao', 'devolução',
  'troca', 'reversa', 'logistica reversa', 'logística reversa',
  'contestacao', 'contestação', 'disputa', 'chargeback',
];

class OrdemProcessador {
  constructor({ wakeApi, correiosApi, config }) {
    this.wakeApi     = wakeApi;
    this.correiosApi = correiosApi;
    this.config      = config;

    this.stats = {
      totalAnalisados:  0,
      semRastreio:      0,
      semCorreios:      0,
      statusBloqueado:  0,
      correiosErro:     0,
      emTransito:       0,
      entregues:        0,
      atualizados:      0,
      ignoradosDryRun:  0,
      errosWake:        0,
      pedidosAtualizados: [],
      pedidosIgnorados:   [],
      erros:              [],
    };
  }

  // ─── Processamento principal ─────────────────────────────────────────────

  async processar() {
    const { isDryRun, wake, limites } = this.config;

    logger.info('═'.repeat(60));
    logger.info(`MODO: ${isDryRun ? '🔍 SIMULAÇÃO (nenhum pedido será alterado)' : '⚡ PRODUÇÃO'}`);
    logger.info('═'.repeat(60));

    // 1. Buscar pedidos na Wake
    const pedidos = await this.wakeApi.buscarPedidosParaVerificar(
      wake.statusVerificar,
      wake.maxPedidos
    );

    this.stats.totalAnalisados = pedidos.length;
    logger.info(`\nTotal de pedidos encontrados: ${pedidos.length}`);

    if (pedidos.length === 0) {
      logger.info('Nenhum pedido para processar.');
      return this.stats;
    }

    // 2. Processar cada pedido
    for (let i = 0; i < pedidos.length; i++) {
      const pedido = pedidos[i];
      logger.info(`\n[${i + 1}/${pedidos.length}] Pedido #${pedido.numero} — rastreio: ${pedido.rastreio ?? 'ausente'}`);

      await this._processarPedido(pedido, isDryRun);

      // Respeita rate limit entre pedidos
      if (i < pedidos.length - 1) {
        await sleep(limites.intervaloPedidosMs);
      }
    }

    return this.stats;
  }

  // ─── Processamento individual ────────────────────────────────────────────

  async _processarPedido(pedido, isDryRun) {
    // Regra: não processar pedidos sem rastreio
    if (!pedido.rastreio) {
      logger.info(`  → Ignorado: sem código de rastreio`);
      this.stats.semRastreio++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: 'sem_rastreio' });
      return;
    }

    // Regra: não processar pedidos com status bloqueado
    const statusBloqueado = this._verificarStatusBloqueado(pedido.status);
    if (statusBloqueado) {
      logger.info(`  → Ignorado: status bloqueado (${pedido.status})`);
      this.stats.statusBloqueado++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: `status_bloqueado:${pedido.status}` });
      return;
    }

    // Regra: não processar rastreio com formato inválido para os Correios
    if (!REGEX_RASTREIO_CORREIOS.test(pedido.rastreio)) {
      logger.info(`  → Ignorado: rastreio "${pedido.rastreio}" não é formato Correios`);
      this.stats.semCorreios++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: 'rastreio_nao_correios' });
      return;
    }

    // Regra: apenas Correios
    if (!this._ehCorreios(pedido.transportadora, pedido.rastreio)) {
      logger.info(`  → Ignorado: transportadora "${pedido.transportadora}" não é Correios`);
      this.stats.semCorreios++;
      this.stats.pedidosIgnorados.push({ ...pedido, motivo: `transportadora_nao_correios:${pedido.transportadora}` });
      return;
    }

    // Consultar Correios
    await sleep(this.config.limites.intervaloCorreiosMs);
    const rastreado = await this.correiosApi.rastrearObjeto(pedido.rastreio);

    if (!rastreado) {
      logger.warn(`  → Correios: falha ao rastrear ${pedido.rastreio} — pedido ignorado`);
      this.stats.correiosErro++;
      this.stats.erros.push({
        pedido:  pedido.numero,
        rastreio: pedido.rastreio,
        erro:    'Falha na consulta à API dos Correios',
      });
      return;
    }

    const ultimoEvento = rastreado.eventos[0] ?? {};
    logger.info(`  → Correios: último evento: [${ultimoEvento.tipo}] ${ultimoEvento.descricao} (${ultimoEvento.dtHrCriado ?? 'sem data'})`);

    // Regra: apenas atualizar se confirmado como entregue
    if (!this.correiosApi.estaEntregue(rastreado)) {
      logger.info(`  → Não entregue: pedido em trânsito ou sem evento de entrega`);
      this.stats.emTransito++;
      this.stats.pedidosIgnorados.push({
        ...pedido,
        motivo:         'em_transito',
        ultimoEvento:   `[${ultimoEvento.tipo}] ${ultimoEvento.descricao}`,
        dtUltimoEvento: ultimoEvento.dtHrCriado,
      });
      return;
    }

    // Pedido está entregue
    const dataEntrega = this.correiosApi.obterDataEntrega(rastreado);
    this.stats.entregues++;

    if (isDryRun) {
      logger.info(`  → [SIMULAÇÃO] Seria atualizado: entregue em ${dataEntrega ?? 'data desconhecida'}`);
      this.stats.ignoradosDryRun++;
      this.stats.pedidosAtualizados.push({
        pedido:       pedido.numero,
        rastreio:     pedido.rastreio,
        statusWake:   pedido.status,
        statusCorreios: `[${ultimoEvento.tipo}] ${ultimoEvento.descricao}`,
        dataEntrega:  dataEntrega,
        simulacao:    true,
      });
      return;
    }

    // Modo produção: atualizar na Wake
    await this._atualizarNaWake(pedido, dataEntrega, ultimoEvento);
  }

  async _atualizarNaWake(pedido, dataEntrega, ultimoEvento) {
    const nota = 'Pedido atualizado automaticamente como entregue após confirmação no rastreamento dos Correios.';

    try {
      await this.wakeApi.marcarComoEntregue(
        pedido.id,
        this.config.wake.statusEntregue,
        dataEntrega,
        nota
      );

      logger.info(`  → Atualizado na Wake: pedido #${pedido.numero} → ${this.config.wake.statusEntregue}`);
      this.stats.atualizados++;
      this.stats.pedidosAtualizados.push({
        pedido:         pedido.numero,
        rastreio:       pedido.rastreio,
        statusWake:     pedido.status,
        statusCorreios: `[${ultimoEvento.tipo}] ${ultimoEvento.descricao}`,
        dataEntrega:    dataEntrega,
        simulacao:      false,
      });

    } catch (erroWake) {
      logger.error(`  → Erro ao atualizar pedido #${pedido.numero} na Wake: ${erroWake.message}`);
      this.stats.errosWake++;
      this.stats.erros.push({
        pedido:  pedido.numero,
        rastreio: pedido.rastreio,
        erro:    `Wake API: ${erroWake.message}`,
      });
    }
  }

  // ─── Helpers ─────────────────────────────────────────────────────────────

  _verificarStatusBloqueado(status) {
    if (!status) return false;
    const statusNorm = status.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    return STATUS_BLOQUEADOS.some(bloqueado =>
      statusNorm.includes(bloqueado.normalize('NFD').replace(/[̀-ͯ]/g, ''))
    );
  }

  _ehCorreios(transportadora, rastreio) {
    // O formato do rastreio dos Correios é suficiente como identificador primário
    // quando o nome da transportadora não está disponível
    if (!transportadora || transportadora.trim() === '') {
      return REGEX_RASTREIO_CORREIOS.test(rastreio);
    }

    const nomeNorm = transportadora.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    return NOMES_CORREIOS.some(nome =>
      nomeNorm.includes(nome.normalize('NFD').replace(/[̀-ͯ]/g, ''))
    );
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { OrdemProcessador };
