import os

def to_bin32(val):
    return f"{val & 0xFFFFFFFF:032b}"

class Mic1:
    def __init__(self):
        # Registradores de 32 bits [cite: 95]
        self.regs = {
            'MAR': 0, 'MDR': 0, 'PC': 0, 'SP': 0,
            'LV': 0, 'CPP': 0, 'TOS': 0, 'OPC': 0, 'H': 0
        }
        self.MBR = 0  # 8 bits [cite: 96]
        self.memoria_dados = [0] * 8  # 8 endereços conforme o enunciado [cite: 150]

    def carregar_registradores(self, path):
        if not os.path.exists(path): return
        with open(path, 'r') as f:
            for linha in f:
                if '=' in linha:
                    reg, val = linha.split('=')
                    reg = reg.strip().upper()
                    val_int = int(val.strip(), 2)
                    if reg == 'MBR': self.MBR = val_int
                    else: self.regs[reg] = val_int

    def carregar_memoria(self, path):
        if not os.path.exists(path): return
        with open(path, 'r') as f:
            self.memoria_dados = [int(linha.strip(), 2) for linha in f if linha.strip()]

    def ula_completa(self, A, B, controle_ula):
        # Desempacota os 8 bits de controle da ULA [cite: 82]
        sll8, sra1, f0, f1, ena, enb, inva, inc = [int(b) for b in controle_ula]
        
        a_val = A if ena else 0
        b_val = B if enb else 0
        if inva: a_val = ~a_val & 0xFFFFFFFF
            
        carry_in = 1 if inc else 0
        S = 0
        vai_um = 0
        
        # Lógica da Unidade Lógica [cite: 21]
        if f0 == 0 and f1 == 0: S = a_val & b_val
        elif f0 == 0 and f1 == 1: S = a_val | b_val
        elif f0 == 1 and f1 == 0: S = ~b_val & 0xFFFFFFFF
        elif f0 == 1 and f1 == 1:
            soma = a_val + b_val + carry_in
            S = soma & 0xFFFFFFFF
            vai_um = 1 if soma > 0xFFFFFFFF else 0

        # Deslocador [cite: 90, 91]
        Sd = S
        if sll8: Sd = (S << 8) & 0xFFFFFFFF
        elif sra1: Sd = (S >> 1) | (S & 0x80000000) # Aritmético

        return Sd

    def executar_microinstrucao(self, micro_bitstr):
        # 1. Decodificação da palavra de 23 bits [cite: 147]
        ctrl_ula = micro_bitstr[0:8]
        ctrl_c   = micro_bitstr[8:17]
        ctrl_mem = micro_bitstr[17:19]
        ctrl_b   = micro_bitstr[19:23]

        # Caso Especial: FETCH (BIPUSH) [cite: 225, 228, 230]
        if ctrl_mem == "11":
            argumento_8bits = int(ctrl_ula, 2)
            self.MBR = argumento_8bits
            self.regs['H'] = self.MBR # H = MBR sem passar pela ULA [cite: 230]
            return "MBR", ["H"]

        # 2. Barramento B (Decodificador 4 bits) [cite: 101]
        map_b = {
            0:'MDR', 1:'PC', 2:'MBR', 3:'MBRU', 4:'SP', 
            5:'LV', 6:'CPP', 7:'TOS', 8:'OPC'
        }
        reg_b_nome = map_b.get(int(ctrl_b, 2), 'NONE')
        val_b = 0
        if reg_b_nome == 'MBRU':
            val_b = self.MBR & 0xFF
        elif reg_b_nome == 'MBR':
            # Extensão de sinal [cite: 103]
            val_b = self.MBR if not (self.MBR & 0x80) else (self.MBR | 0xFFFFFF00)
        elif reg_b_nome in self.regs:
            val_b = self.regs[reg_b_nome]

        # 3. Execução ULA
        Sd = self.ula_completa(self.regs['H'], val_b, ctrl_ula)

        # 4. Barramento C (Escrita nos registradores) [cite: 107, 114]
        regs_c = ['MAR', 'MDR', 'PC', 'SP', 'LV', 'CPP', 'TOS', 'OPC', 'H']
        escritos = []
        for i, bit in enumerate(reversed(ctrl_c)):
            if bit == '1':
                reg_nome = regs_c[i]
                self.regs[reg_nome] = Sd
                escritos.append(reg_nome)

        # 5. Operações de Memória [cite: 154, 155, 156]
        # Ocorrem APÓS a escrita no Barramento C
        if ctrl_mem == "01": # READ
            if 0 <= self.regs['MAR'] < len(self.memoria_dados):
                self.regs['MDR'] = self.memoria_dados[self.regs['MAR']]
        elif ctrl_mem == "10": # WRITE
            if 0 <= self.regs['MAR'] < len(self.memoria_dados):
                self.memoria_dados[self.regs['MAR']] = self.regs['MDR']

        return reg_b_nome, escritos

def traduzir_ijvm(linha_ijvm):
    # Simula o tradutor para o Entregável [cite: 237]
    partes = linha_ijvm.split()
    cmd = partes[0].upper()
    
    if cmd == "BIPUSH": # [cite: 221, 222, 226]
        arg = partes[1] # ex: 00110011
        return [
            "00110101000001000000100", # SP=MAR=SP+1
            f"{arg}00000000000110000",  # FETCH ESPECIAL (H=MBR)
            "00111100000000110000000"  # MDR=TOS=H; wr
        ]
    elif cmd == "DUP": # [cite: 213, 214]
        return [
            "00110101000001000000100", # MAR=SP=SP+1
            "00111100000000010100111"  # MDR=TOS; wr (B=TOS)
        ]
    # ... Adicionar ILOAD conforme a lógica de incrementar H 'x' vezes [cite: 211]
    return []

# Bloco principal de execução e log conforme Etapa 3 [cite: 170, 245]