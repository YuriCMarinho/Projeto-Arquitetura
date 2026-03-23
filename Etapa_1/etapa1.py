def to_bin32(valor):
    """Função auxiliar para formatar um número inteiro em uma string binária de 32 bits."""
    return f"{valor & 0xFFFFFFFF:032b}"

def ula_6bits(A, B, instrucao_6bits):
    f0, f1, ena, enb, inva, inc = [int(bit) for bit in instrucao_6bits]
    
    # Aplica Enable
    a_val = A if ena else 0
    b_val = B if enb else 0
    
    # Aplica Inversão
    if inva:
        a_val = ~a_val & 0xFFFFFFFF
        
    carry_in = 1 if inc else 0
    vai_um = 0
    
    # Operações 
    if f0 == 0 and f1 == 0:
        S = a_val & b_val
    elif f0 == 0 and f1 == 1:
        S = a_val | b_val
    elif f0 == 1 and f1 == 0:
        S = ~b_val & 0xFFFFFFFF
    elif f0 == 1 and f1 == 1:
        soma = a_val + b_val + carry_in
        S = soma & 0xFFFFFFFF
        vai_um = 1 if soma > 0xFFFFFFFF else 0
        
    # Retornamos a_val e b_val para imprimir como eles ficaram após ENA/ENB/INVA
    return a_val, b_val, S, vai_um

def rodar_etapa1(arquivo_instrucoes, arquivo_saida):
    # Valores iniciais extraídos do arquivo de saída
    A = 0xFFFFFFFF  # 32 bits '1'
    B = 0x00000001  # Valor 1
    PC = 1
    
    with open(arquivo_saida, 'w') as out:
        # Usamos out.write() em vez de print()
        out.write(f"b = {to_bin32(B)}\n")
        out.write(f"a = {to_bin32(A)}\n\n")
        out.write("Start of Program\n")
    
        with open(arquivo_instrucoes, 'r') as arquivo:
            for linha in arquivo:
                IR = linha.strip()
                if not IR: 
                    continue # Pula linhas vazias
                
                out.write("============================================================\n")
                out.write(f"Cycle {PC}\n\n")
                out.write(f"PC = {PC}\n")
                out.write(f"IR = {IR}\n")
                
                # Roda a instrução na ULA
                a_proc, b_proc, S, co = ula_6bits(A, B, IR)
                
                # Imprime os resultados formatados em 32 bits
                out.write(f"b = {to_bin32(b_proc)}\n")
                out.write(f"a = {to_bin32(a_proc)}\n")
                out.write(f"s = {to_bin32(S)}\n")
                out.write(f"co = {co}\n")
                
                PC += 1
            
        # Finalização do programa
        out.write("============================================================\n")
        out.write(f"Cycle {PC}\n\n")
        out.write(f"PC = {PC}\n")
        out.write("> Line is empty, EOP.\n")

if __name__ == "__main__":
    # Certifique-se de que a primeira linha do seu programa_etapa1.txt seja 111100
    rodar_etapa1('programa_etapa1.txt','log_etapa1.txt')