import pandas as pd
import matplotlib.pyplot as plt

# Função para gerar gráficos
def gerar_graficos(arquivos_csv):
    # Gráfico 1: Tempo X Erro Absoluto
    plt.figure(figsize=(10, 5))
    for arquivo in arquivos_csv:
        dados = pd.read_csv(arquivo)
        nome_controle = arquivo.split('_')[1].split('.')[0]  # Extrai PD ou PID do nome do arquivo
        plt.plot(dados['timestamp'], abs(dados['erro']), 
                 label=f'Controle {nome_controle} Kp = 80 Ki = 0.1 Kd = 2')
        
    plt.title('Tempo X Erro Absoluto')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Erro Absoluto')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Gráfico 2: Tempo X Tempo de Sincronização
    plt.figure(figsize=(10, 5))
    for arquivo in arquivos_csv:
        dados = pd.read_csv(arquivo)
        nome_controle = arquivo.split('_')[1].split('.')[0]  # Extrai PD ou PID
        sincronizacao = dados[dados['erro'] == 0]  # Filtra onde erro == 0
        if not sincronizacao.empty:
            plt.plot(sincronizacao['timestamp'], sincronizacao['timestamp'], 'o', label=f'Controle {nome_controle} Kp = 80 Ki = 0.1 Kd = 2')
        else:
            print(f"Controle {nome_controle} não sincronizou (erro zero não encontrado).")


    plt.title('Tempo X Tempo de Sincronização')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Tempo de Sincronização (s)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Lista de arquivos CSV
arquivos_csv = ['controle_PID.csv']
gerar_graficos(arquivos_csv)
