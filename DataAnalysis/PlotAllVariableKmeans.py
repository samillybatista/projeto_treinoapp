import plotly.express as px
import pandas as pd
import re
from sklearn.cluster import KMeans
from DataAnalysis.DataLoader import DataLoader

# Caminho para o arquivo JSON fornecido
file_path = '../Data/exercise.json'

# Exemplo de como carregar os dados (usando sua classe DataLoader)
data_loader = DataLoader(file_path)
json_data = data_loader.load_json_data()
df = data_loader.extract_data()

# Adicionar os dados de frequência cardíaca média
heart_rate_data = [entry["heart_rate"]["average"] for entry in json_data]
df['heart_rate_avg'] = heart_rate_data

# Remover o dia da semana do campo 'start_time' e converter para datetime
df['start_time'] = df['start_time'].apply(lambda x: re.match(r'\d{2}/\d{2}', x).group(0) + '/2024')
df['start_time'] = pd.to_datetime(df['start_time'], format='%d/%m/%Y')

# Ajustar o tamanho dos pontos e formatar as datas no hover
df['Data'] = df['start_time'].dt.strftime('%d/%m/%Y')

# Selecionar as colunas para o clustering (K-means) incluindo calorias, duração e frequência cardíaca média
X = df[['calories', 'duration', 'heart_rate_avg']]

# Aplicar K-means com 3 clusters
kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
df['cluster'] = kmeans.labels_

# Calcular a média de calorias, duração e frequência cardíaca por cluster (ordenar os clusters por média de calorias)
cluster_means = df.groupby('cluster')[['calories', 'duration', 'heart_rate_avg']].mean()

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

# Criar gráfico de dispersão 3D interativo usando Plotly, com clusters categorizados
fig = px.scatter(df, x='duration', y='calories', color='cluster_category',color_discrete_map=color_map,
                    hover_data={'heart_rate_avg': True,'Data':True}, labels={
                        'duration': 'Duração do Treino (segundos)',
                        'calories': 'Calorias Queimadas',
                        'heart_rate_avg': 'Frequência Cardíaca Média (bpm)',
                        'cluster_category': 'Categoria de Intensidade',
                        'Data':'Dia'
                    },
                    title='Relação entre Duração do Treino, Calorias Queimadas e Frequência Cardíaca com K-means Clustering',
                   size='heart_rate_avg',  # Tamanho dos pontos em função da Frequência Cardíaca Média,
                   size_max = 40  # Aumentar o tamanho máximo dos pontos para maior visibilidade


)
# Aumentar o tamanho máximo e mínimo dos pontos, ajustando a referência
fig.update_traces(marker=dict(sizeref=2., sizemin=10))
# Aumentar o tamanho dos pontos
#fig.update_traces(marker=dict(size=16))
fig.write_html("../html/Plot_Duracao_Calorias_Frequencia.html")

# Exibir o gráfico interativo 3D
fig.show()
