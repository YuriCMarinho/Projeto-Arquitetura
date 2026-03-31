# Simulador Mic-1 — Arquitetura II
# Suporta: ILOAD x, DUP, BIPUSH byte

# -------------------------------------------------------
# Estado da máquina
# -------------------------------------------------------

regs = {
    'H'  : 0,
    'OPC': 0,
    'TOS': 0,
    'CPP': 0,
    'LV' : 0,
    'SP' : 0,
    'MBR': 0,
    'PC' : 0,
    'MDR': 0,
    'MAR': 0,
}
mem = {}

# -------------------------------------------------------
# Carrega os arquivos de entrada
# -------------------------------------------------------

# Memória: cada linha é uma palavra de 32 bits, linha N = endereço N
with open("dados_etapa3_tarefa1.txt") as f:
    for endereco, linha in enumerate(f):
        if linha.strip():
            mem[endereco] = int(linha.strip(), 2)

# Registradores: formato "nome = valor_binario"
try:
    with open("registradores_etapa3_tarefa1.txt") as f:
        for linha in f:
            if '=' not in linha:
                continue
            nome, valor = linha.strip().split('=')
            nome  = nome.strip().upper()
            valor = valor.strip()
            if nome in regs:
                regs[nome] = int(valor, 2)
except FileNotFoundError:
    print("Aviso: arquivo de registradores não encontrado. Usando valores padrão.\n")

# -------------------------------------------------------
# Funções de log
# -------------------------------------------------------

def log_regs(momento):
    valores = "  ".join(f"{r}={regs[r]}" for r in regs)
    print(f"  [{momento}]  {valores}")

def log_mem(titulo):
    celulas = "  ".join(f"[{e}]={v}" for e, v in sorted(mem.items()))
    print(f"  {titulo}: {celulas}")

def micro(descricao, logica, bus_B, bus_C):
    print(f"\n  Microinstrução: {descricao}")
    log_regs("início")
    print(f"  Bus B: {bus_B}   Bus C: {', '.join(bus_C)}")
    logica()
    log_regs("fim   ")

# -------------------------------------------------------
# Instrução ILOAD x
# Carrega a variável local de índice x no topo da pilha
# -------------------------------------------------------

def iload(x):

    # Copia a base das variáveis locais para H
    micro("H = LV",
          lambda: regs.update({'H': regs['LV']}),
          bus_B="LV", bus_C=["H"])

    # Avança H até o endereço da variável desejada (x incrementos)
    for _ in range(x):
        micro("H = H+1",
              lambda: regs.update({'H': regs['H'] + 1}),
              bus_B="H", bus_C=["H"])

    # Lê o valor da memória naquele endereço
    def ler_memoria():
        regs['MAR'] = regs['H']
        regs['MDR'] = mem.get(regs['H'], 0)
    micro("MAR = H; rd", ler_memoria, bus_B="H", bus_C=["MAR", "MDR"])

    # Empilha o valor lido no novo topo da pilha
    def empilhar():
        regs['SP']  += 1
        regs['MAR']  = regs['SP']
        mem[regs['MAR']] = regs['MDR']
    micro("MAR = SP = SP+1; wr", empilhar, bus_B="SP", bus_C=["MAR", "SP"])

    # Atualiza TOS com o valor empilhado
    micro("TOS = MDR",
          lambda: regs.update({'TOS': regs['MDR']}),
          bus_B="MDR", bus_C=["TOS"])

# -------------------------------------------------------
# Instrução DUP
# Duplica o valor no topo da pilha
# -------------------------------------------------------

def dup():

    # Abre espaço na pilha
    def abrir_espaco():
        regs['SP']  += 1
        regs['MAR']  = regs['SP']
    micro("MAR = SP = SP+1", abrir_espaco, bus_B="SP", bus_C=["MAR", "SP"])

    # Copia o topo atual para a nova posição
    def copiar_topo():
        regs['MDR'] = regs['TOS']
        mem[regs['MAR']] = regs['MDR']
    micro("MDR = TOS; wr", copiar_topo, bus_B="TOS", bus_C=["MDR"])

# -------------------------------------------------------
# Instrução BIPUSH byte
# Empilha um valor de 8 bits fornecido diretamente
# -------------------------------------------------------

def bipush(byte_arg):

    # Abre espaço na pilha
    def abrir_espaco():
        regs['SP']  += 1
        regs['MAR']  = regs['SP']
    micro("SP = MAR = SP+1", abrir_espaco, bus_B="SP", bus_C=["MAR", "SP"])

    # Fetch especial: os 8 bits do argumento vão direto para MBR e H
    # Código completo: [8 bits do argumento] + 000000000110000
    # READ e WRITE em 1 simultaneamente sinalizam esse caso especial
    codigo = f"{byte_arg}000000000110000"
    def fetch_especial():
        regs['MBR'] = int(byte_arg, 2)
        regs['H']   = regs['MBR']
    micro(f"fetch [{codigo}]", fetch_especial, bus_B="N/A", bus_C=["MBR", "H"])

    # Grava o valor carregado no topo da pilha
    def empilhar():
        regs['MDR'] = regs['H']
        regs['TOS'] = regs['H']
        mem[regs['MAR']] = regs['MDR']
    micro("MDR = TOS = H; wr", empilhar, bus_B="H", bus_C=["MDR", "TOS"])

# -------------------------------------------------------
# Execução
# -------------------------------------------------------

print("=" * 55)
print("  ESTADO INICIAL")
print("=" * 55)
log_regs("inicial")
log_mem("Memória")

with open("instruções.txt", encoding="utf-8") as f:
    instrucoes = [linha.strip() for linha in f if linha.strip()]

for instrucao in instrucoes:
    partes = instrucao.split()
    print(f"\n{'=' * 55}")
    print(f"  INSTRUÇÃO: {instrucao}")
    print(f"{'=' * 55}")

    if   partes[0] == "ILOAD":  iload(int(partes[1]))
    elif partes[0] == "DUP":    dup()
    elif partes[0] == "BIPUSH": bipush(partes[1])
    else:
        print(f"  Instrução desconhecida: '{partes[0]}'")

    print()
    log_mem(f"Memória após '{instrucao}'")
