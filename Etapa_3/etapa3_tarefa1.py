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
        self.memoria = {} # Memória de dados
        
        # Mapa do Decodificador (Barramento B)
        self.map_b = {
            0: 'mdr', 1: 'pc', 2: 'mbr', 3: 'mbru',
            4: 'sp', 5: 'lv', 6: 'cpp',7: 'tos', 8: 'opc'
        }
        # Mapa do Seletor (Barramento C) do bit 8 ao bit 0
        self.map_c = ['h', 'opc', 'tos', 'cpp', 'lv', 'sp', 'pc', 'mdr', 'mar']

    def carregar_registradores(self, arquivo):
        if not os.path.exists(arquivo): return
        with open(arquivo, 'r') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: continue
                # Separa o nome do registrador e o valor binário
                reg, val = linha.split(" = ")
                self.regs[reg] = int(val, 2)

    def carregar_memoria(self, arquivo):
        self.memoria = {}
        if not os.path.exists(arquivo): return
        with open(arquivo, 'r') as f:
            for ender, linha in enumerate(f):
                if linha.strip():
                    self.memoria[ender] = int(linha.strip(), 2)

    def log_estado_regs(self, log_file, titulo):
        """Escreve o estado de todos os registradores no arquivo de log."""
        log_file.write(f"{titulo}\n")
        ordem = ['mar', 'mdr', 'pc', 'mbr', 'sp', 'lv', 'cpp', 'tos', 'opc', 'h']
        for r in ordem:
            val = to_bin8(self.regs[r]) if r == 'mbr' else to_bin32(self.regs[r])
            log_file.write(f"{r} = {val}\n")

    def log_estado_memoria(self, log_file, titulo):
        log_file.write(f"{titulo}\n")
        if not self.memoria:
            log_file.write("(Memoria vazia)\n")
        for end in sorted(self.memoria.keys()):
            log_file.write(f"[{end:02d}] = {to_bin32(self.memoria[end])}\n")

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

    def executar(self, micro_file, reg_file, mem_file, log_out):
        self.carregar_registradores(reg_file)
        self.carregar_memoria(mem_file)
        ciclo = 1

        with open(log_out, 'w') as log:
            log.write("=====================================================\n")
            self.log_estado_memoria(log, "> Initial Data Memory")
            log.write("\n")
            self.log_estado_regs(log, "> Initial register states")
            log.write("\n=====================================================\nStart of program\n")
            
            if not os.path.exists(micro_file): return
            with open(micro_file, 'r') as file:
                for linha in file:
                    IR = linha.strip()
                    if len(IR) != 23: continue
                    
                    log.write("=====================================================\n")
                    log.write(f"Cycle {ciclo}\nir = {IR[0:8]} {IR[8:17]} {IR[17:19]} {IR[19:23]}\n\n")
                    
                    # Decodificação (23 bits)
                    ctrl_ula, ctrl_c, ctrl_mem, ctrl_b = IR[0:8], IR[8:17], IR[17:19], IR[19:23]
                    
                    
                    # CASO ESPECIAL: FETCH do BIPUSH (WRITE=1 e READ=1)
                    if ctrl_mem == '11':
                        val_byte = int(ctrl_ula, 2)
                        log.write("b_bus = (N/A - FETCH INSTRUCTION)\n")
                        log.write("c_bus = (N/A)\n\n")
                        
                        self.log_estado_regs(log, "> Registers before instruction")
                        
                        # MBR recebe os 8 bits, H recebe MBR preenchido com zeros
                        self.regs['mbr'] = val_byte
                        self.regs['h'] = val_byte
                        
                        log.write("\n")
                        self.log_estado_regs(log, "> Registers after instruction")
                        log.write("\n")
                        self.log_estado_memoria(log, "> Data Memory after instruction")
                        ciclo += 1
                        continue

                    
                    # FLUXO NORMAL DE EXECUÇÃO
                    reg_b = self.map_b.get(int(ctrl_b, 2))
                    
                    val_b = 0
                    if reg_b == 'mbr': # Extensão de SINAL
                        val_b = self.regs['mbr'] if not (self.regs['mbr'] & 0x80) else (self.regs['mbr'] | 0xFFFFFF00)
                    elif reg_b == 'mbru': # Extensão de ZEROS
                        val_b = self.regs['mbr'] & 0xFF
                    else: val_b = self.regs[reg_b]

                    log.write(f"b_bus = {reg_b}\n")
                    destinos = [self.map_c[i] for i, bit in enumerate(ctrl_c) if bit == '1']
                    log.write(f"c_bus = {', '.join(destinos) if destinos else 'None'}\n\n")
                    
                    self.log_estado_regs(log, "> Registers before instruction")
                    
                    # 1. Execução e escrita no Barramento C
                    Sd = self.ula(self.regs['h'], val_b, ctrl_ula)
                    for d in destinos:
                        if d == 'mbr': self.regs[d] = Sd & 0xFF
                        else: self.regs[d] = Sd
                    
                    # 2. Acesso à Memória (Após escrita do Barramento C)
                    if ctrl_mem == '10': # WRITE
                        self.memoria[self.regs['mar']] = self.regs['mdr']
                    elif ctrl_mem == '01': # READ
                        self.regs['mdr'] = self.memoria.get(self.regs['mar'], 0)
                        
                    log.write("\n")
                    self.log_estado_regs(log, "> Registers after instruction")
                    log.write("\n")
                    self.log_estado_memoria(log, "> Data Memory after instruction")
                    ciclo += 1
                
                log.write("=====================================================\nNo more lines, EOP.\n")

if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    
    arq_micro = os.path.join(base, 'microinstrucoes_etapa3_tarefa1.txt')
    arq_regs = os.path.join(base, 'registradores_etapa3_tarefa1.txt')
    arq_mem = os.path.join(base, 'dados_etapa3_tarefa1.txt')
    arq_log = os.path.join(base, 'log_etapa3_tarefa1.txt')
    
    Mic1Datapath().executar(arq_micro, arq_regs, arq_mem, arq_log)
    print(f"Execução da Tarefa 1 finalizada! Verifique o arquivo: {os.path.basename(arq_log)}")