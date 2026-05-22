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
  if (!config.bling.apiUrl.startsWith('https://')) {
    throw new Error('BLING_API_URL deve usar HTTPS');
  }
  if (!config.wake.apiUrl.startsWith('https://')) {
    throw new Error('WAKE_API_URL deve usar HTTPS');
  }
  if (!config.correios.apiUrl.startsWith('https://')) {
    throw new Error('CORREIOS_API_URL deve usar HTTPS');
  }
  if (config.bling.maxPedidos < 1 || config.bling.maxPedidos > 1000) {
    throw new Error('BLING_MAX_PEDIDOS deve estar entre 1 e 1000');
  }
}

function carregarConfig() {
  const config = {
    isDryRun: opcional('DRY_RUN', 'true').toLowerCase() !== 'false',

    // Bling é a fonte dos pedidos e rastreios
    bling: {
      apiUrl:       opcional('BLING_API_URL', 'https://api.bling.com.br/Api/v3'),
      clientId:     obrigatorio('BLING_CLIENT_ID'),
      clientSecret: obrigatorio('BLING_CLIENT_SECRET'),
      _refreshToken: obrigatorio('BLING_REFRESH_TOKEN'),
      // IDs de situação do Bling a verificar (ex.: "9,12,15")
      situacoesVerificar: opcional('BLING_SITUACOES_VERIFICAR', '9,12,15')
        .split(',')
        .map(s => parseInt(s.trim(), 10))
        .filter(n => !isNaN(n)),
      // ID da situação "Entregue" no Bling
      situacaoEntregueId: parseInt(obrigatorio('BLING_SITUACAO_ENTREGUE_ID'), 10),
      maxPedidos: parseInt(opcional('BLING_MAX_PEDIDOS', '200'), 10),
    },

    // Wake recebe apenas a atualização de status, por número de pedido
    wake: {
      apiUrl:        obrigatorio('WAKE_API_URL'),
      accessToken:   obrigatorio('WAKE_ACCESS_TOKEN'),
      statusEntregue: opcional('WAKE_STATUS_ENTREGUE', 'Entregue'),
    },

    correios: {
      apiUrl:         opcional('CORREIOS_API_URL', 'https://api.correios.com.br'),
      usuario:        obrigatorio('CORREIOS_USUARIO'),
      senha:          obrigatorio('CORREIOS_SENHA'),
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
