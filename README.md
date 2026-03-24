# 🖥️ Simulador Mic-1 — UFPB

Simulador da microarquitetura **Mic-1** em Python, desenvolvido para a disciplina de **Arquitetura de Computadores** da UFPB.

## 📁 Estrutura

```
├── main.py                              # Ponto de entrada
├── Etapa_1/
│   ├── etapa1.py                        # ULA de 6 bits
│   └── programa_etapa1.txt              # Instruções de entrada
├── Etapa_2/
│   ├── etapa2_tarefa1.py                # ULA de 8 bits (com deslocador)
│   ├── etapa2_tarefa2.py                # Datapath completo do Mic-1
│   ├── programa_etapa2_tarefa1.txt
│   ├── programa_etapa2_tarefa2.txt
│   └── registradores_etapa2_tarefa2.txt
└── saidas/                              # Logs gerados pela execução
```

## ⚙️ Etapas

| Etapa | Descrição |
|-------|-----------|
| **1** | ULA de 6 bits — operações AND, OR, NOT, soma com controle de ENA/ENB/INVA/INC |
| **2.1** | ULA de 8 bits — adiciona deslocador (SLL8, SRA1) e flags N/Z |
| **2.2** | Datapath completo — 10 registradores, barramentos B (4 bits) e C (9 bits), instruções de 21 bits |

## 🚀 Como Executar

```bash
python main.py
```

Os logs de cada etapa são gerados na pasta `saidas/`.

## 📚 Referência

> **Andrew S. Tanenbaum** — *Organização Estruturada de Computadores*, 6ª edição.
