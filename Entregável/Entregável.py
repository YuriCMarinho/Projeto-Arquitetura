# Simulador Mic-1 — Arquitetura II
# Suporta: ILOAD x, DUP, BIPUSH byte

#Ordem: Valores nas linhas da memoria ant -> registradores -> bar B -> bar C -> Valores na memoria Pos 


# -------------------------------------------------------
# Estado da máquina
# -------------------------------------------------------

regs = {
    'mar': 0,
    'mdr': 0,
    'pc' : 0,
    'mbr': 0,
    'sp' : 0,
    'lv' : 0,
    'cpp': 0,
    'tos': 0,
    'opc': 0,
    'h'  : 0,
}
mem = {}

# -------------------------------------------------------
# Carrega os arquivos de entrada
# -------------------------------------------------------

with open("dados_etapa3_tarefa1.txt") as f:
    for endereco, linha in enumerate(f):
        if linha.strip():
            mem[endereco] = int(linha.strip(), 2)

try:
    with open("registradores_etapa3_tarefa1.txt") as f:
        for linha in f:
            if '=' not in linha:
                continue
            nome, valor = linha.strip().split('=')
            nome  = nome.strip().lower()
            valor = valor.strip()
            if nome in regs:
                regs[nome] = int(valor, 2)
except FileNotFoundError:
    print("Aviso: arquivo de registradores não encontrado. Usando valores padrão.\n")

# -------------------------------------------------------
# Funções de formatação
# -------------------------------------------------------

def para_bin(valor, bits=32):
    """Converte inteiro para string binária com o número de bits correto."""
    return format(valor, f'0{bits}b')

def imprimir_regs():
    for nome, valor in regs.items():
        bits = 8 if nome == 'mbr' else 32
        print(f"{nome} = {para_bin(valor, bits)}")

def imprimir_mem():
    print("*******************************")
    for endereco in range(len(mem)):
        print(para_bin(mem[endereco]))
    print("*******************************")

# -------------------------------------------------------
# Instruções IJVM 
# -------------------------------------------------------

def iload(x):
    regs['h'] = regs['lv']
    for _ in range(x):
        regs['h'] += 1
    regs['mar'] = regs['h']
    regs['mdr'] = mem.get(regs['h'], 0)
    regs['sp']  += 1
    regs['mar']  = regs['sp']
    mem[regs['mar']] = regs['mdr']
    regs['tos'] = regs['mdr']

    bar_b = "lv, sp"
    bar_c = "h, mar, sp, tos"
    return bar_b, bar_c

def dup():
    regs['sp']  += 1
    regs['mar']  = regs['sp']
    regs['mdr']  = regs['tos']
    mem[regs['mar']] = regs['mdr']

    bar_b = "sp, tos"
    bar_c = "mar, sp, mdr"
    return bar_b, bar_c

def bipush(byte_arg):
    regs['sp']  += 1
    regs['mar']  = regs['sp']
    regs['mbr']  = int(byte_arg, 2)
    regs['h']    = regs['mbr']
    regs['mdr']  = regs['h']
    regs['tos']  = regs['h']
    mem[regs['mar']] = regs['mdr']

    bar_b = "sp"
    bar_c = "h, tos, mdr, sp, mar"
    return bar_b, bar_c

# -------------------------------------------------------
# Execução
# -------------------------------------------------------

print("==============================================")
print("> Estado da memoria inicial")
imprimir_mem()
print("> Estado dos registradores iniciais")
imprimir_regs()

with open("instruções.txt", encoding="utf-8") as f:
    instrucoes = [linha.strip() for linha in f if linha.strip()]

print()
print("==============================================")
print("Comecando!")

for numero_instrucao, instrucao in enumerate(instrucoes, start=1):
    partes  = instrucao.split()
    comando = partes[0].upper()

    # Salva estado antes de executar
    regs_antes = dict(regs)
    mem_antes  = dict(mem)

    # Executa a instrução e captura os barramentos
    if   comando == "ILOAD":  bar_b, bar_c = iload(int(partes[1]))
    elif comando == "DUP":    bar_b, bar_c = dup()
    elif comando == "BIPUSH": bar_b, bar_c = bipush(partes[1])
    else:
        print(f"Instrução desconhecida: '{comando}'")
        continue

    # Exibe o log no formato esperado
    print(f"instrucao = {instrucao}")
    print("==============================================")
    print(f"Instrução {numero_instrucao}")
    print(f"bar_b = {bar_b}")
    print(f"bar_c = {bar_c}")
    print()
    print("> Registradores antes da instrucao")
    for nome, valor in regs_antes.items():
        bits = 8 if nome == 'mbr' else 32
        print(f"{nome} = {para_bin(valor, bits)}")
    print()
    print("> Registradores depois da instrucao")
    imprimir_regs()
    print()
    print("> Memoria depois da instrucao")
    imprimir_mem()
