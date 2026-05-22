#!/usr/bin/env node
'use strict';

/**
 * correios-wake-sync
 * Sincroniza status de entrega dos Correios com pedidos na Wake Commerce.
 *
 * Uso:
 *   node index.js              → usa DRY_RUN do .env (padrão: simulação)
 *   node index.js --dry-run    → força modo simulação
 *   node index.js --producao   → força modo produção
 *   node index.js --help       → exibe ajuda
 *
 * Variáveis de ambiente:
 *   Copie .env.example → .env e preencha com suas credenciais.
 */

const { carregarConfig }    = require('./src/config');
const logger                = require('./src/logger');
const { WakeApi }           = require('./src/wakeApi');
const { CorreiosApi }       = require('./src/correiosApi');
const { OrdemProcessador }  = require('./src/orderProcessor');
const { gerarRelatorio }    = require('./src/report');

// ─── CLI args ────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`
correios-wake-sync — sincronizador de entrega Correios → Wake Commerce

USO:
  node index.js [opções]

OPÇÕES:
  --dry-run    Modo simulação: lista pedidos que seriam atualizados sem alterar nada
  --producao   Modo produção: atualiza pedidos entregues na Wake
  --help       Exibe esta ajuda

VARIÁVEIS DE AMBIENTE (arquivo .env):
  WAKE_API_URL            URL da API GraphQL da Wake
  WAKE_ACCESS_TOKEN       Token de acesso à Wake
  WAKE_STATUS_VERIFICAR   Status a verificar (ex.: Enviado,Em transporte)
  WAKE_STATUS_ENTREGUE    Status de entregue na Wake
  CORREIOS_USUARIO        Usuário/CNPJ do contrato Correios
  CORREIOS_SENHA          Senha do contrato Correios
  CORREIOS_CARTAO_POSTAGEM Número do cartão de postagem
  DRY_RUN                 true = simulação | false = produção

EXEMPLOS:
  npm run simular          # simulação
  npm run producao         # produção
  node index.js --dry-run  # simulação via CLI
`);
  process.exit(0);
}

// Flags de CLI sobrepõem a variável de ambiente
if (args.includes('--dry-run'))   process.env.DRY_RUN = 'true';
if (args.includes('--producao'))  process.env.DRY_RUN = 'false';

// ─── Execução principal ──────────────────────────────────────────────────────

async function main() {
  const inicio = new Date();
  logger.info('correios-wake-sync iniciado');

  // 1. Carregar e validar configuração
  let config;
  try {
    config = carregarConfig();
  } catch (erroConfig) {
    logger.error(`Erro de configuração: ${erroConfig.message}`);
    logger.error('Verifique o arquivo .env. Copie .env.example como ponto de partida.');
    process.exit(1);
  }

  logger.info(`Log desta execução: ${logger.caminhoLog}`);

  // 2. Instanciar clientes
  const wakeApi     = new WakeApi(config);
  const correiosApi = new CorreiosApi(config);

  // 3. Testar autenticação nos Correios antes de processar pedidos
  try {
    await correiosApi.autenticar();
  } catch (erroAuth) {
    logger.error(`Falha na autenticação com os Correios: ${erroAuth.message}`);
    logger.error('Verifique CORREIOS_USUARIO, CORREIOS_SENHA e CORREIOS_CARTAO_POSTAGEM no .env');
    process.exit(1);
  }

  // 4. Processar pedidos
  const processador = new OrdemProcessador({ wakeApi, correiosApi, config });
  let stats;

  try {
    stats = await processador.processar();
  } catch (erroProcessamento) {
    logger.error(`Erro inesperado durante processamento: ${erroProcessamento.message}`);
    logger.error(erroProcessamento.stack);
    process.exit(1);
  }

  // 5. Gerar e exibir relatório
  gerarRelatorio(stats, config.isDryRun, inicio);

  const exitCode = stats.erros.length > 0 ? 1 : 0;
  process.exit(exitCode);
}

// Captura erros não tratados para garantir que sempre há saída no log
process.on('unhandledRejection', (motivo) => {
  logger.error(`Rejeição não tratada: ${motivo}`);
  process.exit(1);
});

process.on('uncaughtException', (erro) => {
  logger.error(`Exceção não capturada: ${erro.message}`);
  logger.error(erro.stack);
  process.exit(1);
});

main();
