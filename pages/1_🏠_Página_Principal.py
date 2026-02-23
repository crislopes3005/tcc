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
# CADÚNICO
# =========================
st.markdown("""
**Participantes no CadÚnico**

Destaca-se em azul os participantes cadastrados no CadÚnico, 
indicador relevante de vulnerabilidade socioeconômica.
""")

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


# =========================
# PIRÂMIDE ETÁRIA (SEM NEGATIVO)
# =========================
st.divider()
st.markdown("""
**Distribuição por Faixa Etária e Gênero**

O gráfico permite comparar a participação de homens e mulheres 
em diferentes faixas etárias.
""")

df_idade = df_participantes.dropna(subset=["faixaEtaria", "sex_final"])

contagem = (
    df_idade.groupby(["faixaEtaria", "sex_final"])
    .size()
    .reset_index(name="Participantes")
)

fig = px.bar(
    contagem,
    y="faixaEtaria",
    x="Participantes",
    color="sex_final",
    orientation="h",
    barmode="group",
    text="Participantes",
    color_discrete_map={
        "Masculino": "#B0B0B0",
        "Feminino": "#5B7C99"
    }
)

fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# =========================
# REGIÃO
# =========================
st.markdown("""
**Participantes por Região**

Regiões Norte e Nordeste são destacadas devido à sua relevância 
no debate sobre desigualdades regionais.
""")

contagem = df_participantes["regiao"].value_counts().reset_index()
contagem.columns = ["Regiao", "Participantes"]
contagem = contagem.sort_values("Participantes", ascending=False)

contagem["cor"] = contagem["Regiao"].apply(
    lambda x: "#5B7C99" if x in ["N", "NE", "Norte", "Nordeste"] else "#D3D3D3"
)

fig = px.bar(contagem, x="Regiao", y="Participantes",
             color="cor", color_discrete_map="identity",
             text="Participantes")

fig.update_layout(showlegend=False,
                  xaxis=dict(categoryorder="total descending"))

fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# =========================
# UF
# =========================
st.markdown("""
**Participantes por Unidade da Federação**

Estados da Região Norte são destacados por sua relevância 
nas análises de desigualdade territorial.
""")

estados_norte = ["AC","AP","AM","PA","RO","RR","TO"]

contagem = df_participantes["siglaUf"].value_counts().reset_index()
contagem.columns = ["UF", "Participantes"]
contagem = contagem.sort_values("Participantes", ascending=False)

contagem["cor"] = contagem["UF"].apply(
    lambda x: "#5B7C99" if x in estados_norte else "#D3D3D3"
)

fig = px.bar(contagem, x="UF", y="Participantes",
             color="cor", color_discrete_map="identity",
             text="Participantes")

fig.update_layout(showlegend=False,
                  xaxis=dict(categoryorder="total descending"))

fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# =========================
# OCUPAÇÃO
# =========================
st.markdown("""
**Participantes por Ocupação**

Destacam-se servidores públicos e trabalhadores de empresas públicas,
pela possível maior familiaridade com processos institucionais.
""")

contagem = df_participantes["ocupacao_grupo"].value_counts().reset_index()
contagem.columns = ["Ocupacao", "Participantes"]
contagem = contagem.sort_values("Participantes", ascending=False)

contagem["cor"] = contagem["Ocupacao"].apply(
    lambda x: "#5B7C99" if x in ["servidor_publico", "empresa_publica"] else "#D3D3D3"
)

fig = px.bar(contagem, x="Ocupacao", y="Participantes",
             color="cor", color_discrete_map="identity",
             text="Participantes")

fig.update_layout(showlegend=False,
                  xaxis=dict(categoryorder="total descending"))

fig.update_traces(textposition="outside")
st.plotly_chart(fig, use_container_width=True)


# =========================
# RODAPÉ
# =========================
st.divider()
st.subheader('Autora do projeto')
st.write("Cristiane Lopes de Assis")
