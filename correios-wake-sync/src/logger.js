'use strict';

const winston = require('winston');
const path    = require('path');
const fs      = require('fs');

const LOGS_DIR = path.join(__dirname, '..', 'logs');
if (!fs.existsSync(LOGS_DIR)) fs.mkdirSync(LOGS_DIR, { recursive: true });

const timestamp = new Date()
  .toISOString()
  .replace(/[:.]/g, '-')
  .replace('T', '_')
  .slice(0, 19);

const arquivoExecucao = path.join(LOGS_DIR, `execucao_${timestamp}.log`);
const arquivoErros    = path.join(LOGS_DIR, 'erros.log');

function formatarMensagem(info) {
  const ts   = new Date().toISOString();
  const nivel = info.level.toUpperCase().padEnd(7);
  return `[${ts}] ${nivel} ${info.message}`;
}

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.errors({ stack: true }),
    winston.format.printf(formatarMensagem)
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(formatarMensagem)
      ),
    }),
    new winston.transports.File({ filename: arquivoExecucao }),
    new winston.transports.File({ filename: arquivoErros, level: 'error' }),
  ],
});

logger.caminhoLog = arquivoExecucao;

module.exports = logger;
