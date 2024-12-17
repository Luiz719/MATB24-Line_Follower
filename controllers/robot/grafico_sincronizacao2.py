import pandas as pd
import matplotlib.pyplot as plt
import os
print(f"Diretório atual: {os.getcwd()}")
print(f"Arquivos disponíveis: {os.listdir(os.getcwd())}")


# Função para ler dados de um arquivo CSV
def ler_dados_csv(arquivo):
    try:
        dados = pd.read_csv(arquivo)
        return dados
    except Exception as e:
        print(f"Erro ao ler o arquivo {arquivo}: {e}")
        return None

# Função para plotar o gráfico
def plotar_grafico(dados1, dados2):
    try:
        plt.figure(figsize=(10, 6))

        # Plotar os dados do primeiro arquivo
        plt.plot(dados1['timestamp_inicio'], dados1['tempo_retorno'], label='PID', marker='o')

        # Plotar os dados do segundo arquivo
        plt.plot(dados2['timestamp_inicio'], dados2['tempo_retorno'], label='PD', marker='x')

        # Configurações do gráfico
        plt.title('Tempo X Tempo de Sincronização', fontsize=14)
        plt.xlabel('Tempo (s)', fontsize=12)
        plt.ylabel('Tempo de Sincronização (s)', fontsize=12)
        plt.legend()
        plt.grid(True)

        # Mostrar o gráfico
        plt.show()
    except Exception as e:
        print(f"Erro ao plotar o gráfico: {e}")

# Caminhos dos arquivos CSV
arquivo1 = 'tempo_retorno_erro.csv'
arquivo2 = 'tempo_retorno_erro_pd.csv'

# Ler os dados dos arquivos
dados1 = ler_dados_csv(arquivo1)
dados2 = ler_dados_csv(arquivo2)

# Verificar se os dados foram lidos corretamente antes de gerar o gráfico
if dados1 is not None and dados2 is not None:
    plotar_grafico(dados1, dados2)
