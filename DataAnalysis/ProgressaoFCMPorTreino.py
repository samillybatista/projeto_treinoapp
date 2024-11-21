import json
import pandas as pd
import matplotlib.pyplot as plt

from DataAnalysis.DataLoader import DataLoader


file_path = '../Data/bioData.json'

data_loader = DataLoader(file_path)
json_data = data_loader.load_json_data()
df = data_loader.extract_data()

# Finalmente, podemos criar um gráfico de dispersão para mostrar a relação entre frequência cardíaca média e calorias
heart_rate_data = [entry["heart_rate"]["average"] for entry in json_data]

# Adicionar essa informação ao DataFrame
df['heart_rate_avg'] = heart_rate_data

# Primeiro, criaremos um gráfico de linha para mostrar a progressão de calorias queimadas ao longo das sessões
# Gráfico de Frequencia Cardiaca Média ao longo das sessões com datas no eixo X
plt.figure(figsize=(10, 6))
plt.plot(df['start_time'], df['heart_rate_avg'], marker='o', linestyle='-', color='orange')
plt.title('Progressão de Frequencia Cardiaca Média ao Longo das Sessões')
plt.xlabel('Data (dd/MM)')
plt.ylabel('Heart Rate (Avg)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()