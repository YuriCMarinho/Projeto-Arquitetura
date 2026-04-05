import os

# Simulador Mic-1 — Arquitetura II
# Suporta: ILOAD x, DUP, BIPUSH byte

# -------------------------------------------------------
# Estado da máquina
# -------------------------------------------------------

regs = {
    'mar': 0, # mem address register
    'mdr': 0, # mem data register
    'pc' : 0, # program counter
    'mbr': 0, # mem buffer register
    'sp' : 0, # stack pointer (pro topo)
    'lv' : 0, # local variable
    'cpp': 0, # constant pool pointer
    'tos': 0, # top of stack (valor do topo)
    'opc': 0, # opcode temporario
    'h'  : 0, # registrador aux da ULA
}
mem = {}

# -------------------------------------------------------
# Funções de formatação
# -------------------------------------------------------

def para_bin(valor, bits=32):
    """Converte inteiro para string binária com o número de bits correto."""
    return format(valor, f'0{bits}b')

def imprimir_regs(out):
    for nome, valor in regs.items():
        bits = 8 if nome == 'mbr' else 32 #só o mbr tem 8 bits o resto todo tem 32
        out.write(f"{nome} = {para_bin(valor, bits)}\n")

def imprimir_mem(out):
    out.write("*******************************\n")
    for endereco in range(len(mem)):
        out.write(f"{para_bin(mem[endereco])}\n")
    out.write("*******************************\n")

# -------------------------------------------------------
# Instruções IJVM 
# -------------------------------------------------------

def iload(x): #Carrega variável local na pilha
    regs['h'] = regs['lv']
    for _ in range(x): #+1 x vezes
        regs['h'] += 1
    regs['mar'] = regs['h']
    regs['mdr'] = mem.get(regs['h'], 0) # recebe o valor do endereço da memoria
    regs['sp']  += 1
    regs['mar']  = regs['sp']
    mem[regs['mar']] = regs['mdr']#empilha o valor(ver na memoria depois)
    regs['tos'] = regs['mdr']

    bar_b = "lv, sp"
    bar_c = "h, mar, sp, tos"
    return bar_b, bar_c

def dup(): # Duplica o topo da pilha
    regs['sp']  += 1
    regs['mar']  = regs['sp']
    regs['mdr']  = regs['tos']
    mem[regs['mar']] = regs['mdr']

    bar_b = "sp, tos"
    bar_c = "mar, sp, mdr"
    return bar_b, bar_c

def bipush(byte_arg): #Empilha uma constante de 1 byte
    regs['sp']  += 1
    regs['mar']  = regs['sp']
    regs['mbr']  = int(byte_arg, 2) #recebe o valor do byte
    regs['h']    = regs['mbr']
    regs['mdr']  = regs['h']
    regs['tos']  = regs['h']
    mem[regs['mar']] = regs['mdr'] #wr

    bar_b = "sp"
    bar_c = "h, tos, mdr, sp, mar"
    return bar_b, bar_c

# -------------------------------------------------------
# Execução Principal
# -------------------------------------------------------

def rodar_etapa3(arq_dados, arq_regs, arq_instrucoes, arq_saida):
    
    # 1. Carrega a Memória
    if os.path.exists(arq_dados):
        with open(arq_dados, 'r') as f:
            for endereco, linha in enumerate(f):
                if linha.strip():
                    mem[endereco] = int(linha.strip(), 2)
    
    # 2. Carrega os Registradores
    try:
        with open(arq_regs, 'r') as f:
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

    # 3. Abre o arquivo de LOG para escrita
    with open(arq_saida, 'w', encoding='utf-8') as out:
        
        out.write("==============================================\n")
        out.write("> Estado da memoria inicial\n")
        imprimir_mem(out)
        out.write("> Estado dos registradores iniciais\n")
        imprimir_regs(out)

        # 4. Lê as instruções
        if not os.path.exists(arq_instrucoes):
            out.write("\nErro: Arquivo de instruções não encontrado.\n")
            return

        with open(arq_instrucoes, 'r', encoding='utf-8') as f:
            instrucoes = [linha.strip() for linha in f if linha.strip()]

        out.write("\n==============================================\n")
        out.write("Comecando!\n")

        # 5. Executa as instruções e grava no log
        for numero_instrucao, instrucao in enumerate(instrucoes, start=1):
            partes  = instrucao.split()
            comando = partes[0].upper()

            # Salva estado antes de executar
            regs_antes = dict(regs)

            # Executa a instrução e captura os barramentos
            if   comando == "ILOAD":  bar_b, bar_c = iload(int(partes[1]))
            elif comando == "DUP":    bar_b, bar_c = dup()
            elif comando == "BIPUSH": bar_b, bar_c = bipush(partes[1])
            else:
                out.write(f"Instrução desconhecida: '{comando}'\n")
                continue

            # Escreve o log no formato esperado usando out.write()
            out.write(f"instrucao = {instrucao}\n")
            out.write("==============================================\n")
            out.write(f"Instrução {numero_instrucao}\n")
            out.write(f"bar_b = {bar_b}\n")
            out.write(f"bar_c = {bar_c}\n\n")
            
            out.write("> Registradores antes da instrucao\n")
            for nome, valor in regs_antes.items():
                bits = 8 if nome == 'mbr' else 32
                out.write(f"{nome} = {para_bin(valor, bits)}\n")
            out.write("\n")
            
            out.write("> Registradores depois da instrucao\n")
            imprimir_regs(out)
            out.write("\n")
            
            out.write("> Memoria depois da instrucao\n")
            imprimir_mem(out)
            out.write("\n")

    print(f"Simulação concluída com sucesso! Verifique o arquivo: {os.path.basename(arq_saida)}")


if __name__ == "__main__":
    # Organiza os caminhos usando os.path de forma idêntica à sua referência
    base = os.path.dirname(os.path.abspath(__file__))
    
    arquivo_dados = os.path.join(base, 'dados_etapa3_tarefa1.txt')
    arquivo_regs = os.path.join(base, 'registradores_etapa3_tarefa1.txt')
    arquivo_instrucoes = os.path.join(base, 'instruções.txt')
    arquivo_log = os.path.join(base, 'log_entregavel.txt')
    
    rodar_etapa3(arquivo_dados, arquivo_regs, arquivo_instrucoes, arquivo_log)
