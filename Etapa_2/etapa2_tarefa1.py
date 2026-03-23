def to_bin32(val):
    return f"{val & 0xFFFFFFFF:032b}"

def ula_8bits(A, B, ir):
    sll8, sra1, f0, f1, ena, enb, inva, inc = [int(bit) for bit in ir]
    
    # Regra de erro do deslocador
    if sll8 == 1 and sra1 == 1:
        return None, None, None, None, None, None, None, True
        
    a_val = A if ena else 0
    b_val = B if enb else 0
    if inva:
        a_val = ~a_val & 0xFFFFFFFF
        
    carry_in = 1 if inc else 0
    vai_um = 0
    
    if f0 == 0 and f1 == 0: S = a_val & b_val
    elif f0 == 0 and f1 == 1: S = a_val | b_val
    elif f0 == 1 and f1 == 0: S = ~b_val & 0xFFFFFFFF
    elif f0 == 1 and f1 == 1:
        soma = a_val + b_val + carry_in
        S = soma & 0xFFFFFFFF
        vai_um = 1 if soma > 0xFFFFFFFF else 0
    else: S = 0
        
    Sd = S
    if sll8:
        Sd = (S << 8) & 0xFFFFFFFF
    elif sra1:
        sinal = S & 0x80000000
        Sd = (S >> 1) | sinal
        
    z = 1 if Sd == 0 else 0
    n = 1 if (Sd & 0x80000000) else 0
    
    return a_val, b_val, S, Sd, n, z, vai_um, False

def rodar_tarefa1():
    A = 0x00000001  # 1
    B = 0x80000000  # Bit mais significativo alto
    PC = 1
    
    with open('log_etapa2_tarefa1.txt', 'w') as log:
        log.write(f"b = {to_bin32(B)}\na = {to_bin32(A)}\n\nStart of Program\n")
    
        with open('programa_etapa2_tarefa1.txt', 'r') as arquivo:
            for linha in arquivo:
                IR = linha.strip()
                if not IR: continue
                
                log.write("============================================================\n")
                log.write(f"Cycle {PC}\n\nPC = {PC}\nIR = {IR}\n")
                
                a_v, b_v, S, Sd, n, z, co, erro = ula_8bits(A, B, IR)
                if erro:
                    log.write("> Error, invalid control signals.\n") 
                else:
                    log.write(f"b = {to_bin32(b_v)}\na = {to_bin32(a_v)}\ns = {to_bin32(S)}\n")
                    log.write(f"sd = {to_bin32(Sd)}\nn = {n}\nz = {z}\nco = {co}\n")
                PC += 1
                
                log.write("============================================================\n")
                log.write(f"Cycle {PC}\n\nPC = {PC}\n> Line is empty, EOP.\n") 


if __name__ == "__main__":
    rodar_tarefa1()