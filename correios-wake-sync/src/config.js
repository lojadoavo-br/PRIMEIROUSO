'use strict';

require('dotenv').config();

function obrigatorio(nome) {
  const valor = process.env[nome];
  if (!valor || !valor.trim()) {
    throw new Error(`Variável de ambiente obrigatória não definida: ${nome}`);
  }
  return valor.trim();
}

function opcional(nome, padrao) {
  const valor = process.env[nome];
  return (valor && valor.trim()) ? valor.trim() : padrao;
}

function validarConfig(config) {
  if (!config.wake.apiUrl.startsWith('https://')) {
    throw new Error('WAKE_API_URL deve usar HTTPS');
  }
  if (!config.correios.apiUrl.startsWith('https://')) {
    throw new Error('CORREIOS_API_URL deve usar HTTPS');
  }
  if (config.wake.maxPedidos < 1 || config.wake.maxPedidos > 1000) {
    throw new Error('WAKE_MAX_PEDIDOS deve estar entre 1 e 1000');
  }
}

function carregarConfig() {
  const config = {
    isDryRun: opcional('DRY_RUN', 'true').toLowerCase() !== 'false',

    wake: {
      apiUrl:        obrigatorio('WAKE_API_URL'),
      accessToken:   obrigatorio('WAKE_ACCESS_TOKEN'),
      statusVerificar: opcional('WAKE_STATUS_VERIFICAR', 'Enviado,Em transporte,Objeto postado')
        .split(',')
        .map(s => s.trim())
        .filter(Boolean),
      statusEntregue:  opcional('WAKE_STATUS_ENTREGUE', 'Entregue'),
      statusIdVerificar: opcional('WAKE_STATUS_ID_VERIFICAR', '')
        .split(',')
        .map(s => parseInt(s.trim(), 10))
        .filter(n => !isNaN(n)),
      statusIdEntregue: parseInt(opcional('WAKE_STATUS_ID_ENTREGUE', '0'), 10) || null,
      maxPedidos:    parseInt(opcional('WAKE_MAX_PEDIDOS', '200'), 10),
    },

    correios: {
      apiUrl:        opcional('CORREIOS_API_URL', 'https://api.correios.com.br'),
      usuario:       obrigatorio('CORREIOS_USUARIO'),
      senha:         obrigatorio('CORREIOS_SENHA'),
      cartaoPostagem: obrigatorio('CORREIOS_CARTAO_POSTAGEM'),
    },

    limites: {
      intervaloPedidosMs:  parseInt(opcional('INTERVALO_ENTRE_PEDIDOS_MS', '1500'), 10),
      intervaloCorreiosMs: parseInt(opcional('INTERVALO_CORREIOS_MS', '800'), 10),
      maxTentativas:       parseInt(opcional('MAX_TENTATIVAS', '3'), 10),
    },
  };

  validarConfig(config);
  return config;
}

module.exports = { carregarConfig };
