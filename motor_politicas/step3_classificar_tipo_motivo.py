"""
Step 3: Classificar Tipo de Solicitacao e Motivo
Classifica o tipo e motivo da solicitacao de forma deterministica.
"""
from abstra.tasks import get_trigger_task, send_task

print("=== Step 3: Classificar Tipo e Motivo ===")

# Recebe a task do step anterior
task = get_trigger_task()
payload = task.payload

print(f"Payload recebido: {payload}")

# Extrai dados necessarios para classificacao
booking_id = payload["booking_id"]
texto_solicitacao = payload.get("texto_solicitacao", "").lower()
dias_antes = payload["dias_antes"]
solicitacao_apos_viagem = payload["solicitacao_apos_viagem"]

print(f"Booking ID: {booking_id}")
print(f"Texto da solicitacao: {texto_solicitacao[:100]}...")
print(f"Dias antes: {dias_antes}")

# Classificacao deterministica baseada em regras simples
# Para demo, usamos deteccao de palavras-chave no texto

TIPO_SOLICITACAO = "OUTROS"
MOTIVO = "OUTROS"

# Detecta tipo de solicitacao
if any(palavra in texto_solicitacao for palavra in ["reembolso", "devolucao", "cancelar", "cancelamento"]):
    TIPO_SOLICITACAO = "REEMBOLSO"
elif any(palavra in texto_solicitacao for palavra in ["remarcar", "remarcacao", "mudar data", "alterar data"]):
    TIPO_SOLICITACAO = "REMARCACAO"
elif any(palavra in texto_solicitacao for palavra in ["reclamacao", "problema", "atraso"]):
    TIPO_SOLICITACAO = "RECLAMACAO_SERVICO"

# Detecta motivo especifico
if TIPO_SOLICITACAO == "REEMBOLSO":
    if dias_antes >= 1:
        MOTIVO = "CANCELAMENTO_CLIENTE_ANTECIPADO"
    elif "atraso" in texto_solicitacao or "atrasou" in texto_solicitacao:
        MOTIVO = "ATRASO_ONIBUS"
    elif "nao embarquei" in texto_solicitacao or "perdi" in texto_solicitacao or "no-show" in texto_solicitacao:
        MOTIVO = "NO_SHOW_CLIENTE"
    else:
        MOTIVO = "OUTROS"
elif TIPO_SOLICITACAO == "REMARCACAO":
    MOTIVO = "ALTERACAO_PLANO_CLIENTE"
elif "atraso" in texto_solicitacao:
    MOTIVO = "ATRASO_ONIBUS"

print(f"Classificacao determinada:")
print(f"  TIPO_SOLICITACAO: {TIPO_SOLICITACAO}")
print(f"  MOTIVO: {MOTIVO}")

# Monta payload enriquecido com classificacao
payload_classificado = {
    **payload,
    "TIPO_SOLICITACAO": TIPO_SOLICITACAO,
    "MOTIVO": MOTIVO
}

print("Classificacao concluida com sucesso!")

# Envia para o proximo step
send_task("aplicar_politicas", payload_classificado)
print("Task enviada para Step 4: Aplicar Politicas")

# Completa a task atual
task.complete()
print("=== Step 3 Concluido ===")
