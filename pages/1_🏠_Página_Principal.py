# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG STREAMLIT (SEMPRE PRIMEIRO)
# =========================
st.set_page_config(
    page_title='Análise de representatividade - Plataforma Brasil Participativo 🗣️ 🤝',
    page_icon='📊',
    layout='wide'
)

# =========================
# CARREGAR DADOS (UPLOAD OU PADRÃO)
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

    except Exception as e:
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
# FILTROS SIDEBAR
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

    cluster_selecionado = st.sidebar.selectbox(
        "Selecione a classificação do proponente:",
        lista_cluster
    )

    if cluster_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[df_filtrado['cluster_k3'] == cluster_selecionado]

# =========================
# TEXTO EXPLICATIVO
# =========================
st.write("""
<div style="text-align: justify">

Para análise da representatividade nos processos de participação hospedados na Plataforma Brasil Participativo, foram selecionados os processos do Plano Clima Participativo e do Novo Plano Nacional de Cultura.

Para cada um dos processos é possível avaliar o perfil socioeconômico dos proponentes pelo conjunto de propostas recebido e pelo conjunto de propostas que foram ou não selecionadas para análise das respectivas pastas.

É possível também analisar o perfil socioeconômico pela classificação dos proponentes, a saber: participantes de baixa mobilização, participantes altamente engajados e participantes socioeconomicamente vulneráveis.

</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# CARDS KPI
# =========================
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Número de propostas recebidas")
    st.metric("", df_filtrado['id_x'].count())

with col2:
    st.subheader("Número de proponentes distintos")
    st.metric("", df_filtrado['id_autor'].nunique())

with col3:
    st.subheader("Número de propostas analisadas")
    analisadas = df_filtrado[df_filtrado['state'] == 'Analisado']
    st.metric("", len(analisadas))

st.divider()

# =========================
# DATA PARTICIPANTES
# =========================
df_participantes = df_filtrado.drop_duplicates(subset='id_autor')

# =========================
# GRÁFICO PIZZA - cadunico
# =========================

df_cadunico = df_participantes.dropna(subset=["cadunico"])

contagem = df_cadunico["cadunico"].value_counts().reset_index()
contagem.columns = ["Cadastro", "Participantes"]

fig = px.pie(
    contagem,
    names="Cadastro",
    values="Participantes",
    hole=0.4
)

# Definição das cores
cores = {
    "Não cadastrado": "#B0B0B0",   # cinza
    "Cadastrado": "#5B7C99"     # azul acinzentado
}

fig.update_traces(
    marker=dict(
        colors=[cores.get(cadunico, "#CCCCCC") for cadunico in contagem["Cadastro"]]
    ),
    textinfo="percent+label"
)

fig.update_layout(
    title="Participantes no CadÚnico",
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# GRÁFICOS ORGANIZADOS
# =========================

# -------------------------
# COLUNAS 1 A 4
# -------------------------
col1, col2, col3, col4 = st.columns(4)

# =========================
# 1️⃣ SEXO (PIZZA)
# =========================
with col1:
    df_sexo = df_participantes.dropna(subset=["sex_final"])
    contagem = df_sexo["sex_final"].value_counts().reset_index()
    contagem.columns = ["Sexo", "Participantes"]

    fig = px.pie(
        contagem,
        names="Sexo",
        values="Participantes",
        hole=0.4
    )

    cores = {
        "Masculino": "#B0B0B0",
        "Feminino": "#5B7C99"
    }

    fig.update_traces(
        marker=dict(
            colors=[cores.get(sexo, "#CCCCCC") for sexo in contagem["Sexo"]]
        ),
        textinfo="percent+label"
    )

    fig.update_layout(title="Sexo")

    st.plotly_chart(fig, use_container_width=True)

# =========================
# 2️⃣ FAIXA ETÁRIA (BARRA)
# =========================
with col2:
    contagem = df_participantes["faixaEtaria"].value_counts().reset_index()
    contagem.columns = ["Faixa", "Participantes"]

    contagem["cor"] = contagem["Faixa"].apply(
        lambda x: "#5B7C99" if x == "25 a 44 anos" else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x="Faixa",
        y="Participantes",
        color="cor",
        color_discrete_map="identity"
    )

    fig.update_layout(title="Faixa etária", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 3️⃣ REGIÃO (BARRA)
# =========================
with col3:
    contagem = df_participantes["regiao"].value_counts().reset_index()
    contagem.columns = ["Regiao", "Participantes"]

    contagem["cor"] = contagem["Regiao"].apply(
        lambda x: "#5B7C99" if x in ["NO", "NE", "Norte", "Nordeste"] else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x="Regiao",
        y="Participantes",
        color="cor",
        color_discrete_map="identity"
    )

    fig.update_layout(title="Região", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 4️⃣ UF (BARRA)
# =========================
with col4:
    estados_norte = ["AC","AP","AM","PA","RO","RR","TO"]

    contagem = df_participantes["siglaUf"].value_counts().reset_index()
    contagem.columns = ["UF", "Participantes"]

    contagem["cor"] = contagem["UF"].apply(
        lambda x: "#5B7C99" if x in estados_norte else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x="UF",
        y="Participantes",
        color="cor",
        color_discrete_map="identity"
    )

    fig.update_layout(title="Estado (UF)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# =========================
# OCUPAÇÃO (LINHA FINAL)
# =========================

st.divider()

contagem = df_participantes["ocupacao_grupo"].value_counts().reset_index()
contagem.columns = ["Ocupacao", "Participantes"]

contagem["cor"] = contagem["Ocupacao"].apply(
    lambda x: "#5B7C99" if x in ["servidor_publico", "empresa_publica"] else "#D3D3D3"
)

fig = px.bar(
    contagem,
    x="Ocupacao",
    y="Participantes",
    color="cor",
    color_discrete_map="identity"
)

fig.update_layout(title="Ocupação", showlegend=False)

st.plotly_chart(fig, use_container_width=True)

# =========================
# RODAPÉ
# =========================
st.divider()
st.subheader('Autora do projeto')
st.write("Cristiane Lopes de Assis")
