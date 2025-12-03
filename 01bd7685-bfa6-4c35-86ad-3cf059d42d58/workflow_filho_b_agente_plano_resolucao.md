# Workflow Filho B – `AgentePlanoResolucao`

Workflow **orientado a IA (agent)** responsável por:

* Ler o texto da solicitação do cliente.

* Considerar a **decisão de política já tomada** pelo `MotorPoliticasPosVenda`.

* Montar um **plano estruturado de ações** e uma **resposta sugerida** para o cliente.

* Indicar se o caso deve ser **escalado para supervisor**.

> Importante: este workflow **não altera a política** (`ELEGIVEL`, `VALOR_REEMBOLSO`, `RESTRICOES`).\
> Ele apenas **planeja como tratar o caso** e **como comunicar**, com base nessas decisões.

***

## 1. Objetivo

Dado:

* o texto da solicitação do cliente

* o tipo de solicitação, motivo e decisão de política (saída do Filho A)

O workflow:

1. Usa IA para analisar o contexto, o tom e o histórico da decisão.
2. Define um conjunto de **ações estruturadas** a serem tomadas (reembolso, voucher, tag, remarcação, etc.).
3. Gera uma **mensagem de resposta sugerida** para o cliente.
4. Decide se o caso deve ou não ser **escalado para um supervisor**.

Esse workflow será exportado como um **Component** e chamado pelo Workflow Pai `OrquestradorPosVenda`.

***

## 2. Inputs esperados

O workflow `AgentePlanoResolucao` recebe, como entrada, o output do Filho A + o texto original do cliente:

```json
{
  "texto_solicitacao": "string",
  "TIPO_SOLICITACAO": "string",
  "MOTIVO": "string",
  "ELEGIVEL": true,
  "VALOR_REEMBOLSO": 0,
  "CODIGO_REGRA_APLICADA": "string",
  "RESTRICOES": "string or null"
}
```

### 2.1. Descrição dos campos de entrada

* **texto\_solicitacao** (string)\
  Texto livre da mensagem enviada pelo cliente.

* **TIPO\_SOLICITACAO** (string)\
  Tipo da solicitação, conforme classificado pelo Filho A.\
  Exemplos: `REEMBOLSO`, `REMARCACAO`, `RECLAMACAO_SERVICO`, etc.

* **MOTIVO** (string)\
  Motivo formalizado, em formato de código.\
  Exemplos: `CANCELAMENTO_CLIENTE_ANTECIPADO`, `ATRASO_ONIBUS`, `NO_SHOW_CLIENTE`, etc.

* **ELEGIVEL** (boolean)\
  Indica se a solicitação é elegível a reembolso segundo a política.

* **VALOR\_REEMBOLSO** (number)\
  Valor de reembolso aprovado pela política.\
  **Importante**: o agent não pode aumentar esse valor.

* **CODIGO\_REGRA\_APLICADA** (string)\
  Código da regra de negócio aplicada (ex.: `"RULE_FULL_REFUND_24H_BEFORE"`).

* **RESTRICOES** (string | null)\
  Restrições associadas à decisão.\
  Exemplos:

  * `null`

  * `"APENAS_VOUCHER_POR_EXCECAO"`

  * `"REMARCACAO_MESMA_ROTA_E_TARIFA"`

***

## 3. Sucessão de etapas (steps internos)

### 3.1. Step 1 – Preparar contexto para IA

**Nome sugerido**: `montar_contexto_para_agente`

**Responsabilidades**:

* Montar um objeto de contexto que será enviado ao modelo de IA, contendo:

  * Texto da solicitação (`texto_solicitacao`)

  * Tipo e motivo (`TIPO_SOLICITACAO`, `MOTIVO`)

  * Decisão de política (`ELEGIVEL`, `VALOR_REEMBOLSO`, `CODIGO_REGRA_APLICADA`, `RESTRICOES`)

  * Opcional: adicionar campos derivativos (ex.: tags legíveis para humanos).

**Saída interna**:

* `contexto_agente` (estrutura consolidada contendo todos os campos necessários ao prompt)

***

### 3.2. Step 2 – Agent de plano e resposta

**Nome sugerido**: `agente_plano_e_resposta`

**Tipo**: step de IA (LLM / agent)

**Responsabilidades**:

* Gerar, a partir do `contexto_agente`:

  * Um plano estruturado de ações (`ACOES`)

  * Uma mensagem sugerida para o cliente (`RESPOSTA_SUGERIDA`)

  * Um indicador de escalonamento (`ESCALAR_SUPERVISOR`)

**Formato de output esperado**:

```json
{
  "ACOES": [
    {
      "tipo": "string",
      "valor": 0,
      "motivo": "string opcional",
      "tag": "string opcional",
      "nova_data": "string opcional",
      "canal": "string opcional"
    }
  ],
  "RESPOSTA_SUGERIDA": "string",
  "ESCALAR_SUPERVISOR": false
}
```

**Observação**: os campos dentro de cada item de `ACOES` podem variar conforme o tipo de ação (ex.: `REEMBOLSO` usa `valor`, `REMARCAR_VIAGEM` usa `nova_data`, `TAGUEAR_CLIENTE` usa `tag`).

***

### 3.3. Step 3 – Validação determinística das ações (opcional, mas recomendado)

**Nome sugerido**: `validar_acoes_contra_politica`

**Responsabilidades**:

* Garantir que as ações sugeridas não violem a política definida pelo Filho A.

* Regras exemplo:

  * Se `ELEGIVEL = false`, nenhuma ação do tipo "REEMBOLSO" com `valor > 0` deve ser permitida.

  * Se houver `RESTRICOES = "APENAS_VOUCHER_POR_EXCECAO"`, o agent pode sugerir voucher, mas não reembolso em dinheiro.

**Comportamento sugerido em caso de violação**:

* Remover ou ajustar ações inconsistentes.

* Opcionalmente, adicionar uma ação de fallback (ex.: `NAO_REEMBOLSAR` com motivo de política).

**Saída interna**:

* `ACOES_VALIDADAS` (lista de ações após saneamento)

* `RESPOSTA_SUGERIDA` (inalterada, ou ajustada se necessário)

* `ESCALAR_SUPERVISOR` (pode permanecer ou ser forçado para `true` em casos críticos)

***

### 3.4. Step 4 – Montar output final do workflow

**Nome sugerido**: `montar_output_final`

**Responsabilidades**:

* Consolidar os campos finais que serão expostos como output do workflow:

```json
{
  "ACOES": [...],
  "RESPOSTA_SUGERIDA": "string",
  "ESCALAR_SUPERVISOR": false
}
```

***

## 4. Outputs esperados

O output público do workflow `AgentePlanoResolucao` deve seguir o formato:

```json
{
  "ACOES": [
    {
      "tipo": "string",
      "valor": 0,
      "motivo": "string opcional",
      "tag": "string opcional",
      "nova_data": "string opcional",
      "canal": "string opcional"
    }
  ],
  "RESPOSTA_SUGERIDA": "string",
  "ESCALAR_SUPERVISOR": false
}
```

### 4.1. Descrição dos campos de saída

* **ACOES** (array)\
  Lista estruturada de ações que o sistema/times devem executar.\
  Exemplos de tipos de ação:

  * `REEMBOLSO`

    * campos relevantes: `valor`

  * `ENVIAR_VOUCHER`

    * campos relevantes: `valor`

  * `NAO_REEMBOLSAR`

    * campos relevantes: `motivo`

  * `REMARCAR_VIAGEM`

    * campos relevantes: `nova_data`

  * `TAGUEAR_CLIENTE`

    * campos relevantes: `tag`

  * `CONFIRMAR_COM_CLIENTE`

    * campos relevantes: `canal` ("email", "whatsapp", etc.)

* **RESPOSTA\_SUGERIDA** (string)\
  Mensagem em texto livre para ser enviada ao cliente (ou usada como base).\
  Deve refletir:

  * a decisão de política

  * o plano de ação (`ACOES`)

  * um tom empático e claro

* **ESCALAR\_SUPERVISOR** (boolean)\
  Indica se o caso deve ser escalado para supervisão humana.\
  Exemplos de gatilhos típicos:

  * cliente muito insatisfeito (tom forte)

  * reincidência / histórico de problemas

  * valor muito alto

  * tipo de incidente crítico

***

## 5. Relação com os casos de teste (mock)

O workflow deve ser capaz de gerar algo similar aos seguintes resultados:

### 5.1. Caso 1 – Reembolso simples, cliente ok

**Input** (resumo do Filho A + texto):

* `TIPO_SOLICITACAO = "REEMBOLSO"`

* `MOTIVO = "CANCELAMENTO_CLIENTE_ANTECIPADO"`

* `ELEGIVEL = true`

* `VALOR_REEMBOLSO = 199.90`

**Output esperado**:

```json
{
  "ACOES": [
    { "tipo": "REEMBOLSO", "valor": 199.90 }
  ],
  "RESPOSTA_SUGERIDA": "Olá! Tudo bem? Já processamos o cancelamento da sua passagem e o reembolso integral de R$ 199,90 será realizado conforme o meio de pagamento utilizado. Qualquer dúvida é só responder por aqui :)",
  "ESCALAR_SUPERVISOR": false
}
```

### 5.2. Caso 2 – Atraso operacional, cliente furioso

**Input** (resumo do Filho A + texto):

* `TIPO_SOLICITACAO = "REEMBOLSO"`

* `MOTIVO = "ATRASO_ONIBUS"`

* `ELEGIVEL = true`

* `VALOR_REEMBOLSO = 259.50`

**Output esperado**:

```json
{
  "ACOES": [
    { "tipo": "REEMBOLSO", "valor": 259.50 },
    { "tipo": "ENVIAR_VOUCHER", "valor": 50.00 },
    { "tipo": "TAGUEAR_CLIENTE", "tag": "ALTO_RISCO" }
  ],
  "RESPOSTA_SUGERIDA": "Olá! Antes de tudo, sentimos muito pelo transtorno e pelo impacto no seu compromisso. Já aprovamos o reembolso integral de R$ 259,50 e, além disso, vamos disponibilizar um voucher de R$ 50,00 para uma próxima viagem, como forma de compensação. Estamos registrando o ocorrido com a rota e o parceiro responsáveis para evitar que isso se repita.",
  "ESCALAR_SUPERVISOR": true
}
```

### 5.3. Caso 3 – No-show, tarifa restrita (sem reembolso, voucher como exceção)

**Input**:

* `TIPO_SOLICITACAO = "REEMBOLSO"`

* `MOTIVO = "NO_SHOW_CLIENTE"`

* `ELEGIVEL = false`

* `VALOR_REEMBOLSO = 0.0`

* `RESTRICOES = "APENAS_VOUCHER_POR_EXCECAO"`

**Output esperado**:

```json
{
  "ACOES": [
    { "tipo": "NAO_REEMBOLSAR", "motivo": "NO_SHOW_TARIFA_RESTRITA" },
    { "tipo": "ENVIAR_VOUCHER", "valor": 50.00 }
  ],
  "RESPOSTA_SUGERIDA": "Olá! Entendemos a situação e agradecemos por ter explicado. Pela política da tarifa que você escolheu, não podemos realizar reembolso em caso de não comparecimento. Mesmo assim, gostaríamos de ajudar: podemos oferecer um voucher de R$ 50,00 para ser usado em uma próxima compra.",
  "ESCALAR_SUPERVISOR": false
}
```

### 5.4. Caso 4 – Remarcação

**Input**:

* `TIPO_SOLICITACAO = "REMARCACAO"`

* `MOTIVO = "ALTERACAO_PLANO_CLIENTE"`

* `ELEGIVEL = true`

* `VALOR_REEMBOLSO = 0.0`

* `RESTRICOES = "REMARCACAO_MESMA_ROTA_E_TARIFA"`

**Output esperado**:

```json
{
  "ACOES": [
    { "tipo": "REMARCAR_VIAGEM", "nova_data": "2025-12-23" },
    { "tipo": "CONFIRMAR_COM_CLIENTE", "canal": "email" }
  ],
  "RESPOSTA_SUGERIDA": "Olá! Sem problemas, conseguimos remarcar a sua viagem para o dia seguinte mantendo o mesmo valor e rota. Confirma pra gente se o horário das XXh está ok? Assim já finalizamos a alteração.",
  "ESCALAR_SUPERVISOR": false
}
```

