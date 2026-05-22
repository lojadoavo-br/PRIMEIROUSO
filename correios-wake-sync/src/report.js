'use strict';

const fs     = require('fs');
const path   = require('path');
const logger = require('./logger');

function gerarRelatorio(stats, isDryRun, inicio) {
  const fim     = new Date();
  const duracao = ((fim - inicio) / 1000).toFixed(1);
  const modo    = isDryRun ? 'SIMULAÇÃO' : 'PRODUÇÃO';

  const linhas = [
    '═'.repeat(60),
    `RELATÓRIO FINAL — MODO ${modo}`,
    `Data/hora: ${fim.toISOString()}`,
    `Duração:   ${duracao}s`,
    '─'.repeat(60),
    'RESUMO GERAL:',
    `  Total de pedidos analisados:      ${stats.totalAnalisados}`,
    `  Sem código de rastreio:           ${stats.semRastreio}`,
    `  Rastreio/transportadora ≠ Correios: ${stats.naoCorreios}`,
    `  Situação bloqueada:               ${stats.statusBloqueado}`,
    `  Erro na API dos Correios:         ${stats.correiosErro}`,
    `  Em trânsito (não entregues):      ${stats.emTransito}`,
    `  Confirmados como entregues:       ${stats.entregues}`,
  ];

  if (isDryRun) {
    linhas.push(`  [SIMULAÇÃO] Seriam atualizados:   ${stats.ignoradosDryRun}`);
  } else {
    linhas.push(`  Atualizados no Bling:             ${stats.atualizadosBling}`);
    linhas.push(`  Atualizados na Wake:              ${stats.atualizadosWake}`);
    linhas.push(`  Erros Bling:                      ${stats.errosBling}`);
    linhas.push(`  Erros Wake:                       ${stats.errosWake}`);
  }

  if (stats.pedidosAtualizados.length > 0) {
    linhas.push('─'.repeat(60));
    linhas.push(isDryRun ? 'PEDIDOS QUE SERIAM ATUALIZADOS:' : 'PEDIDOS ATUALIZADOS:');
    for (const p of stats.pedidosAtualizados) {
      linhas.push(`  Pedido #${p.pedido} | Rastreio: ${p.rastreio}`);
      linhas.push(`    Situação Bling:   ${p.situacaoBling}`);
      linhas.push(`    Evento Correios:  ${p.statusCorreios}`);
      linhas.push(`    Data entrega:     ${p.dataEntrega ?? 'não informada'}`);
      if (!isDryRun) {
        linhas.push(`    Bling atualizado: ${p.blingAtualizado ? 'Sim' : 'Não'} | Wake atualizada: ${p.wakeAtualizado ? 'Sim' : 'Não'}`);
      }
    }
  }

  if (stats.pedidosIgnorados.length > 0) {
    linhas.push('─'.repeat(60));
    linhas.push('PEDIDOS IGNORADOS:');
    for (const p of stats.pedidosIgnorados) {
      const detalhe = p.ultimoEvento ? ` — ${p.ultimoEvento}` : '';
      linhas.push(`  Pedido #${p.numero} | Rastreio: ${p.rastreio ?? 'ausente'} | ${p.motivo}${detalhe}`);
    }
  }

  if (stats.erros.length > 0) {
    linhas.push('─'.repeat(60));
    linhas.push('ERROS:');
    for (const e of stats.erros) {
      linhas.push(`  Pedido #${e.pedido} | ${e.erro}`);
    }
  }

  linhas.push('═'.repeat(60));

  logger.info('\n' + linhas.join('\n'));

  // Salvar JSON para integração (n8n, dashboards, etc.)
  const logsDir = path.join(__dirname, '..', 'logs');
  const ts = fim.toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
  const arquivoJson = path.join(logsDir, `relatorio_${ts}.json`);

  const json = {
    modo, inicio: inicio.toISOString(), fim: fim.toISOString(),
    duracaoSegundos: parseFloat(duracao),
    resumo: {
      totalAnalisados:    stats.totalAnalisados,
      semRastreio:        stats.semRastreio,
      naoCorreios:        stats.naoCorreios,
      statusBloqueado:    stats.statusBloqueado,
      correiosErro:       stats.correiosErro,
      emTransito:         stats.emTransito,
      entregues:          stats.entregues,
      atualizadosBling:   isDryRun ? stats.ignoradosDryRun : stats.atualizadosBling,
      atualizadosWake:    isDryRun ? stats.ignoradosDryRun : stats.atualizadosWake,
      errosBling:         stats.errosBling,
      errosWake:          stats.errosWake,
    },
    pedidosAtualizados: stats.pedidosAtualizados,
    pedidosIgnorados:   stats.pedidosIgnorados,
    erros:              stats.erros,
  };

  fs.writeFileSync(arquivoJson, JSON.stringify(json, null, 2), 'utf-8');
  logger.info(`Relatório JSON salvo: ${arquivoJson}`);

  return json;
}

module.exports = { gerarRelatorio };
