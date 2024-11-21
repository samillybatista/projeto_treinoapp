import json
import pandas as pd
import matplotlib.pyplot as plt

from DataAnalysis.DataLoader import DataLoader

# Caminho para o arquivo JSON fornecido
file_path = '../Data/bioData.json'

data_loader = DataLoader(file_path)
json_data = data_loader.load_json_data()
df = data_loader.extract_data()


# Primeiro, criaremos um gráfico de linha para mostrar a progressão de calorias queimadas ao longo das sessões
# Gráfico de calorias queimadas ao longo das sessões com datas no eixo X
plt.figure(figsize=(10, 6))
plt.plot(df['start_time'], df['calories'], marker='o', linestyle='-', color='orange')
plt.title('Progressão de Calorias Queimadas ao Longo das Sessões')
plt.xlabel('Data (dd/MM)')
plt.ylabel('Calorias Queimadas')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()