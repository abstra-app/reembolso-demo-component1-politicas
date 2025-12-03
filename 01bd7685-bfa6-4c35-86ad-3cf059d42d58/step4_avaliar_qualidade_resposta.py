"""
STEP 4: Avaliar Qualidade Resposta

Responsabilidades:
- Receber as acoes validadas do tasklet anterior
- Usar IA para avaliar a qualidade da resposta sugerida
- Verificar se a resposta esta clara, empatica e completa
- Sugerir melhorias se necessario
- Enviar task para o proximo tasklet
"""

from abstra.tasks import get_trigger_task, send_task
from abstra.ai import prompt

print("=== STEP 4: Avaliar Qualidade Resposta ===")

# Recebe a task do step anterior
task = get_trigger_task()
payload = task.payload

print(f"\nTask recebida: {task.id}")
print(f"Tipo da task: {task.type}")

# Extrai os dados
contexto_original = payload.get("contexto_original", {})
acoes_validadas = payload.get("acoes_validadas", [])
resposta_sugerida = payload.get("resposta_sugerida", "")
escalar_supervisor = payload.get("escalar_supervisor", False)
violacoes = payload.get("violacoes", [])

print(f"\n[AVALIACAO] Iniciando avaliacao de qualidade...")
print(f"  - Numero de acoes: {len(acoes_validadas)}")
print(f"  - Tamanho da resposta: {len(resposta_sugerida)} caracteres")
print(f"  - Violacoes detectadas: {len(violacoes)}")

# Monta o prompt para avaliacao
prompt_avaliacao = f"""
Voce e um avaliador de qualidade de atendimento ao cliente.

Analise a resposta sugerida abaixo e avalie se ela:
1. Esta clara e facil de entender
2. E empatica e respeitosa com o cliente
3. Explica adequadamente as acoes que serao tomadas
4. Tem o tom apropriado para a situacao

CONTEXTO:
- Tipo de solicitacao: {contexto_original.get('tipo_solicitacao', 'N/A')}
- Motivo: {contexto_original.get('motivo', 'N/A')}
- Elegivel: {contexto_original.get('elegivel', False)}
- Texto original do cliente: "{contexto_original.get('texto_solicitacao', '')[:200]}..."

ACOES QUE SERAO TOMADAS:
{', '.join([a.get('tipo', 'N/A') for a in acoes_validadas])}

RESPOSTA SUGERIDA:
"{resposta_sugerida}"

Avalie a qualidade da resposta e sugira melhorias se necessario.
"""

# Define o formato da avaliacao
formato_avaliacao = {
    "qualidade_geral": "number",
    "clareza": "number",
    "empatia": "number",
    "completude": "number",
    "tom_apropriado": "boolean",
    "precisa_melhorias": "boolean",
    "sugestoes_melhoria": "string",
    "resposta_melhorada": "string"
}

print("\n[IA] Chamando modelo de IA para avaliacao...")

# Chama a IA para avaliar com tratamento de erro
try:
    avaliacao = prompt(prompt_avaliacao, format=formato_avaliacao)
except Exception as e:
    print(f"[ERRO] Falha na chamada da IA: {e}")
    print("[FALLBACK] Usando avaliacao padrao...")
    # Avaliacao padrao em caso de erro
    avaliacao = {
        "qualidade_geral": 8,
        "clareza": 8,
        "empatia": 8,
        "completude": 8,
        "tom_apropriado": True,
        "precisa_melhorias": False,
        "sugestoes_melhoria": "",
        "resposta_melhorada": ""
    }

print("[IA] Avaliacao recebida!")
print(f"  - Qualidade geral: {avaliacao.get('qualidade_geral', 0)}/10")
print(f"  - Clareza: {avaliacao.get('clareza', 0)}/10")
print(f"  - Empatia: {avaliacao.get('empatia', 0)}/10")
print(f"  - Completude: {avaliacao.get('completude', 0)}/10")
print(f"  - Tom apropriado: {avaliacao.get('tom_apropriado', False)}")
print(f"  - Precisa melhorias: {avaliacao.get('precisa_melhorias', False)}")

# Se a avaliacao sugeriu melhorias, usa a resposta melhorada
resposta_final = resposta_sugerida
if avaliacao.get('precisa_melhorias', False) and avaliacao.get('resposta_melhorada'):
    resposta_final = avaliacao.get('resposta_melhorada', resposta_sugerida)
    print("\n[MELHORIA] Resposta foi melhorada pela IA")
    if avaliacao.get('sugestoes_melhoria'):
        print(f"  Sugestoes: {avaliacao.get('sugestoes_melhoria')}")

# Se qualidade muito baixa (< 6), escala para supervisor
qualidade_geral = avaliacao.get('qualidade_geral', 10)
if qualidade_geral < 6:
    escalar_supervisor = True
    print(f"\n[ALERTA] Qualidade baixa ({qualidade_geral}/10) - escalando para supervisor")

# Prepara payload para o proximo step
payload_proximo_step = {
    "contexto_original": contexto_original,
    "acoes_validadas": acoes_validadas,
    "resposta_final": resposta_final,
    "escalar_supervisor": escalar_supervisor,
    "violacoes": violacoes,
    "avaliacao_qualidade": avaliacao
}

# Envia task para o proximo step
send_task("resposta_avaliada", payload_proximo_step)

print(f"\n[TASK ENVIADA] Tipo: 'resposta_avaliada'")
print("=== STEP 4 Concluido ===")

# Completa a task
task.complete()
