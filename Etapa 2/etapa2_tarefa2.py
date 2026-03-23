def to_bin32(val):
    return f"{val & 0xFFFFFFFF:032b}"

def to_bin8(val):
    return f"{val & 0xFF:08b}"

class Mic1Datapath:
    def __init__(self):
        # Inicializa todos os registradores
        self.regs = {
            'mar': 0, 'mdr': 0, 'pc': 0, 'mbr': 0, 'sp': 0, 
            'lv': 0, 'cpp': 0, 'tos': 0, 'opc': 0, 'h': 0
        }
        
        # Mapa do Decodificador (Barramento B)
        self.map_b = {
            0: 'mdr', 1: 'pc', 2: 'mbr', 3: 'mbru', 
            4: 'sp', 5: 'lv', 6: 'cpp', 7: 'opc', 8: 'tos'
        }
        
        # Mapa do Seletor (Barramento C) do bit 8 ao bit 0
        self.map_c = ['h', 'opc', 'tos', 'cpp', 'lv', 'sp', 'pc', 'mdr', 'mar']

    def carregar_registradores(self, arquivo):
        with open(arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: continue
                # Separa o nome do registrador e o valor binário
                reg, val = linha.split(" = ")
                self.regs[reg] = int(val, 2)

    def imprimir_regs(self, prefixo):
        print(prefixo)
        ordem_impressao = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        for r in ordem_impressao:
            if r == 'mbr':
                print(f"{r} = {to_bin8(self.regs[r])}") # MBR tem apenas 8 bits
            else:
                print(f"{r} = {to_bin32(self.regs[r])}") # Os demais têm 32 bits

    def ula(self, A, B, ctrl):
        sll8, sra1, f0, f1, ena, enb, inva, inc = [int(x) for x in ctrl]
        
        a_val = A if ena else 0
        b_val = B if enb else 0
        if inva: a_val = ~a_val & 0xFFFFFFFF
        carry_in = 1 if inc else 0
        
        if f0 == 0 and f1 == 0: S = a_val & b_val
        elif f0 == 0 and f1 == 1: S = a_val | b_val
        elif f0 == 1 and f1 == 0: S = ~b_val & 0xFFFFFFFF
        elif f0 == 1 and f1 == 1: S = (a_val + b_val + carry_in) & 0xFFFFFFFF
        else: S = 0
            
        Sd = S
        if sll8: Sd = (S << 8) & 0xFFFFFFFF
        elif sra1: 
            sinal = S & 0x80000000
            Sd = (S >> 1) | sinal
        return Sd

    def executar(self, prog_file, reg_file):
        try:
            self.carregar_registradores(reg_file)
        except FileNotFoundError:
            print(f"Erro: Arquivo '{reg_file}' não encontrado.")
            return

        print("=====================================================")
        self.imprimir_regs("> Initial register states")
        print()
        print("=====================================================")
        print("Start of program")
        print("=====================================================")
        
        ciclo = 1
        try:
            with open(prog_file, 'r') as file:
                for linha in file:
                    IR = linha.strip()
                    if len(IR) != 21: continue # Pula linhas inválidas
                    
                    print(f"Cycle {ciclo}")
                    print(f"ir = {IR[0:8]} {IR[8:17]} {IR[17:21]}\n")
                    
                    ctrl_ula = IR[0:8]
                    ctrl_c = IR[8:17]
                    ctrl_b = IR[17:21]
                    
                    # 1. Definindo a entrada do Barramento B
                    idx_b = int(ctrl_b, 2)
                    reg_b = self.map_b.get(idx_b, None)
                    print(f"b_bus = {reg_b}")
                    
                    B_val = 0
                    if reg_b == 'mbr':
                        # Extensão de Zeros: preenche com 0 até 32 bits
                        B_val = self.regs['mbr']
                    elif reg_b == 'mbru':
                        # Extensão de Sinal: replica o bit mais alto até 32 bits
                        if self.regs['mbr'] & 0x80:
                            B_val = self.regs['mbr'] | 0xFFFFFF00
                        else:
                            B_val = self.regs['mbr']
                    elif reg_b is not None:
                        B_val = self.regs[reg_b]
                    
                    # 2. Definindo os destinos no Barramento C
                    escritos = []
                    for i, bit in enumerate(ctrl_c):
                        if bit == '1':
                            escritos.append(self.map_c[i])
                    
                    print(f"c_bus = {', '.join(escritos)}\n")
                    
                    self.imprimir_regs("> Registers before instruction")
                    print()
                    
                    # 3. Execução na ULA
                    A_val = self.regs['h']
                    Sd = self.ula(A_val, B_val, ctrl_ula)
                    
                    # 4. Escrita nos registradores
                    for destino in escritos:
                        if destino == 'mbr':
                            self.regs[destino] = Sd & 0xFF
                        else:
                            self.regs[destino] = Sd
                            
                    self.imprimir_regs("> Registers after instruction")
                    print("=====================================================")
                    ciclo += 1
                    
            print(f"Cycle {ciclo - 1}")
            print("No more lines, EOP.")
            
        except FileNotFoundError:
            print(f"Erro: Arquivo '{prog_file}' não encontrado.")

if __name__ == "__main__":
    maquina = Mic1Datapath()
    # Chama a execução passando os dois arquivos de texto necessários
    maquina.executar('programa_etapa2_tarefa2.txt', 'registradores_etapa2_tarefa2.txt')