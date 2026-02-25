# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG STREAMLIT
# =========================
st.set_page_config(
    page_title='Análise de representatividade - Plataforma Brasil Participativo 🗣️ 🤝',
    page_icon='📊',
    layout='wide'
)

# =========================
# CARREGAR DADOS
# =========================
st.sidebar.header("📂 Base de dados")

arquivo_upload = st.sidebar.file_uploader(
    "Envie um arquivo CSV para substituir a base padrão",
    type=["csv"]
)

if arquivo_upload is not None:
    try:
        try:
            df = pd.read_csv(arquivo_upload, sep=';', encoding='utf-8')
        except UnicodeDecodeError:
            arquivo_upload.seek(0)
            df = pd.read_csv(arquivo_upload, sep=';', encoding='latin1')

        st.sidebar.success("Arquivo carregado com sucesso!")
        st.session_state["df"] = df

    except Exception:
        st.sidebar.error("Erro ao carregar o arquivo.")
        st.stop()
else:
    df = pd.read_csv('df_final.csv', sep=';', encoding='utf-8')
    st.session_state["df"] = df


# =========================
# TÍTULO
# =========================
st.markdown('# Análise de representatividade - Plataforma Brasil Participativo 🗣️ 🤝')

# =========================
# FILTROS
# =========================
st.sidebar.header("🔎 Filtros")
escolha = st.sidebar.selectbox("Deseja filtrar os resultados?", ['Não', 'Sim'])

df_filtrado = df.copy()

if escolha == 'Sim':

    lista_processos = df['processo'].dropna().unique().tolist()
    lista_processos.insert(0, "Marcar Todos")
    processo_selecionado = st.sidebar.selectbox("Selecione um processo:", lista_processos)

    if processo_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[df_filtrado['processo'] == processo_selecionado]

    lista_status = df_filtrado['state'].dropna().unique().tolist()
    lista_status.insert(0, "Marcar Todos")
    status_selecionado = st.sidebar.selectbox("Selecione o estado da proposta:", lista_status)

    if status_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[df_filtrado['state'] == status_selecionado]

    lista_cluster = df_filtrado['cluster_k3'].dropna().unique().tolist()
    lista_cluster.insert(0, "Marcar Todos")
    cluster_selecionado = st.sidebar.selectbox("Selecione a classificação do proponente:", lista_cluster)

    if cluster_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[df_filtrado['cluster_k3'] == cluster_selecionado]


# =========================
# KPIs
# =========================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Número de propostas recebidas", df_filtrado['id_x'].count())

with col2:
    st.metric("Número de proponentes distintos", df_filtrado['id_autor'].nunique())

with col3:
    analisadas = df_filtrado[df_filtrado['state'] == 'Analisado']
    st.metric("Número de propostas analisadas", len(analisadas))

st.divider()

df_participantes = df_filtrado.drop_duplicates(subset='id_autor')


# =========================
# SEÇÃO VISUAL ANALÍTICA
# =========================

st.divider()

# =========================
# 1️⃣ CADÚNICO
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Participantes no CadÚnico

Destacam-se em azul os participantes cadastrados no CadÚnico,
indicador central de vulnerabilidade socioeconômica.

A proporção permite avaliar o grau de inclusão social
dos participantes do processo.
""")

with col_grafico:
    df_cadunico = df_participantes.dropna(subset=["cadunico"])
    contagem = df_cadunico["cadunico"].value_counts().reset_index()
    contagem.columns = ["Cadastro", "Participantes"]

    fig = px.pie(contagem, names="Cadastro", values="Participantes", hole=0.4)

    cores = {"Cadastrado": "#5B7C99", "Não cadastrado": "#D3D3D3"}

    fig.update_traces(
        marker=dict(colors=[cores.get(v, "#CCCCCC") for v in contagem["Cadastro"]]),
        textinfo="percent+label"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# PIRÂMIDE ETÁRIA COM %
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Estrutura Etária por Gênero

A pirâmide apresenta a distribuição etária dos participantes,
incluindo valores absolutos e percentuais.
""")

with col_grafico:

    df_idade = df_participantes.dropna(subset=["faixaEtaria", "sex_final"]).copy()

    contagem = (
        df_idade.groupby(["faixaEtaria", "sex_final"])
        .size()
        .reset_index(name="Participantes")
    )

    total = contagem["Participantes"].sum()
    contagem["Percentual"] = (contagem["Participantes"] / total * 100).round(1)

    ordem_faixas = [
        "0 a 12 anos",
        "13 a 17 anos",
        "18 a 24 anos",
        "25 a 44 anos",
        "45 a 59 anos",
        "Maior de 60 anos"
    ]

    contagem["faixaEtaria"] = pd.Categorical(
        contagem["faixaEtaria"],
        categories=ordem_faixas,
        ordered=True
    )

    contagem = contagem.sort_values("faixaEtaria")

    contagem["valor_plot"] = contagem.apply(
        lambda row: -row["Participantes"] if row["sex_final"] == "Masculino"
        else row["Participantes"],
        axis=1
    )

    contagem["label"] = (
        contagem["Participantes"].astype(str) +
        " (" + contagem["Percentual"].astype(str) + "%)"
    )

    fig = px.bar(
        contagem,
        y="faixaEtaria",
        x="valor_plot",
        color="sex_final",
        orientation="h",
        barmode="relative",
        text="label",
        color_discrete_map={
            "Masculino": "#B0B0B0",
            "Feminino": "#5B7C99"
        }
    )

    fig.update_traces(textposition="outside")

    fig.update_xaxes(
        showticklabels=False,
        showgrid=False,
        zeroline=True,
        zerolinecolor="#999999"
    )

    st.plotly_chart(fig, use_container_width=True)
    
# =========================
# REGIÃO COM %
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Participação Regional

O gráfico apresenta valores absolutos e percentuais,
permitindo avaliar a concentração territorial.
""")

with col_grafico:

    contagem = df_participantes["regiao"].value_counts().reset_index()
    contagem.columns = ["Regiao", "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=False)

    total = contagem["Participantes"].sum()
    contagem["Percentual"] = (contagem["Participantes"] / total * 100).round(1)

    contagem["label"] = (
        contagem["Participantes"].astype(str) +
        " (" + contagem["Percentual"].astype(str) + "%)"
    )

    contagem["cor"] = contagem["Regiao"].apply(
        lambda x: "#5B7C99" if x in ["N", "NE", "Norte", "Nordeste"] else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x="Regiao",
        y="Participantes",
        color="cor",
        color_discrete_map="identity",
        text="label"
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(categoryorder="total descending")
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

# =========================
# MAPA DO BRASIL POR UF (FUNCIONA)
# =========================

import json
import requests

st.divider()
st.subheader("Distribuição Territorial dos Participantes")

# Contagem por UF
df_mapa = df_participantes.copy()

contagem = df_mapa["siglaUf"].value_counts().reset_index()
contagem.columns = ["UF", "Participantes"]

# GeoJSON oficial dos estados do Brasil
url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
geojson = requests.get(url).json()

fig = px.choropleth(
    contagem,
    geojson=geojson,
    locations="UF",
    featureidkey="properties.sigla",
    color="Participantes",
    color_continuous_scale="Blues"
)

fig.update_geos(
    fitbounds="locations",
    visible=False
)

st.plotly_chart(fig, use_container_width=True)
    
# =========================
# PERFIL DE OCUPAÇÃO 
# =========================

st.divider()

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Perfil de Ocupação

A distribuição evidencia o perfil socioocupacional dos participantes.

Destacam-se servidores públicos e trabalhadores de empresas públicas,
considerando sua possível maior familiaridade com processos institucionais.

A ordenação decrescente facilita a identificação das categorias
com maior concentração de participação.
""")

with col_grafico:

    contagem = df_participantes["ocupacao_grupo"].value_counts().reset_index()
    contagem.columns = ["Ocupacao", "Participantes"]

    # 🔹 Ordenar decrescente (maior primeiro)
    contagem = contagem.sort_values("Participantes", ascending=True)

    total = contagem["Participantes"].sum()
    contagem["Percentual"] = (contagem["Participantes"] / total * 100).round(1)

    contagem["cor"] = contagem["Ocupacao"].apply(
        lambda x: "#5B7C99" if x in ["servidor_publico", "empresa_publica"]
        else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        y="Ocupacao",
        x="Participantes",
        orientation="h",
        color="cor",
        color_discrete_map="identity",
        text=contagem["Participantes"].astype(str) +
             " (" + contagem["Percentual"].astype(str) + "%)"
    )

    # 🔹 Aqui está o segredo para manter maior em cima
    fig.update_layout(
        showlegend=False,
        yaxis=dict(
            categoryorder="array",
            categoryarray=contagem["Ocupacao"]  # mantém a ordem exata
        )
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

# =========================
# MAPA POR GRANDES REGIÕES (SEM REQUESTS)
# =========================

st.divider()

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Distribuição Regional

O mapa representa a intensidade da participação por grandes regiões,
permitindo visualizar a concentração territorial da representatividade.
""")

with col_grafico:

    df_mapa = df_participantes.copy()

    # Padronizar nomes
    mapa_regioes = {
        "N": "Norte",
        "NE": "Nordeste",
        "CO": "Centro-Oeste",
        "SE": "Sudeste",
        "S": "Sul"
    }

    df_mapa["regiao_nome"] = df_mapa["regiao"].replace(mapa_regioes)

    contagem = df_mapa["regiao_nome"].value_counts().reset_index()
    contagem.columns = ["Regiao", "Participantes"]

    # Coordenadas centrais aproximadas das regiões
    coordenadas = {
        "Norte": (-3, -60),
        "Nordeste": (-10, -40),
        "Centro-Oeste": (-15, -55),
        "Sudeste": (-20, -45),
        "Sul": (-27, -50)
    }

    contagem["lat"] = contagem["Regiao"].map(lambda x: coordenadas[x][0])
    contagem["lon"] = contagem["Regiao"].map(lambda x: coordenadas[x][1])

    fig = px.scatter_geo(
        contagem,
        lat="lat",
        lon="lon",
        size="Participantes",
        color="Participantes",
        hover_name="Regiao",
        scope="south america",
        color_continuous_scale="Blues",
        projection="mercator"
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    st.plotly_chart(fig, use_container_width=True)
