"""
STEP 3: Validar Acoes Contra Politica

Responsabilidades:
- Receber a resposta da IA do tasklet anterior
- Aplicar validacoes deterministicas
- Garantir que acoes nao violem a politica
- Ajustar ou remover acoes inconsistentes
- Enviar task para o proximo tasklet
"""

from abstra.tasks import get_trigger_task, send_task

print("=== STEP 3: Validar Acoes Contra Politica ===")

# Recebe a task do step anterior
task = get_trigger_task()
payload = task.payload

print(f"\nTask recebida: {task.id}")
print(f"Tipo da task: {task.type}")

# Extrai os dados
contexto_original = payload.get("contexto_original", {})
resposta_ia = payload.get("resposta_ia", {})

# Dados do contexto original
elegivel = contexto_original.get("elegivel", False)
valor_reembolso = contexto_original.get("valor_reembolso", 0.0)
restricoes = contexto_original.get("restricoes", None)

# Dados da resposta da IA
acoes_ia = resposta_ia.get("ACOES", [])
resposta_sugerida = resposta_ia.get("RESPOSTA_SUGERIDA", "")
escalar_supervisor = resposta_ia.get("ESCALAR_SUPERVISOR", False)

print(f"\n[VALIDACAO] Iniciando validacao de {len(acoes_ia)} acao(oes)...")
print(f"  - Elegivel: {elegivel}")
print(f"  - Valor aprovado: R$ {valor_reembolso:.2f}")
print(f"  - Restricoes: {restricoes}")

# Lista para armazenar acoes validadas
acoes_validadas = []
violacoes_encontradas = []

# Valida cada acao
for i, acao in enumerate(acoes_ia):
    tipo_acao = acao.get("tipo", "")
    print(f"\n[VALIDACAO] Acao {i+1}: {tipo_acao}")
    
    # VALIDACAO 1: Se nao elegivel, nao pode ter REEMBOLSO com valor > 0
    if not elegivel and tipo_acao == "REEMBOLSO":
        valor_acao = acao.get("valor", 0)
        if valor_acao > 0:
            violacao = f"Tentativa de reembolso R$ {valor_acao:.2f} quando ELEGIVEL = false"
            violacoes_encontradas.append(violacao)
            print(f"  [X] VIOLACAO: {violacao}")
            print(f"  [X] Acao removida")
            continue
    
    # VALIDACAO 2: Valor de reembolso nao pode exceder o aprovado
    if tipo_acao == "REEMBOLSO":
        valor_acao = acao.get("valor", 0)
        if valor_acao > valor_reembolso:
            violacao = f"Tentativa de reembolso R$ {valor_acao:.2f} excede aprovado R$ {valor_reembolso:.2f}"
            violacoes_encontradas.append(violacao)
            print(f"  [!] VIOLACAO: {violacao}")
            print(f"  [!] Ajustando valor para R$ {valor_reembolso:.2f}")
            acao["valor"] = valor_reembolso
    
    # VALIDACAO 3: Se restricao = APENAS_VOUCHER_POR_EXCECAO, nao pode ter REEMBOLSO
    if restricoes == "APENAS_VOUCHER_POR_EXCECAO" and tipo_acao == "REEMBOLSO":
        violacao = "Tentativa de reembolso quando restricao permite apenas voucher"
        violacoes_encontradas.append(violacao)
        print(f"  [X] VIOLACAO: {violacao}")
        print(f"  [X] Acao removida")
        continue
    
    # Acao passou nas validacoes
    print(f"  [OK] Acao validada")
    acoes_validadas.append(acao)

# VALIDACAO 4: Se nao elegivel e nao tem NAO_REEMBOLSAR, adiciona automaticamente
if not elegivel and not any(a.get("tipo") == "NAO_REEMBOLSAR" for a in acoes_validadas):
    motivo = contexto_original.get("motivo", "POLITICA_NAO_PERMITE")
    acoes_validadas.insert(0, {
        "tipo": "NAO_REEMBOLSAR",
        "motivo": motivo
    })
    print(f"\n[AUTO] Adicionada acao NAO_REEMBOLSAR (motivo: {motivo})")

# Se houve violacoes criticas, escala para supervisor
if violacoes_encontradas:
    print(f"\n[ALERTA] {len(violacoes_encontradas)} violacao(oes) encontrada(s):")
    for v in violacoes_encontradas:
        print(f"  - {v}")
    escalar_supervisor = True
    print("[ALERTA] Caso escalado para supervisor devido a violacoes")

print(f"\n[RESULTADO] Validacao concluida:")
print(f"  - Acoes validadas: {len(acoes_validadas)}")
print(f"  - Violacoes: {len(violacoes_encontradas)}")
print(f"  - Escalar supervisor: {escalar_supervisor}")

# Prepara payload para o proximo step
payload_proximo_step = {
    "contexto_original": contexto_original,
    "acoes_validadas": acoes_validadas,
    "resposta_sugerida": resposta_sugerida,
    "escalar_supervisor": escalar_supervisor,
    "violacoes": violacoes_encontradas
}

# Envia task para o proximo step
send_task("acoes_validadas", payload_proximo_step)

print(f"\n[TASK ENVIADA] Tipo: 'acoes_validadas'")
print("=== STEP 3 Concluido ===")

# Completa a task
task.complete()
