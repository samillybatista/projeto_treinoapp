from projeto_treinoapp.DataAnalysis.DataLoader import DataLoader
import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import plotly.express as px
import re

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Caminho para o arquivo JSON fornecido
file_path = '../Data/bioData.json'

data_loader = DataLoader(file_path)
json_data = data_loader.load_json_data()
df = data_loader.extract_data()

# Remover o dia da semana do campo 'start_time' e converter para datetime
df['start_time'] = df['start_time'].apply(
    lambda x: re.match(r'\d{2}/\d{2}', x).group(0) + '/2024')
df['start_time'] = pd.to_datetime(df['start_time'], format='%d/%m/%Y')

# Ajustar o tamanho dos pontos e formatar as datas no hover
df['Data'] = df['start_time'].dt.strftime('%d/%m/%Y')

# Finalmente, podemos criar um gráfico de dispersão para mostrar a relação entre frequência cardíaca média e calorias
heart_rate_data = [entry["heart_rate"]["average"] for entry in json_data]

# Adicionar essa informação ao DataFrame
df['heart_rate_avg'] = heart_rate_data

# Selecionar as colunas para o clustering
X = df[['heart_rate_avg', 'calories']]

# Aplicar K-means com 3 clusters (ou mais, dependendo da sua necessidade)
kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
df['cluster'] = kmeans.labels_

# Calcular a média de frequência cardíaca e calorias por cluster
cluster_means = df.groupby('cluster')[['heart_rate_avg', 'calories']].mean()

# Ordenar os clusters por calorias e atribuir rótulos baseados nas médias
sorted_clusters = cluster_means.sort_values(by='calories')

# Criar um dicionário de mapeamento para os rótulos de intensidade
cluster_labels = {sorted_clusters.index[0]: 'Baixa Intensidade',
                  sorted_clusters.index[1]: 'Intensidade Moderada',
                  sorted_clusters.index[2]: 'Alta Intensidade'}


# Atribuir os rótulos categorizados aos clusters no DataFrame
df['cluster_category'] = df['cluster'].map(cluster_labels)

# Definir cores para cada categoria de cluster
color_map = {
    'Baixa Intensidade': 'green',
    'Intensidade Moderada': 'blue',
    'Alta Intensidade': 'red'
}

# Criar gráfico de dispersão interativo com Plotly, usando os clusters categorizados

fig = px.scatter(df, x='duration', y='heart_rate_avg', color='cluster_category',
                 color_discrete_map=color_map, hover_data={'Data': True},
                 labels={
                     'heart_rate_avg': 'Frequência Cardíaca Média (bpm)',
                     'calories': 'Calorias Queimadas',
                     'cluster_category': 'Intensidade do Treino'
                 },
                 title='Relação entre Frequência Cardíaca Média e Calorias Queimadas com Agrupamento',
                 # Ordem personalizada das legendas
                 category_orders={"cluster_ca   tegory": [
                     "Alta Intensidade", "Intensidade Moderada", "Baixa Intensidade"]}
                 )

# Aumentar o tamanho dos pontos para melhorar a visualização
fig.update_traces(marker=dict(size=14))
fig.write_html("../html/Plot_Frequencia_Calorias.html")

# Exibir o gráfico interativo
# fig.show()
