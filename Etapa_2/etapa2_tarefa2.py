import os

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
            4: 'sp', 5: 'lv', 6: 'cpp',7: 'tos', 8: 'opc' 
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

    def log_estado_regs(self, log_file, titulo):
        """Escreve o estado de todos os registradores no arquivo de log."""
        log_file.write(f"{titulo}\n")
        ordem = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        for r in ordem:
            val = to_bin8(self.regs[r]) if r == 'mbr' else to_bin32(self.regs[r])
            log_file.write(f"{r} = {val}\n")

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

    def executar(self, prog_file, reg_file, log_out):
        self.carregar_registradores(reg_file)
        ciclo = 1

        with open(log_out, 'w') as log:
            log.write("=====================================================\n")
            self.log_estado_regs(log, "> Initial register states")
            log.write("\n=====================================================\nStart of program\n")
            
            if not os.path.exists(prog_file): return
            with open(prog_file, 'r') as file:
                for linha in file:
                    IR = linha.strip()
                    if len(IR) != 21: continue
                    
                    log.write("=====================================================\n")
                    log.write(f"Cycle {ciclo}\nir = {IR[0:8]} {IR[8:17]} {IR[17:21]}\n\n")
                    
                    # Decodificação barramentos
                    ctrl_ula, ctrl_c, ctrl_b = IR[0:8], IR[8:17], IR[17:21]
                    reg_b = self.map_b.get(int(ctrl_b, 2))
                    
                    # Lógica MBR (Sinal) vs MBRU (Zero) 
                    val_b = 0
                    if reg_b == 'mbr': # Extensão de SINAL
                        val_b = self.regs['mbr'] if not (self.regs['mbr'] & 0x80) else (self.regs['mbr'] | 0xFFFFFF00)
                    elif reg_b == 'mbru': # Extensão de ZEROS
                        val_b = self.regs['mbr'] & 0xFF
                    else: val_b = self.regs[reg_b]

                    log.write(f"b_bus = {reg_b}\n")
                    destinos = [self.map_c[i] for i, bit in enumerate(ctrl_c) if bit == '1']
                    log.write(f"c_bus = {', '.join(destinos)}\n\n")
                    
                    self.log_estado_regs(log, "> Registers before instruction")
                    
                    # Execução e Escrita
                    Sd = self.ula(self.regs['h'], val_b, ctrl_ula)
                    for d in destinos:
                        if d == 'mbr': self.regs[d] = Sd & 0xFF
                        else: self.regs[d] = Sd
                        
                    log.write("\n")
                    self.log_estado_regs(log, "> Registers after instruction")
                    ciclo += 1
                
                log.write("=====================================================\nNo more lines, EOP.\n")

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    Mic1Datapath().executar(os.path.join(base, 'programa_etapa2_tarefa2.txt'), 
                             os.path.join(base, 'registradores_etapa2_tarefa2.txt'), 
                             os.path.join(base, 'log_etapa2_tarefa2.txt'))