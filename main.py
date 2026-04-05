import os
import sys

# Importa as funções e classes dos seus arquivos
from Etapa_1.etapa1 import rodar_etapa1
from Etapa_2.etapa2_tarefa1 import rodar_tarefa1
from Etapa_2.etapa2_tarefa2 import Mic1Datapath
from Etapa_3.etapa3_tarefa1 import Mic1Datapath as Mic1Tarefa1
from Etapa_3.etapa3_tarefa2 import compilar_ijvm, Mic1Datapath as Mic1Tarefa2

def executar_projeto():
    # Descobre o caminho base de onde a main.py está sendo executada
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Iniciando Simulador Mic-1 (UFPB) ===")

    # Cria a pasta de saídas se não existir
    pasta_saidas = os.path.join(base_dir, 'saidas')
    os.makedirs(pasta_saidas, exist_ok=True)

    # --- EXECUÇÃO ETAPA 1 ---
    print("\n[Executando Etapa 1]...")
    e1_in = os.path.join(base_dir, 'Etapa_1', 'programa_etapa1.txt')
    e1_out = os.path.join(pasta_saidas, 'log_etapa1.txt')
    try:
        rodar_etapa1(e1_in, e1_out)
        print(f"OK: Log gerado em saidas/log_etapa1.txt")
    except Exception as e:
        print(f"Erro na Etapa 1: {e}")

    # --- EXECUÇÃO ETAPA 2.1 ---
    print("\n[Executando Etapa 2.1 - ULA]...")
    e21_in = os.path.join(base_dir, 'Etapa_2', 'programa_etapa2_tarefa1.txt')
    e21_out = os.path.join(pasta_saidas, 'log_etapa2_tarefa1.txt')

    try:
        rodar_tarefa1(e21_in, e21_out) 
        print(f"OK: Log gerado em saidas/log_etapa2_tarefa1.txt")
    except Exception as e:
        print(f"Erro na Etapa 2.1: {e}")

    # --- EXECUÇÃO ETAPA 2.2 ---
    print("\n[Executando Etapa 2.2 - Datapath]...")
    e2_prog = os.path.join(base_dir, 'Etapa_2', 'programa_etapa2_tarefa2.txt')
    e2_regs = os.path.join(base_dir, 'Etapa_2', 'registradores_etapa2_tarefa2.txt')
    e2_log = os.path.join(pasta_saidas, 'log_etapa2_tarefa2.txt')
    
    try:
        maquina = Mic1Datapath()
        maquina.executar(e2_prog, e2_regs, e2_log)
        print(f"OK: Log gerado em saidas/log_etapa2_tarefa2.txt")
    except Exception as e:
        print(f"Erro na Etapa 2.2: {e}")

    # --- EXECUÇÃO ETAPA 3.1 ---
    print("\n[Executando Etapa 3.1 - Microinstruções]...")
    e31_micro = os.path.join(base_dir, 'Etapa_3', 'microinstrucoes_etapa3_tarefa1.txt')
    e31_regs = os.path.join(base_dir, 'Etapa_3', 'registradores_etapa3_tarefa1.txt')
    e31_mem = os.path.join(base_dir, 'Etapa_3', 'dados_etapa3_tarefa1.txt')
    e31_log = os.path.join(pasta_saidas, 'log_etapa3_tarefa1.txt')

    try:
        maquina31 = Mic1Tarefa1()
        maquina31.executar(e31_micro, e31_regs, e31_mem, e31_log)
        print(f"OK: Log gerado em saidas/log_etapa3_tarefa1.txt")
    except Exception as e:
        print(f"Erro na Etapa 3.1: {e}")

    # --- EXECUÇÃO ETAPA 3.2 ---
    print("\n[Executando Etapa 3.2 - IJVM]...")
    e32_ijvm = os.path.join(base_dir, 'Etapa_3', 'instrucoes_etapa3_tarefa2.txt')
    e32_micro = os.path.join(pasta_saidas, 'microinstrucoes_etapa3_tarefa2.txt')
    e32_regs = os.path.join(base_dir, 'Etapa_3', 'registradores_etapa3_tarefa2.txt')
    e32_mem = os.path.join(base_dir, 'Etapa_3', 'dados_etapa3_tarefa2.txt')
    e32_log = os.path.join(pasta_saidas, 'log_etapa3_tarefa2.txt')

    try:
        compilar_ijvm(e32_ijvm, e32_micro)
        maquina32 = Mic1Tarefa2()
        maquina32.executar(e32_micro, e32_regs, e32_mem, e32_log)
        print(f"OK: Log gerado em saidas/log_etapa3_tarefa2.txt")
    except Exception as e:
        print(f"Erro na Etapa 3.2: {e}")

    print("\n=== Simulação Finalizada com Sucesso ===")

if __name__ == "__main__":
    executar_projeto()