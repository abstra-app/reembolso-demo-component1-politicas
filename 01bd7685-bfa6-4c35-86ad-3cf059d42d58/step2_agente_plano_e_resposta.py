"""
STEP 2: Agente Plano e Resposta

Responsabilidades:
- Receber o contexto_agente do tasklet anterior
- Construir um prompt detalhado para a IA
- Chamar abstra.ai.prompt() com formato estruturado
- Gerar ACOES, RESPOSTA_SUGERIDA e ESCALAR_SUPERVISOR
- Enviar task para o proximo tasklet
"""

from abstra.tasks import get_trigger_task, send_task
from abstra.ai import prompt

print("=== STEP 2: Agente Plano e Resposta ===")

# Recebe a task do step anterior
task = get_trigger_task()
contexto_agente = task.payload

print(f"\nTask recebida: {task.id}")
print(f"Tipo da task: {task.type}")

# Extrai os dados do contexto
texto_solicitacao = contexto_agente.get("texto_solicitacao", "")
tipo_solicitacao = contexto_agente.get("tipo_solicitacao", "")
motivo = contexto_agente.get("motivo", "")
elegivel = contexto_agente.get("elegivel", False)
valor_reembolso = contexto_agente.get("valor_reembolso", 0.0)
codigo_regra_aplicada = contexto_agente.get("codigo_regra_aplicada", "")
restricoes = contexto_agente.get("restricoes", None)

print(f"\n[CONTEXTO] Processando solicitacao:")
print(f"  - Tipo: {tipo_solicitacao}")
print(f"  - Motivo: {motivo}")
print(f"  - Elegivel: {elegivel}")
print(f"  - Valor aprovado: R$ {valor_reembolso:.2f}")

# Monta o prompt para a IA
prompt_text = f"""
Voce e um agente especializado em atendimento ao cliente de uma empresa de transporte rodoviario.

Sua missao e analisar a solicitacao do cliente e criar:
1. Um PLANO DE ACOES estruturado
2. Uma RESPOSTA SUGERIDA empatica e clara para o cliente
3. Decidir se o caso deve ser ESCALADO PARA SUPERVISOR

CONTEXTO DA SOLICITACAO:
- Texto do cliente: "{texto_solicitacao}"
- Tipo de solicitacao: {tipo_solicitacao}
- Motivo: {motivo}

DECISAO DE POLITICA JA TOMADA (NAO PODE SER ALTERADA):
- Elegivel para reembolso: {"SIM" if elegivel else "NAO"}
- Valor de reembolso aprovado: R$ {valor_reembolso:.2f}
- Regra aplicada: {codigo_regra_aplicada}
- Restricoes: {restricoes if restricoes else "Nenhuma"}

IMPORTANTE:
- Voce NAO pode aumentar o valor de reembolso alem de R$ {valor_reembolso:.2f}
- Se elegivel = false, NAO pode sugerir reembolso em dinheiro
- Respeite as restricoes impostas pela politica
- Analise o tom do cliente (calmo, frustrado, furioso) para decidir sobre escalonamento
- Seja empatico e claro na resposta

TIPOS DE ACOES DISPONIVEIS:
- REEMBOLSO: reembolso em dinheiro (campo: valor)
- ENVIAR_VOUCHER: voucher para proxima compra (campo: valor)
- NAO_REEMBOLSAR: negar reembolso (campo: motivo)
- REMARCAR_VIAGEM: remarcar para outra data (campo: nova_data no formato YYYY-MM-DD)
- TAGUEAR_CLIENTE: adicionar tag ao perfil (campo: tag, ex: ALTO_RISCO, VIP, REINCIDENTE)
- CONFIRMAR_COM_CLIENTE: pedir confirmacao (campo: canal, ex: email, whatsapp)

CRITERIOS PARA ESCALONAMENTO:
- Cliente muito insatisfeito ou furioso
- Valor muito alto (acima de R$ 500)
- Reincidencia ou historico de problemas
- Situacao complexa ou atipica

Gere sua resposta no formato JSON especificado.
"""

# Define o formato estruturado esperado
formato_resposta = {
    "ACOES": [
        {
            "tipo": "string",
            "valor": "number (opcional)",
            "motivo": "string (opcional)",
            "tag": "string (opcional)",
            "nova_data": "string (opcional)",
            "canal": "string (opcional)"
        }
    ],
    "RESPOSTA_SUGERIDA": "string",
    "ESCALAR_SUPERVISOR": "boolean"
}

print("\n[IA] Chamando modelo de IA...")

# Chama a IA com formato estruturado
resposta_ia = prompt(prompt_text, format=formato_resposta)

print("[IA] Resposta recebida com sucesso!")
print(f"  - Numero de acoes sugeridas: {len(resposta_ia.get('ACOES', []))}")
print(f"  - Escalar supervisor: {resposta_ia.get('ESCALAR_SUPERVISOR', False)}")

# Prepara payload para o proximo step
payload_proximo_step = {
    "contexto_original": contexto_agente,
    "resposta_ia": resposta_ia
}

# Envia task para o proximo step
send_task("resposta_ia_gerada", payload_proximo_step)

print(f"\n[TASK ENVIADA] Tipo: 'resposta_ia_gerada'")
print("=== STEP 2 Concluido ===")

# Completa a task
task.complete()
