import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from DataAnalysis.DataLoader import DataLoader

# Caminho para o arquivo JSON fornecido
file_path = '../Data/exercise.json'

data_loader = DataLoader(file_path)
json_data = data_loader.load_json_data()
df = data_loader.extract_data()

# Vamos adicionar algumas análises estatísticas com base nos dados extraídos
# Estatísticas básicas de calorias e duração

# Estatísticas descritivas
calories_stats = df['calories'].describe()
duration_stats = df['duration'].describe()

# Relação entre calorias e duração (coeficiente de correlação)
correlation = df['calories'].corr(df['duration'])

# Exibir as estatísticas descritivas
print("Estatísticas Descritivas - Calorias")
print(calories_stats)
print("\nEstatísticas Descritivas - Duração")
print(duration_stats)
print(f"\nCorrelação entre Calorias Queimadas e Duração: {correlation:.2f}")

# Plotando um histograma de calorias queimadas
# Dados de calorias
calories = df['calories']

# Plotar histograma das calorias
plt.figure(figsize=(10, 6))
count, bins, ignored = plt.hist(calories, bins=10, density=True, alpha=0.6, color='blue', edgecolor='black')

# Calcular média e desvio padrão
mu, std = np.mean(calories), np.std(calories)

# Plotar a curva gaussiana (normal)
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = stats.norm.pdf(x, mu, std)

# Adicionar a curva gaussiana ao gráfico
plt.plot(x, p, 'k', linewidth=2)
title = "Distribuição de Calorias Queimadas com Curva Gaussiana"
plt.title(title)
plt.xlabel('Calorias Queimadas')
plt.ylabel('Densidade de Probabilidade')
plt.grid(True)

# Mostrar o gráfico
plt.show()