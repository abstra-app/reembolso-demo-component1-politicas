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
    # Resultados da análise de política
    "TIPO_SOLICITACAO": TIPO_SOLICITACAO,
    "MOTIVO": MOTIVO,
    "ELEGIVEL": ELEGIVEL,
    "VALOR_REEMBOLSO": VALOR_REEMBOLSO,
    "CODIGO_REGRA_APLICADA": CODIGO_REGRA_APLICADA,
    "RESTRICOES": RESTRICOES,
    
    # ⭐ CAMPOS ESSENCIAIS PARA O COMPONENT 2 (Agente de Resolução)
    # O texto original é necessário para gerar resposta personalizada
    "texto_solicitacao": payload.get("texto_solicitacao", ""),
    
    # Dados adicionais úteis para contexto
    "booking_id": payload.get("booking_id", ""),
    "canal_venda": payload.get("canal_venda_normalizado", ""),
    "valor_pago": payload.get("valor_pago_num", 0.0),
    "data_viagem": payload.get("data_viagem", ""),
    "data_solicitacao": payload.get("data_solicitacao", ""),
    "dias_antes": payload.get("dias_antes", 0)
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

# Envia o output final para o proximo stage/workflow
print("\n>>> Enviando output final...")
texto_solicitacao = output_decisao.get('texto_solicitacao', '')
print(f"  - Incluindo texto_solicitacao: {len(str(texto_solicitacao))} caracteres")
print(f"  - Booking ID: {output_decisao.get('booking_id')}")
print(f"  - Canal: {output_decisao.get('canal_venda')}")
print(f"  - Valor pago: R$ {output_decisao.get('valor_pago', 0):.2f}")

send_task(
    "decisao_final",
    output_decisao
)

print("\nOutput montado e enviado com sucesso!")
print("Workflow Motor de Politicas de Pos-Venda concluido.")

# Completa a task atual
task.complete()
print("=== Step 5 Concluido ===")
