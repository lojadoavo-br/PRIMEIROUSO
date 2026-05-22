#!/usr/bin/env node
'use strict';

/**
 * correios-wake-sync
 * Lê pedidos do Bling, verifica entrega nos Correios e atualiza Bling + Wake.
 *
 * Uso:
 *   node index.js              → usa DRY_RUN do .env (padrão: simulação)
 *   node index.js --dry-run    → força simulação
 *   node index.js --producao   → força produção
 *   node index.js --help       → ajuda
 */

const { carregarConfig }    = require('./src/config');
const logger                = require('./src/logger');
const { BlingApi }          = require('./src/blingApi');
const { WakeApi }           = require('./src/wakeApi');
const { CorreiosApi }       = require('./src/correiosApi');
const { OrdemProcessador }  = require('./src/orderProcessor');
const { gerarRelatorio }    = require('./src/report');

// ─── CLI ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`
correios-wake-sync — Bling + Correios + Wake Commerce

Lê pedidos do Bling que têm código de rastreio dos Correios,
verifica se foram entregues e atualiza o status no Bling e na Wake.

USO:
  node index.js [opções]

OPÇÕES:
  --dry-run    Simulação: mostra o que seria feito, não altera nada
  --producao   Produção: atualiza Bling e Wake
  --help       Esta ajuda

VARIÁVEIS DE AMBIENTE (.env):
  BLING_CLIENT_ID              ID do app Bling (developer.bling.com.br)
  BLING_CLIENT_SECRET          Secret do app Bling
  BLING_REFRESH_TOKEN          Refresh token OAuth2 (obtido na autorização inicial)
  BLING_SITUACOES_VERIFICAR    IDs de situação a verificar (ex: 9,12,15)
  BLING_SITUACAO_ENTREGUE_ID   ID da situação "Entregue" no Bling

  WAKE_API_URL                 URL GraphQL da Wake
  WAKE_ACCESS_TOKEN            Token da Wake
  WAKE_STATUS_ENTREGUE         Nome do status "Entregue" na Wake

  CORREIOS_USUARIO             Usuário/CNPJ do contrato Correios
  CORREIOS_SENHA               Senha do contrato
  CORREIOS_CARTAO_POSTAGEM     Número do cartão de postagem

  DRY_RUN                      true=simulação | false=produção

EXEMPLOS:
  npm run simular
  npm run producao
  node index.js --dry-run
`);
  process.exit(0);
}

if (args.includes('--dry-run'))   process.env.DRY_RUN = 'true';
if (args.includes('--producao'))  process.env.DRY_RUN = 'false';

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const inicio = new Date();
  logger.info('correios-wake-sync iniciado');

  let config;
  try {
    config = carregarConfig();
  } catch (erroConfig) {
    logger.error(`Configuração inválida: ${erroConfig.message}`);
    logger.error('Verifique o .env (copie .env.example como ponto de partida).');
    process.exit(1);
  }

  logger.info(`Log desta execução: ${logger.caminhoLog}`);

  const blingApi    = new BlingApi(config);
  const wakeApi     = new WakeApi(config);
  const correiosApi = new CorreiosApi(config);

  // Testar autenticação nos Correios antes de começar
  try {
    await correiosApi.autenticar();
  } catch (erroAuth) {
    logger.error(`Falha na autenticação Correios: ${erroAuth.message}`);
    logger.error('Verifique CORREIOS_USUARIO, CORREIOS_SENHA e CORREIOS_CARTAO_POSTAGEM.');
    process.exit(1);
  }

  // Testar autenticação no Bling
  try {
    await blingApi.autenticar();
  } catch (erroAuth) {
    logger.error(`Falha na autenticação Bling: ${erroAuth.message}`);
    logger.error('Verifique BLING_CLIENT_ID, BLING_CLIENT_SECRET e BLING_REFRESH_TOKEN.');
    process.exit(1);
  }

  const processador = new OrdemProcessador({ blingApi, wakeApi, correiosApi, config });
  let stats;

  try {
    stats = await processador.processar();
  } catch (erro) {
    logger.error(`Erro inesperado: ${erro.message}`);
    logger.error(erro.stack);
    process.exit(1);
  }

  gerarRelatorio(stats, config.isDryRun, inicio);

  process.exit(stats.erros.length > 0 ? 1 : 0);
}

process.on('unhandledRejection', motivo => {
  logger.error(`Rejeição não tratada: ${motivo}`);
  process.exit(1);
});

process.on('uncaughtException', erro => {
  logger.error(`Exceção não capturada: ${erro.message}`);
  process.exit(1);
});

main();
