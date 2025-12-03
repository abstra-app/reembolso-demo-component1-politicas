"""
Step 1: Normalizar e Validar Entrada
Valida campos obrigatórios, converte tipos e normaliza dados de entrada.
"""
from abstra.tasks import get_trigger_task, send_task
from datetime import datetime

print("=== Step 1: Normalizar e Validar Entrada ===")

# Recebe a task de entrada
task = get_trigger_task()
payload = task.payload

print(f"Payload recebido: {payload}")

# Validação de campos obrigatórios
campos_obrigatorios = ["booking_id", "canal_venda", "data_viagem", "data_solicitacao", "valor_pago"]
campos_faltantes = [campo for campo in campos_obrigatorios if campo not in payload]

if campos_faltantes:
    erro = f"Campos obrigatórios faltando: {', '.join(campos_faltantes)}"
    print(f"ERRO: {erro}")
    raise ValueError(erro)

# Extração e normalização dos dados
booking_id = str(payload["booking_id"])
canal_venda_normalizado = str(payload["canal_venda"]).lower().strip()
texto_solicitacao = payload.get("texto_solicitacao", "")

# Conversão de valor_pago para número
try:
    valor_pago_num = float(payload["valor_pago"])
    print(f"Valor pago convertido: R$ {valor_pago_num:.2f}")
except (ValueError, TypeError) as e:
    erro = f"Erro ao converter valor_pago para número: {e}"
    print(f"ERRO: {erro}")
    raise ValueError(erro)

# Conversão de datas (formato ISO: YYYY-MM-DD)
try:
    data_viagem_str = str(payload["data_viagem"])
    data_solicitacao_str = str(payload["data_solicitacao"])
    
    # Parse das datas (aceita formato ISO completo ou apenas data)
    if "T" in data_viagem_str:
        data_viagem_dt = datetime.fromisoformat(data_viagem_str.replace("Z", "+00:00")).date()
    else:
        data_viagem_dt = datetime.fromisoformat(data_viagem_str).date()
    
    if "T" in data_solicitacao_str:
        data_solicitacao_dt = datetime.fromisoformat(data_solicitacao_str.replace("Z", "+00:00")).date()
    else:
        data_solicitacao_dt = datetime.fromisoformat(data_solicitacao_str).date()
    
    print(f"Data da viagem: {data_viagem_dt}")
    print(f"Data da solicitação: {data_solicitacao_dt}")
    
except (ValueError, TypeError) as e:
    erro = f"Erro ao converter datas (use formato ISO YYYY-MM-DD): {e}"
    print(f"ERRO: {erro}")
    raise ValueError(erro)

# Monta payload normalizado para o próximo step
payload_normalizado = {
    "booking_id": booking_id,
    "canal_venda_normalizado": canal_venda_normalizado,
    "data_viagem": str(data_viagem_dt),
    "data_solicitacao": str(data_solicitacao_dt),
    "valor_pago_num": valor_pago_num,
    "texto_solicitacao": texto_solicitacao
}

print(f"Dados normalizados com sucesso!")
print(f"Booking ID: {booking_id}")
print(f"Canal: {canal_venda_normalizado}")
print(f"Valor: R$ {valor_pago_num:.2f}")

# Envia para o próximo step
send_task("calcular_contexto_tempo", payload_normalizado)
print("Task enviada para Step 2: Calcular Contexto Tempo")

# Completa a task atual
task.complete()
print("=== Step 1 Concluído ===")
