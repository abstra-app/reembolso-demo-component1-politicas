# Workflow Filho A – `MotorPoliticasPosVenda`

Workflow **determinístico** responsável por aplicar as **políticas de pós-venda** (reembolso / remarcação / exceções) a partir de dados da reserva e da solicitação do cliente.

> Este workflow **não usa IA/agent**.  
> É composto apenas por **etapas em código** (e integrações determinísticas) e será exportado como um **Component**.

---

## 1. Objetivo

Dado um pedido de pós-venda, o workflow:

1. Recebe dados básicos da reserva + contexto da solicitação.  
2. Calcula informações derivadas (por exemplo, quantos dias antes da viagem a solicitação foi feita).  
3. Classifica o **tipo de solicitação** e o **motivo** de forma determinística/simplificada.  
4. Aplica as **políticas de elegibilidade** e de **cálculo de reembolso**.  
5. Expõe um conjunto de **campos estruturados de decisão**, que serão utilizados pelo workflow pai e pelo workflow Filho B (`AgentePlanoResolucao`).

---

## 2. Inputs esperados

O workflow `MotorPoliticasPosVenda` recebe o seguinte payload:

```json
{
  "booking_id": "string",
  "canal_venda": "string",
  "data_viagem": "string",
  "data_solicitacao": "string",
  "valor_pago": 0,
  "texto_solicitacao": "string"
}
```

### 2.1. Descrição dos campos de entrada

- **booking_id** (string)  
  Identificador da reserva/compra.

- **canal_venda** (string)  
  Canal em que a viagem foi comprada.  
  Exemplos: "app", "web", "parceiro", "balcao".

- **data_viagem** (string, formato ISO)  
  Data da viagem contratada.  
  Exemplo: "2025-12-20".

- **data_solicitacao** (string, formato ISO)  
  Data em que o cliente fez o pedido de pós-venda.  
  Exemplo: "2025-12-18".

- **valor_pago** (number)  
  Valor total pago pelo cliente na passagem (decimal).  
  Exemplo: 199.90.

- **texto_solicitacao** (string)  
  Texto livre da mensagem do cliente.  
  Para a primeira versão, pode ser:
  - usado apenas para logging / auditoria, ou
  - usado em regras determinísticas simples (ex.: identificação de palavra-chave).

---

## 3. Sucessão de etapas (steps internos)

Todos os steps deste workflow são determinísticos (code e integrações).

### 3.1. Step 1 – Normalizar e validar entrada

**Nome sugerido:** `normalizar_entrada`

**Responsabilidades:**
- Validar a presença de campos obrigatórios:
  - booking_id, canal_venda, data_viagem, data_solicitacao, valor_pago.
- Converter tipos:
  - valor_pago → número
  - data_viagem, data_solicitacao → objetos de data.
- Normalizar canal_venda (ex.: tudo minúsculo).

**Saídas internas:**
- booking_id
- canal_venda_normalizado
- data_viagem_dt
- data_solicitacao_dt
- valor_pago_num
- texto_solicitacao (repassado como veio)

---

### 3.2. Step 2 – Calcular contexto de tempo

**Nome sugerido:** `calcular_contexto_tempo`

**Responsabilidades:**
- Calcular dias_antes = diferença em dias entre data_viagem e data_solicitacao:
  - dias_antes > 0 → solicitação antes da viagem
  - dias_antes = 0 → no dia da viagem
  - dias_antes < 0 → solicitação após a viagem
- Derivar flags auxiliares:
  - solicitacao_antes_da_viagem (bool)
  - solicitacao_apos_viagem (bool)

**Saídas internas:**
- dias_antes (int)
- solicitacao_antes_da_viagem (bool)
- solicitacao_apos_viagem (bool)

---

### 3.3. Step 3 – Classificar tipo de solicitação e motivo

**Nome sugerido:** `classificar_tipo_e_motivo`

**Responsabilidades:**
- Determinar:
  - TIPO_SOLICITACAO
  - MOTIVO

Esta classificação pode ser:
- Hard-coded para cenários de demo (ex.: baseado em booking_id), ou
- Implementada com regras simples (por exemplo, detecção de substring em texto_solicitacao).

**Sugestão de valores:**
- **TIPO_SOLICITACAO** (enum):
  - REEMBOLSO
  - REMARCACAO
  - RECLAMACAO_SERVICO
  - INFORMACAO
  - OUTROS
- **MOTIVO** (enum em UPPER_SNAKE_CASE):
  - CANCELAMENTO_CLIENTE_ANTECIPADO
  - ATRASO_ONIBUS
  - NO_SHOW_CLIENTE
  - ALTERACAO_PLANO_CLIENTE
  - ERRO_PLATAFORMA
  - OUTROS

**Saídas deste step:**
- TIPO_SOLICITACAO
- MOTIVO

**Observação:** para a demo, você pode garantir que os quatro casos mock caiam exatamente nos valores desejados (1: cancelamento antecipado, 2: atraso, 3: no-show, 4: alteração de plano).

---

### 3.4. Step 4 – Aplicar políticas de elegibilidade e cálculo

**Nome sugerido:** `aplicar_politicas`

**Responsabilidades:**
- Implementar regras de negócio determinísticas para:
  - ELEGIVEL (true/false)
  - VALOR_REEMBOLSO
  - CODIGO_REGRA_APLICADA
  - RESTRICOES
- As regras usam:
  - TIPO_SOLICITACAO
  - MOTIVO
  - dias_antes / flags de tempo
  - valor_pago_num
  - eventualmente canal_venda_normalizado

**Exemplo de lógica (conceitual):**

- **Caso 1** – Cancelamento antecipado (REEMBOLSO + CANCELAMENTO_CLIENTE_ANTECIPADO + dias_antes >= 1):
  - ELEGIVEL = true
  - VALOR_REEMBOLSO = valor_pago
  - CODIGO_REGRA_APLICADA = "RULE_FULL_REFUND_24H_BEFORE"
  - RESTRICOES = null

- **Caso 2** – Atraso de ônibus (REEMBOLSO + ATRASO_ONIBUS + solicitação após viagem):
  - ELEGIVEL = true
  - VALOR_REEMBOLSO = valor_pago
  - CODIGO_REGRA_APLICADA = "RULE_OPERATIONAL_DELAY_FULL_REFUND"
  - RESTRICOES = null

- **Caso 3** – No-show (REEMBOLSO + NO_SHOW_CLIENTE):
  - ELEGIVEL = false
  - VALOR_REEMBOLSO = 0.0
  - CODIGO_REGRA_APLICADA = "RULE_NO_SHOW_NO_REFUND"
  - RESTRICOES = "APENAS_VOUCHER_POR_EXCECAO"

- **Caso 4** – Remarcação (REMARCACAO + ALTERACAO_PLANO_CLIENTE):
  - ELEGIVEL = true
  - VALOR_REEMBOLSO = 0.0
  - CODIGO_REGRA_APLICADA = "RULE_FREE_REBOOKING_SAME_ROUTE"
  - RESTRICOES = "REMARCACAO_MESMA_ROTA_E_TARIFA"

**Saídas deste step:**
- ELEGIVEL (bool)
- VALOR_REEMBOLSO (number)
- CODIGO_REGRA_APLICADA (string)
- RESTRICOES (string ou null)

---

### 3.5. Step 5 – Montar output final do workflow

**Nome sugerido:** `montar_output_decisao`

**Responsabilidades:**
- Reunir as principais variáveis em um objeto único de saída, seguindo o contrato de output.

---

## 4. Outputs esperados

O output do workflow MotorPoliticasPosVenda deve seguir o formato abaixo:

```json
{
  "TIPO_SOLICITACAO": "REEMBOLSO",
  "MOTIVO": "ATRASO_ONIBUS",
  "ELEGIVEL": true,
  "VALOR_REEMBOLSO": 0,
  "CODIGO_REGRA_APLICADA": "string",
  "RESTRICOES": null
}
```

### 4.1. Descrição dos campos de saída
	•	TIPO_SOLICITACAO (string)
Tipo de solicitação classificado pelo workflow.
Exemplos: REEMBOLSO, REMARCACAO, etc.
	•	MOTIVO (string)
Motivo estruturado em formato de código (UPPER_SNAKE_CASE).
Exemplos: CANCELAMENTO_CLIENTE_ANTECIPADO, ATRASO_ONIBUS.
	•	ELEGIVEL (boolean)
Indica se a solicitação é elegível a algum tipo de reembolso segundo a política.
	•	VALOR_REEMBOLSO (number)
Valor a ser reembolsado segundo a política aplicada.
	•	CODIGO_REGRA_APLICADA (string)
Código identificador da política/regra que foi aplicada.
Exemplos:
	•	"RULE_FULL_REFUND_24H_BEFORE"
	•	"RULE_OPERATIONAL_DELAY_FULL_REFUND"
	•	"RULE_NO_SHOW_NO_REFUND"
	•	"RULE_FREE_REBOOKING_SAME_ROUTE"
	•	RESTRICOES (string | null)
Eventuais restrições associadas à decisão.
Exemplos:
	•	null
	•	"APENAS_VOUCHER_POR_EXCECAO"
	•	"REMARCACAO_MESMA_ROTA_E_TARIFA"

---

## 5. Relação com os casos de teste (mock)

O workflow deve ser capaz de produzir os outputs abaixo, dado o input correspondente:

### 5.1. Caso 1 – Cancelamento antecipado
- TIPO_SOLICITACAO = "REEMBOLSO"
- MOTIVO = "CANCELAMENTO_CLIENTE_ANTECIPADO"
- ELEGIVEL = true
- VALOR_REEMBOLSO = valor_pago
- CODIGO_REGRA_APLICADA = "RULE_FULL_REFUND_24H_BEFORE"
- RESTRICOES = null

### 5.2. Caso 2 – Atraso operacional
- TIPO_SOLICITACAO = "REEMBOLSO"
- MOTIVO = "ATRASO_ONIBUS"
- ELEGIVEL = true
- VALOR_REEMBOLSO = valor_pago
- CODIGO_REGRA_APLICADA = "RULE_OPERATIONAL_DELAY_FULL_REFUND"
- RESTRICOES = null

### 5.3. Caso 3 – No-show, tarifa restrita
- TIPO_SOLICITACAO = "REEMBOLSO"
- MOTIVO = "NO_SHOW_CLIENTE"
- ELEGIVEL = false
- VALOR_REEMBOLSO = 0.0
- CODIGO_REGRA_APLICADA = "RULE_NO_SHOW_NO_REFUND"
- RESTRICOES = "APENAS_VOUCHER_POR_EXCECAO"

### 5.4. Caso 4 – Remarcação
- TIPO_SOLICITACAO = "REMARCACAO"
- MOTIVO = "ALTERACAO_PLANO_CLIENTE"
- ELEGIVEL = true
- VALOR_REEMBOLSO = 0.0
- CODIGO_REGRA_APLICADA = "RULE_FREE_REBOOKING_SAME_ROUTE"
- RESTRICOES = "REMARCACAO_MESMA_ROTA_E_TARIFA"