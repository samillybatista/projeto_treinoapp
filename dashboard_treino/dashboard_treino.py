import os
import re
import sys
import json
import subprocess
import pandas as pd  # type: ignore
import seaborn as sns  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import streamlit as st  # type: ignore
import calendar
from datetime import datetime
import plotly.express as px  # type: ignore
from sklearn.cluster import KMeans

from DataAnalysis.DataLoader import DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from requisicaoDados import PolarAccessLinkExample
from polarAccessLinkAdapter import PolarAccessLinkAdapter


st.set_page_config(layout="wide")

page_bg_img = """
<style>
.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.ekr3hml0 {
    background-color: rgb(32, 32, 32) !important;
}
.section.stSidebar.st-emotion-cache-1wqrzgl.e1dbuyne0 {
    max-width: 250px;
    background-color: rgb(27, 27, 29) !important;
}
.st-emotion-cache-1wqrzgl {
    background-color: rgb(27, 27, 29) !important;
}
.st-emotion-cache-6qob1r.e1dbuyne8 {
    max-width: 250px;  
    background-color: rgb(27, 27, 29) !important;
}
.st-emotion-cache-yw8pof {
    padding: 0px 0px 0px 0px;
    max-width: 1200.800px;
}

.st-emotion-cache-14553y9.e121c1cl0 {
    font-size: 22px;
}

.st-emotion-cache-h4xjwg  {
    height: 0px;
}

header.stAppHeader.st-emotion-cache-h4xjwg.e10jh26i0 {
    background-color: rgb(32, 32, 32) !important;
}
</style>
"""


st.markdown(page_bg_img, unsafe_allow_html=True)


# Função para carregar os dados de bio do atleta
def load_bio_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bio_data_path = os.path.join(script_dir, "../Data/bioData.json")
    with open(bio_data_path, "r") as file:
        return json.load(file)


# Função para converter a duração no formato ISO 8601 para minutos
def convert_duration(duration_str):
    duration = pd.to_timedelta(duration_str)
    return duration.total_seconds() / 60


def somar_calorias_perdidas(bio_data: dict) -> int:
    calorias_perdidas = 0
    if isinstance(bio_data, dict):
        for key, value in bio_data.items():
            if key == "calories":
                calorias_perdidas += value
            elif isinstance(value, (dict, list)):
                calorias_perdidas += somar_calorias_perdidas(value)
    elif isinstance(bio_data, list):
        for item in bio_data:
            calorias_perdidas += somar_calorias_perdidas(item)
    return calorias_perdidas


# Função para carregar dados do set.json
def load_set_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    treino_data_path = os.path.join(script_dir, "../Data/set.json")
    with open(treino_data_path, "r", encoding='utf-8') as file:
        return json.load(file)


# Função para carregar os dados de treino
@st.cache_data
def load_treino_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    treino_data_path = os.path.join(script_dir, "../Data/set.json")
    with open(treino_data_path, "r") as file:
        data = json.load(file)
        treino_list = []
        for date, details in data["schedule"].items():
            treino_list.append({
                "Data": date,
                "Tipo": details.get("type", ""),
                "Exercícios": [
                    {"Categoria": ex["category"], "Sets": ex["sets"]}
                    for ex in details.get("exercises", [])
                ]
            })
        rows = []
        for treino in treino_list:
            for ex in treino["Exercícios"]:
                for set_item in ex["Sets"]:
                    rows.append({
                        "Data": treino["Data"],
                        "Tipo": treino["Tipo"],
                        "Categoria": ex["Categoria"],
                        "Exercício": set_item
                    })
        treino_data = pd.DataFrame(rows)
    return treino_data


# Executa o script requisicaoDados.py e captura a saída
def obter_dados_treino():
    try:
        result = subprocess.run(
            ["python", "requisicaoDados.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Captura a saída JSON do script (se existir)
        output = result.stdout.strip()
        return json.loads(output) if output else {}
    except Exception as e:
        st.error(f"Erro ao obter os dados do treino: {e}")
        return {}


# Carrega os dados
bio_data_full = load_bio_data()
bio_data = bio_data_full[0]
treino_data = load_treino_data()
set_data = load_set_data()

# Garante que "Data" seja datetime
treino_data["Data"] = pd.to_datetime(treino_data["Data"])

# Adiciona a coluna de intensidade baseada no cluster
cluster_labels = {0: 'Moderado', 1: 'Intenso', 2: 'Moderado'}
treino_data['Cluster'] = pd.cut(treino_data.index, bins=3, labels=[0, 1, 2])
treino_data['Intensidade'] = treino_data['Cluster'].map(cluster_labels)

# Carrega as informações de bioData
calorias = somar_calorias_perdidas(bio_data["calories"])
duracao = convert_duration(bio_data["duration"])
frequencia_cardíaca_media = bio_data["heart_rate"]["average"]
frequencia_cardíaca_maxima = bio_data["heart_rate"]["maximum"]
tipo_de_treino = bio_data["detailed_sport_info"]
data_treino = pd.to_datetime(bio_data["start_time"])


# Informações do perfil
# Nome, altura e peso
# Função para exibir informações do usuário no Streamlit
def exibir_informacoes_usuario():
    # Instanciar a classe adaptadora
    instancia = PolarAccessLinkAdapter()

    # Obter informações do usuário
    user_info = instancia.get_user_information()

    return user_info


# Streamlit - Interface
informacoes_usuario = exibir_informacoes_usuario()

primeiro_nome = informacoes_usuario.get("first-name", "Atributo não encontrado")
ultimo_nome = informacoes_usuario.get("last-name", "Atributo não encontrado")
peso = informacoes_usuario.get("weight", "Atributo não encontrado")
altura = informacoes_usuario.get("height", "Atributo não encontrado")

# st.sidebar.header("Olá, seja muito bem vindo!")
st.sidebar.header("Olá, " + primeiro_nome + " " + ultimo_nome)
st.sidebar.write(f"Peso: {peso} kg")
st.sidebar.write(f"Altura: {altura} cm")
# st.sidebar.write(f"Data do treino: {data_treino.strftime('%d/%m/%Y %H:%M')}")

# Cria colunas para o grid de 2 gráficos
col1, col2 = st.columns(2)

# Gráfico 1: Intensidade ao Longo do Tempo
with col1:
    # Configurar Streamlit
    st.subheader("Intensidade do Treino")

    # Caminho para o arquivo JSON fornecido
    file_path = '../Data/bioData.json'

    data_loader = DataLoader(file_path)
    json_data = data_loader.load_json_data()
    df = data_loader.extract_data()

    # Remove o dia da semana do campo 'start_time' e converter para datetime
    df['start_time'] = df['start_time'].apply(
        lambda x: re.match(r'\d{2}/\d{2}', x).group(0) + '/2024')
    df['start_time'] = pd.to_datetime(df['start_time'], format='%d/%m/%Y')

    # Ajusta o tamanho dos pontos e formatar as datas no hover
    df['Data'] = df['start_time'].dt.strftime('%d/%m/%Y')

    # Obtem os anos e meses únicos
    anos_unicos_Intensity = df["start_time"].dt.year.unique()
    meses_unicos_en_Intensity = df["start_time"].dt.month.unique()

    # Dicionário de tradução de meses de inglês para português
    meses_pt = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }

    # Criar os widgets para seleção de ano e mês
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        selected_month_Intensity = st.selectbox(
            "Selecione o mês",
            [meses_pt[mes] for mes in meses_unicos_en_Intensity],
            key="mes_intensidade"
        )
    with col1_2:
        selected_year_Intensity = st.selectbox(
            "Selecione o ano",
            anos_unicos_Intensity,
            key="ano_intensidade"
        )

    # Adiciona dados de frequência cardíaca ao DataFrame
    heart_rate_data = [entry["heart_rate"]["average"] for entry in json_data]
    df['heart_rate_avg'] = heart_rate_data

    # Seleciona as colunas para o clustering
    X = df[['heart_rate_avg', 'calories']]

    # Aplica K-means com 3 clusters
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
    df['cluster'] = kmeans.labels_

    # Calcula a média de frequência cardíaca e calorias por cluster
    cluster_means = df.groupby('cluster')[['heart_rate_avg', 'calories']].mean()

    # Ordena os clusters por calorias e atribuir rótulos baseados nas médias
    sorted_clusters = cluster_means.sort_values(by='calories')
    cluster_labels = {sorted_clusters.index[0]: 'Baixa Intensidade',
                      sorted_clusters.index[1]: 'Intensidade Moderada',
                      sorted_clusters.index[2]: 'Alta Intensidade'}
    df['cluster_category'] = df['cluster'].map(cluster_labels)

    # Define cores para cada categoria de cluster
    color_map = {
        'Baixa Intensidade': 'green',
        'Intensidade Moderada': 'blue',
        'Alta Intensidade': 'red'
    }

    # Filtra o DataFrame pelo mês e ano selecionados
    mes_selecionado_num = {v: k for k, v in meses_pt.items()}[selected_month_Intensity]
    df_filtrado = df[
        (df['start_time'].dt.year == selected_year_Intensity) &
        (df['start_time'].dt.month == mes_selecionado_num)
        ]

    # Cria gráfico de dispersão interativo com os dados filtrados
    fig = px.scatter(
        df_filtrado,
        x='duration',
        y='heart_rate_avg',
        color='cluster_category',
        color_discrete_map=color_map,
        hover_data={'Data': True},
        labels={
            'heart_rate_avg': 'Frequência Cardíaca Média (bpm)',
            'calories': 'Calorias Queimadas',
            'cluster_category': 'Intensidade do Treino'
        },
        category_orders={"cluster_category": [
            "Alta Intensidade", "Intensidade Moderada", "Baixa Intensidade"]}
    )

    # Aumenta o tamanho dos pontos para melhorar a visualização
    fig.update_traces(marker=dict(size=10))

    # Exibe o gráfico
    st.plotly_chart(fig, use_container_width=True)


def get_calories_by_date(bio_data, selected_date):
    for entry in bio_data:
        if isinstance(entry, dict) and "start_time" in entry:
            entry_date = datetime.strptime(entry["start_time"][:10], "%Y-%m-%d").date()
            if entry_date == selected_date:
                duration = entry.get("duration", "")
                if duration.startswith("PT") and duration.endswith("S"):
                    try:
                        duration_seconds = float(duration[2:-1])
                        duration_minutes = int(duration_seconds // 60)
                    except ValueError:
                        duration_minutes = 0
                else:
                    duration_minutes = 0
                return (
                entry["calories"], entry["heart_rate"]["average"], entry["heart_rate"]["maximum"], duration_minutes)
    return 0, 0, 0, 0


# Gráfico 2: Resumo Diário
with col2:
    st.subheader("Resumo Diário")
    data_selecionada = st.date_input("Data", value=pd.to_datetime(treino_data["Data"].max()))

    data_str = data_selecionada.strftime("%Y-%m-%d")
    numero_exercicios = 0

    calorias, frequencia_media, frequencia_maxima, duracao_diaria = get_calories_by_date(bio_data_full,
                                                                                         data_selecionada)

    if data_str in set_data["schedule"]:
        numero_exercicios = sum(len(exercise["sets"]) for exercise in set_data["schedule"][data_str]["exercises"])

    col_icon1, col_icon2 = st.columns(2)
    with col_icon1:
        st.metric("💛 Freq. Cardíaca Média (bpm)", int(frequencia_media))
        st.metric("❤️ Freq. Cardíaca Máxima (bpm)", int(frequencia_maxima))

    with col_icon2:
        st.metric("🔥 Calorias Perdidas", int(calorias))
        st.metric("⏱️ Duração Total (min)", int(duracao_diaria))
        st.metric("🏃 Número de Exercícios", numero_exercicios)

# Cria mais colunas para os outros gráficos
col3, col4 = st.columns(2)  # Correção aqui


def get_calories_by_date_month(bio_data, selected_month, selected_year):
    """
    Função para processar os dados de bio_data e retornar métricas por mês e ano.
    """
    data = []
    for entry in bio_data:
        if isinstance(entry, dict) and "start_time" in entry:
            # Converte a data do formato string para datetime.date
            entry_date = datetime.strptime(entry["start_time"][:10], "%Y-%m-%d").date()

            # Verifica se o mês e o ano correspondem ao selecionado
            if entry_date.month == selected_month and entry_date.year == selected_year:
                # Processa duração
                duration = entry.get("duration", "")
                if duration.startswith("PT") and duration.endswith("S"):
                    try:
                        duration_seconds = float(duration[2:-1])
                        duration_minutes = int(duration_seconds // 60)
                    except ValueError:
                        duration_minutes = 0
                else:
                    duration_minutes = 0

                # Adiciona os dados processados à lista
                data.append({
                    "Mês": entry_date.month,
                    "Ano": entry_date.year,
                    "Exercício": entry.get("activity", "Desconhecido"),
                    "Calorias": entry["calories"],
                    "FC_Max": entry["heart_rate"].get("maximum", 0) if "heart_rate" in entry else 0,
                    "FC_Media": entry["heart_rate"].get("average", 0) if "heart_rate" in entry else 0,
                    "Duração": duration_minutes
                })

    # Retorna os dados como DataFrame
    return pd.DataFrame(data)


# Gráfico de Calorias Perdidas Mensalmente
with col3:
    # Cria bio_data_df
    bio_data_df = pd.DataFrame(bio_data_full)
    bio_data_df["Data"] = pd.to_datetime(bio_data_df["start_time"]).dt.date
    bio_data_df["Calorias"] = bio_data_df["calories"]
    bio_data_df["Duração"] = (pd.to_timedelta(bio_data_df["duration"]) / pd.Timedelta(seconds=1)) / 60
    bio_data_df["FC_Max"] = bio_data_df["heart_rate"].apply(lambda x: x.get("maximum", 0) if isinstance(x, dict) else 0)
    bio_data_df["FC_Media"] = bio_data_df["heart_rate"].apply(
        lambda x: x.get("average", 0) if isinstance(x, dict) else 0)



    # Carrega treino_data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    treino_data_path = os.path.join(script_dir, "../Data/set.json")
    with open(treino_data_path, "r") as file:
        treino_data_month = json.load(file)

    treino_data_df = pd.DataFrame(treino_data_month["schedule"].values())
    treino_data_df["Data"] = pd.to_datetime(treino_data_df.index).date
    treino_data_df = treino_data_df.explode("exercises")
    treino_data_df = treino_data_df.reset_index(drop=True)
    treino_data_df["Exercício"] = treino_data_df["exercises"].apply(
        lambda x: x["sets"] if isinstance(x, dict) else None)

    # Merge dos DataFrames
    treino_data_df = treino_data_df.merge(
        bio_data_df[["Data", "Calorias", "Duração", "FC_Max", "FC_Media"]],
        on="Data",
        how="left"
    )

    # Filtra dados pelo mês e ano selecionados
    mes_selecionado = [k for k, v in meses_pt.items() if v == selected_month_Intensity][0]
    treino_data_filtrado = treino_data_df[
        (pd.to_datetime(treino_data_df["Data"]).dt.year == selected_year_Intensity) &
        (pd.to_datetime(treino_data_df["Data"]).dt.month == mes_selecionado)
        ]

    # Agrupa e soma métricas por mês e exercício
    calorias_por_mes = treino_data_filtrado.groupby(["Data", "Exercício"], as_index=False).sum(numeric_only=True)

    # Seleciona métrica para visualização
    metric_options = ["Calorias", "Duração", "Frequência Cardíaca Máxima", "Frequência Cardíaca Média"]
    selected_metric = st.selectbox("Indicador:", metric_options)

    # Converte a coluna "Data" para datetime, se ainda não estiver
    bio_data_df["Data"] = pd.to_datetime(bio_data_df["Data"], errors='coerce')

    # Filtra os dados de bio_data_df com base no ano e mês selecionados
    bio_data_filtrado = bio_data_df[
        (bio_data_df["Data"].dt.year == selected_year_Intensity) &
        (bio_data_df["Data"].dt.month == [k for k, v in meses_pt.items() if v == selected_month_Intensity][0])
        ]

    if selected_metric == "Calorias":

        # Cria um DataFrame para plotar todas as calorias queimadas
        calorias_por_mes = pd.DataFrame({
            "Data": bio_data_filtrado["Data"],
            "Calorias Queimadas": bio_data_filtrado["Calorias"]  # Supondo que a coluna se chama "Calorias"
        })

        # Plota gráfico
        # Cria o gráfico de calorias queimadas
        fig_calorias = px.line(
            calorias_por_mes,
            x="Data",
            y="Calorias Queimadas",
            markers=True,
            title=f"Calorias Queimadas Mensais - {selected_month_Intensity}",
            labels={"Data": "Data", "Calorias Queimadas": "Calorias"},
        )

        # Atualiza o layout do gráfico
        fig_calorias.update_layout(
            xaxis_title="Data",
            yaxis_title="Calorias",
            template="plotly_dark",
            xaxis=dict(tickangle=45)
        )

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig_calorias, use_container_width=True)

    elif selected_metric == "Duração":
        # Cria um DataFrame para plotar todas as durações do treino
        duracoes_por_mes = pd.DataFrame({
            "Data": bio_data_filtrado["Data"],
            "Duração do Treino": bio_data_filtrado["Duração"]  # Supondo que a coluna se chama "Duração"
        })

        # Plota gráfico
        # Cria o gráfico de durações do treino
        fig_duracao = px.line(
            duracoes_por_mes,
            x="Data",
            y="Duração do Treino",
            markers=True,
            title=f"Durações do Treino Mensais - {selected_month_Intensity}",
            labels={"Data": "Data", "Duração do Treino": "Duração (minutos)"},
            line_shape='linear'  # Forma da linha (pode ser ajustada conforme necessário)
        )

        # Atualiza o layout do gráfico
        fig_duracao.update_layout(
            xaxis_title="Data",
            yaxis_title="Duração (minutos)",
            template="plotly_dark",
            xaxis=dict(tickangle=45)
        )

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig_duracao, use_container_width=True)

    elif selected_metric == "Frequência Cardíaca Máxima":
        # Cria um DataFrame para plotar todas as frequências cardíacas
        frequencias_por_mes = pd.DataFrame({
            "Data": bio_data_filtrado["Data"],
            "Frequência Cardíaca": bio_data_filtrado["FC_Max"]  # Supondo que a coluna se chama "Frequência Cardíaca"
        })

        # Cria o gráfico de frequências cardíacas
        fig_frequencia = px.line(
            frequencias_por_mes,
            x="Data",
            y="Frequência Cardíaca",
            markers=True,
            title=f"Frequências Cardíacas Mensais - {selected_month_Intensity}",
            labels={"Data": "Data", "Frequência Cardíaca": "Frequência Cardíaca (bpm)"},
        )

        # Atualiza o layout do gráfico
        fig_frequencia.update_layout(
            xaxis_title="Data",
            yaxis_title="Frequência Cardíaca (bpm)",
            template="plotly_dark",
            xaxis=dict(tickangle=45)
        )

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig_frequencia, use_container_width=True)

    else:
        # Cria um DataFrame para plotar todas as frequências cardíacas médias
        frequencias_media_por_mes = pd.DataFrame({
            "Data": bio_data_filtrado["Data"],
            "Frequência Cardíaca Média": bio_data_filtrado["FC_Media"]  # Supondo que a coluna se chama "FC_Media"
        })

        # Cria o gráfico de frequências cardíacas médias
        fig_frequencia_media = px.line(
            frequencias_media_por_mes,
            x="Data",
            y="Frequência Cardíaca Média",
            markers=True,
            title=f"Frequências Cardíacas Médias Mensais - {selected_month_Intensity}",
            labels={"Data": "Data", "Frequência Cardíaca Média": "Frequência Cardíaca (bpm)"},
        )

        # Atualiza o layout do gráfico
        fig_frequencia_media.update_layout(
            xaxis_title="Data",
            yaxis_title="Frequência Cardíaca (bpm)",
            template="plotly_dark",
            xaxis=dict(tickangle=45)
        )

        # Exibe o gráfico no Streamlit
        st.plotly_chart(fig_frequencia_media, use_container_width=True)

with col4:
    st.subheader("Tabela de Exercícios por Categoria")



    # Função para criar a tabela com todas as categorias dos exercícios e seus respectivos sets
    def criar_tabela_categorias_por_dia(data_selecionada, set_data):
        """
        Retorna as categorias de todos os exercícios realizados na data selecionada,
        com categorias, exercícios e detalhes expandidos.
        """
        data_str = data_selecionada.strftime("%Y-%m-%d")  # Formatar a data para string

        # Verificar se a data está no conjunto de dados
        if data_str not in set_data.get("schedule", {}):
            st.write(f"Data {data_str} não encontrada no cronograma.")
            return pd.DataFrame(columns=["Categoria", "Exercício", "Detalhe 1", "Detalhe 2"])

        # Processar os exercícios do dia
        categorias_sets = []
        exercicios = set_data["schedule"][data_str].get("exercises", [])
        if not exercicios:
            st.write(f"Nenhum exercício encontrado para a data {data_str}.")
            return pd.DataFrame(columns=["Categoria", "Exercício", "Detalhe 1", "Detalhe 2"])

        # Iterar pelos exercícios
        for ex in exercicios:
            categoria = ex.get("category", "Desconhecida")
            sets = ex.get("sets", [])

            if sets:  # Se houver sets, processa
                if isinstance(sets[0], dict):  # Estrutura com dicionários
                    for set_item in sets:
                        exercicio = set_item.get('exercise', 'Sem exercício')
                        detalhes = set_item.get('details', '').split(', ')
                        detalhes_preenchidos = detalhes + [''] * (2 - len(detalhes))
                        categorias_sets.append({
                            "Categoria": categoria,
                            "Exercício": exercicio,
                            "Detalhe 1": detalhes_preenchidos[0],
                            "Detalhe 2": detalhes_preenchidos[1]
                        })
                else:  # Estrutura com strings simples
                    for exercicio in sets:
                        categorias_sets.append({
                            "Categoria": categoria,
                            "Exercício": exercicio,
                            "Detalhe 1": "",
                            "Detalhe 2": ""
                        })
            else:  # Caso a lista de sets esteja vazia
                categorias_sets.append({
                    "Categoria": categoria,
                    "Exercício": "Sem exercício",
                    "Detalhe 1": "",
                    "Detalhe 2": ""
                })

        # Criar e retornar o DataFrame
        return pd.DataFrame(categorias_sets)


    # Gera a tabela com categorias para a data selecionada
    tabela_categorias_dia = criar_tabela_categorias_por_dia(data_selecionada, set_data)

    # Exibe a tabela no Streamlit
    if not tabela_categorias_dia.empty:
        st.dataframe(tabela_categorias_dia)
    else:
        st.write("Nenhum exercício encontrado para a data selecionada.")