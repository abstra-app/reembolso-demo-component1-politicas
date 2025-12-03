"""
STEP 1: Montar Contexto para Agente

Responsabilidades:
- Receber os dados de entrada via get_trigger_task()
- Extrair e validar os 7 campos de entrada
- Montar um objeto contexto_agente consolidado
- Enviar task para o proximo tasklet
"""

from abstra.tasks import get_trigger_task, send_task

print("=== STEP 1: Montar Contexto para Agente ===")

# Recebe a task que disparou este tasklet
task = get_trigger_task()
input_data = task.payload

print(f"\nTask recebida: {task.id}")
print(f"Tipo da task: {task.type}")

# Extrai os campos de entrada
texto_solicitacao = input_data.get("texto_solicitacao", "")
tipo_solicitacao = input_data.get("TIPO_SOLICITACAO", "")
motivo = input_data.get("MOTIVO", "")
elegivel = input_data.get("ELEGIVEL", False)
valor_reembolso = input_data.get("VALOR_REEMBOLSO", 0.0)
codigo_regra_aplicada = input_data.get("CODIGO_REGRA_APLICADA", "")
restricoes = input_data.get("RESTRICOES", None)

# Log dos dados recebidos
print(f"\n[INPUT] Dados recebidos:")
print(f"  - Texto: {texto_solicitacao[:80]}...")
print(f"  - Tipo: {tipo_solicitacao}")
print(f"  - Motivo: {motivo}")
print(f"  - Elegivel: {elegivel}")
print(f"  - Valor Reembolso: R$ {valor_reembolso:.2f}")
print(f"  - Codigo Regra: {codigo_regra_aplicada}")
print(f"  - Restricoes: {restricoes}")

# Validacao basica dos campos obrigatorios
if not texto_solicitacao:
    print("\n[ERRO] Campo 'texto_solicitacao' e obrigatorio!")
    task.complete()
    exit()

if not tipo_solicitacao:
    print("\n[ERRO] Campo 'TIPO_SOLICITACAO' e obrigatorio!")
    task.complete()
    exit()

# Monta o contexto consolidado
contexto_agente = {
    "texto_solicitacao": texto_solicitacao,
    "tipo_solicitacao": tipo_solicitacao,
    "motivo": motivo,
    "elegivel": elegivel,
    "valor_reembolso": valor_reembolso,
    "codigo_regra_aplicada": codigo_regra_aplicada,
    "restricoes": restricoes
}

print(f"\n[OUTPUT] Contexto montado com sucesso!")
print(f"  - Total de campos: {len(contexto_agente)}")

# Envia task para o proximo step
send_task("contexto_montado", contexto_agente)

print(f"\n[TASK ENVIADA] Tipo: 'contexto_montado'")
print("=== STEP 1 Concluido ===")

# Completa a task original
task.complete()
