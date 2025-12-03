"""
Step 2: Calcular Contexto de Tempo
Calcula dias_antes e flags temporais para aplicacao de politicas.
"""
from abstra.tasks import get_trigger_task, send_task
from datetime import datetime

print("=== Step 2: Calcular Contexto de Tempo ===")

# Recebe a task do step anterior
task = get_trigger_task()
payload = task.payload

print(f"Payload recebido: {payload}")

# Extrai as datas
data_viagem = datetime.fromisoformat(payload["data_viagem"]).date()
data_solicitacao = datetime.fromisoformat(payload["data_solicitacao"]).date()

print(f"Data da viagem: {data_viagem}")
print(f"Data da solicitacao: {data_solicitacao}")

# Calcula a diferenca em dias
dias_antes = (data_viagem - data_solicitacao).days

print(f"Dias antes da viagem: {dias_antes}")

# Deriva flags auxiliares
solicitacao_antes_da_viagem = dias_antes > 0
solicitacao_apos_viagem = dias_antes < 0
solicitacao_no_dia_viagem = dias_antes == 0

print(f"Solicitacao antes da viagem: {solicitacao_antes_da_viagem}")
print(f"Solicitacao apos a viagem: {solicitacao_apos_viagem}")
print(f"Solicitacao no dia da viagem: {solicitacao_no_dia_viagem}")

# Monta payload enriquecido com contexto temporal
payload_enriquecido = {
    **payload,
    "dias_antes": dias_antes,
    "solicitacao_antes_da_viagem": solicitacao_antes_da_viagem,
    "solicitacao_apos_viagem": solicitacao_apos_viagem,
    "solicitacao_no_dia_viagem": solicitacao_no_dia_viagem
}

print("Contexto temporal calculado com sucesso!")

# Envia para o proximo step
send_task("classificar_tipo_motivo", payload_enriquecido)
print("Task enviada para Step 3: Classificar Tipo e Motivo")

# Completa a task atual
task.complete()
print("=== Step 2 Concluido ===")
