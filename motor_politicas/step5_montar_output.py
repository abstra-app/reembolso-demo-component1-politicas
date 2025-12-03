"""
Step 5: Montar Output Final da Decisao
Reune os campos de decisao em um output estruturado.
"""
from abstra.tasks import get_trigger_task, send_task
import json

print("=== Step 5: Montar Output Decisao ===")

# Recebe a task do step anterior
task = get_trigger_task()
payload = task.payload

print(f"Payload recebido com {len(payload)} campos")

# Extrai os campos de decisao
TIPO_SOLICITACAO = payload["TIPO_SOLICITACAO"]
MOTIVO = payload["MOTIVO"]
ELEGIVEL = payload["ELEGIVEL"]
VALOR_REEMBOLSO = payload["VALOR_REEMBOLSO"]
CODIGO_REGRA_APLICADA = payload["CODIGO_REGRA_APLICADA"]
RESTRICOES = payload["RESTRICOES"]

# Monta o output estruturado final
output_decisao = {
    "TIPO_SOLICITACAO": TIPO_SOLICITACAO,
    "MOTIVO": MOTIVO,
    "ELEGIVEL": ELEGIVEL,
    "VALOR_REEMBOLSO": VALOR_REEMBOLSO,
    "CODIGO_REGRA_APLICADA": CODIGO_REGRA_APLICADA,
    "RESTRICOES": RESTRICOES
}

print("\n" + "="*60)
print("OUTPUT FINAL DO MOTOR DE POLITICAS DE POS-VENDA")
print("="*60)
print(json.dumps(output_decisao, indent=2, ensure_ascii=False))
print("="*60)

# Informacoes adicionais para auditoria
print(f"\nInformacoes de entrada (auditoria):")
print(f"  Booking ID: {payload['booking_id']}")
print(f"  Canal: {payload['canal_venda_normalizado']}")
print(f"  Valor pago: R$ {payload['valor_pago_num']:.2f}")
print(f"  Data viagem: {payload['data_viagem']}")
print(f"  Data solicitacao: {payload['data_solicitacao']}")
print(f"  Dias antes: {payload['dias_antes']}")

# Este output pode ser enviado para:
# - Workflow pai (orquestrador)
# - Workflow Filho B (AgentePlanoResolucao)
# - Sistema de notificacoes
# - Banco de dados para auditoria

# Exemplo: enviar para workflow pai ou proximo stage
# send_task("workflow_pai", output_decisao)

print("\nOutput montado com sucesso!")
print("Workflow Motor de Politicas de Pos-Venda concluido.")

# Completa a task atual
task.complete()
print("=== Step 5 Concluido ===")
