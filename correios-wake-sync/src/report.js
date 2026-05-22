'use strict';

const fs     = require('fs');
const path   = require('path');
const logger = require('./logger');

function gerarRelatorio(stats, isDryRun, inicio) {
  const fim      = new Date();
  const duracao  = ((fim - inicio) / 1000).toFixed(1);
  const modo     = isDryRun ? 'SIMULAÇÃO' : 'PRODUÇÃO';

  const linhas = [
    '═'.repeat(60),
    `RELATÓRIO FINAL — MODO ${modo}`,
    `Data/hora: ${fim.toISOString()}`,
    `Duração:   ${duracao}s`,
    '─'.repeat(60),
    'RESUMO GERAL:',
    `  Total de pedidos analisados:  ${stats.totalAnalisados}`,
    `  Sem código de rastreio:       ${stats.semRastreio}`,
    `  Rastreio não é Correios:      ${stats.semCorreios}`,
    `  Status bloqueado:             ${stats.statusBloqueado}`,
    `  Erro na API dos Correios:     ${stats.correiosErro}`,
    `  Em trânsito (não entregues):  ${stats.emTransito}`,
    `  Confirmados como entregues:   ${stats.entregues}`,
    isDryRun
      ? `  [SIMULAÇÃO] Seriam atualizados: ${stats.ignoradosDryRun}`
      : `  Atualizados na Wake:           ${stats.atualizados}`,
    isDryRun
      ? ''
      : `  Erros ao atualizar na Wake:    ${stats.errosWake}`,
  ].filter(l => l !== null);

  if (stats.pedidosAtualizados.length > 0) {
    linhas.push('─'.repeat(60));
    linhas.push(isDryRun ? 'PEDIDOS QUE SERIAM ATUALIZADOS:' : 'PEDIDOS ATUALIZADOS:');
    for (const p of stats.pedidosAtualizados) {
      linhas.push(`  Pedido #${p.pedido} | Rastreio: ${p.rastreio}`);
      linhas.push(`    Status Wake anterior: ${p.statusWake}`);
      linhas.push(`    Evento Correios:      ${p.statusCorreios}`);
      linhas.push(`    Data de entrega:      ${p.dataEntrega ?? 'não informada'}`);
    }
  }

  if (stats.pedidosIgnorados.length > 0) {
    linhas.push('─'.repeat(60));
    linhas.push('PEDIDOS IGNORADOS:');
    for (const p of stats.pedidosIgnorados) {
      const motivo = p.ultimoEvento
        ? `${p.motivo} — ${p.ultimoEvento}`
        : p.motivo;
      linhas.push(`  Pedido #${p.numero} | Rastreio: ${p.rastreio ?? 'ausente'} | Motivo: ${motivo}`);
    }
  }

  if (stats.erros.length > 0) {
    linhas.push('─'.repeat(60));
    linhas.push('ERROS ENCONTRADOS:');
    for (const e of stats.erros) {
      linhas.push(`  Pedido #${e.pedido} | Rastreio: ${e.rastreio} | ${e.erro}`);
    }
  }

  linhas.push('═'.repeat(60));

  const texto = linhas.join('\n');
  logger.info('\n' + texto);

  // Salvar relatório JSON para integração com outros sistemas
  const logsDir = path.join(__dirname, '..', 'logs');
  const ts = fim.toISOString().replace(/[:.]/g, '-').replace('T', '_').slice(0, 19);
  const arquivoJson = path.join(logsDir, `relatorio_${ts}.json`);

  const relatorioJson = {
    modo,
    inicio:  inicio.toISOString(),
    fim:     fim.toISOString(),
    duracaoSegundos: parseFloat(duracao),
    resumo: {
      totalAnalisados:   stats.totalAnalisados,
      semRastreio:       stats.semRastreio,
      semCorreios:       stats.semCorreios,
      statusBloqueado:   stats.statusBloqueado,
      correiosErro:      stats.correiosErro,
      emTransito:        stats.emTransito,
      entregues:         stats.entregues,
      atualizados:       isDryRun ? stats.ignoradosDryRun : stats.atualizados,
      errosWake:         stats.errosWake,
    },
    pedidosAtualizados: stats.pedidosAtualizados,
    pedidosIgnorados:   stats.pedidosIgnorados,
    erros:              stats.erros,
  };

  fs.writeFileSync(arquivoJson, JSON.stringify(relatorioJson, null, 2), 'utf-8');
  logger.info(`Relatório JSON salvo em: ${arquivoJson}`);

  return relatorioJson;
}

module.exports = { gerarRelatorio };
