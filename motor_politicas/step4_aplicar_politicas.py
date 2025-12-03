"""
Step 4: Aplicar Politicas de Elegibilidade e Calculo
Aplica as regras de negocio para determinar elegibilidade e valor de reembolso.
"""
from abstra.tasks import get_trigger_task, send_task

print("=== Step 4: Aplicar Politicas ===")

# Recebe a task do step anterior
task = get_trigger_task()
payload = task.payload

print(f"Payload recebido: {payload}")

# Extrai dados necessarios
TIPO_SOLICITACAO = payload["TIPO_SOLICITACAO"]
MOTIVO = payload["MOTIVO"]
dias_antes = payload["dias_antes"]
valor_pago_num = payload["valor_pago_num"]
solicitacao_antes_da_viagem = payload["solicitacao_antes_da_viagem"]
solicitacao_apos_viagem = payload["solicitacao_apos_viagem"]

print(f"Tipo: {TIPO_SOLICITACAO}")
print(f"Motivo: {MOTIVO}")
print(f"Dias antes: {dias_antes}")
print(f"Valor pago: R$ {valor_pago_num:.2f}")

# Inicializa variaveis de decisao
ELEGIVEL = False
VALOR_REEMBOLSO = 0.0
CODIGO_REGRA_APLICADA = "RULE_DEFAULT_NO_REFUND"
RESTRICOES = None

# Aplica politicas baseadas em tipo e motivo

# Caso 1: Cancelamento antecipado (24h antes)
if TIPO_SOLICITACAO == "REEMBOLSO" and MOTIVO == "CANCELAMENTO_CLIENTE_ANTECIPADO" and dias_antes >= 1:
    ELEGIVEL = True
    VALOR_REEMBOLSO = valor_pago_num
    CODIGO_REGRA_APLICADA = "RULE_FULL_REFUND_24H_BEFORE"
    RESTRICOES = None
    print("Politica aplicada: Reembolso total (cancelamento com 24h de antecedencia)")

# Caso 2: Atraso operacional
elif TIPO_SOLICITACAO == "REEMBOLSO" and MOTIVO == "ATRASO_ONIBUS" and solicitacao_apos_viagem:
    ELEGIVEL = True
    VALOR_REEMBOLSO = valor_pago_num
    CODIGO_REGRA_APLICADA = "RULE_OPERATIONAL_DELAY_FULL_REFUND"
    RESTRICOES = None
    print("Politica aplicada: Reembolso total (atraso operacional)")

# Caso 3: No-show do cliente
elif TIPO_SOLICITACAO == "REEMBOLSO" and MOTIVO == "NO_SHOW_CLIENTE":
    ELEGIVEL = False
    VALOR_REEMBOLSO = 0.0
    CODIGO_REGRA_APLICADA = "RULE_NO_SHOW_NO_REFUND"
    RESTRICOES = "APENAS_VOUCHER_POR_EXCECAO"
    print("Politica aplicada: Sem reembolso (no-show do cliente)")

# Caso 4: Remarcacao
elif TIPO_SOLICITACAO == "REMARCACAO" and MOTIVO == "ALTERACAO_PLANO_CLIENTE":
    ELEGIVEL = True
    VALOR_REEMBOLSO = 0.0
    CODIGO_REGRA_APLICADA = "RULE_FREE_REBOOKING_SAME_ROUTE"
    RESTRICOES = "REMARCACAO_MESMA_ROTA_E_TARIFA"
    print("Politica aplicada: Remarcacao gratuita (mesma rota e tarifa)")

# Caso 5: Cancelamento tardio (menos de 24h)
elif TIPO_SOLICITACAO == "REEMBOLSO" and dias_antes < 1 and dias_antes >= 0:
    ELEGIVEL = True
    VALOR_REEMBOLSO = valor_pago_num * 0.5  # 50% de reembolso
    CODIGO_REGRA_APLICADA = "RULE_PARTIAL_REFUND_LATE_CANCELLATION"
    RESTRICOES = "REEMBOLSO_PARCIAL_50_PORCENTO"
    print("Politica aplicada: Reembolso parcial 50% (cancelamento tardio)")

# Caso default: Nao elegivel
else:
    ELEGIVEL = False
    VALOR_REEMBOLSO = 0.0
    CODIGO_REGRA_APLICADA = "RULE_DEFAULT_NO_REFUND"
    RESTRICOES = "FORA_DAS_POLITICAS_PADRAO"
    print("Politica aplicada: Sem reembolso (fora das politicas padrao)")

print(f"\nResultado da aplicacao de politicas:")
print(f"  ELEGIVEL: {ELEGIVEL}")
print(f"  VALOR_REEMBOLSO: R$ {VALOR_REEMBOLSO:.2f}")
print(f"  CODIGO_REGRA_APLICADA: {CODIGO_REGRA_APLICADA}")
print(f"  RESTRICOES: {RESTRICOES}")

# Monta payload com decisao de politica
payload_com_decisao = {
    **payload,
    "ELEGIVEL": ELEGIVEL,
    "VALOR_REEMBOLSO": VALOR_REEMBOLSO,
    "CODIGO_REGRA_APLICADA": CODIGO_REGRA_APLICADA,
    "RESTRICOES": RESTRICOES
}

print("\nPoliticas aplicadas com sucesso!")

# Envia para o proximo step
send_task("montar_output", payload_com_decisao)
print("Task enviada para Step 5: Montar Output Decisao")

# Completa a task atual
task.complete()
print("=== Step 4 Concluido ===")
