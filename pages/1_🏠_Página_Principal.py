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

# =========================
# PIRÂMIDE ETÁRIA
# =========================

st.divider()
st.subheader("Distribuição por Faixa Etária e Gênero")

df_idade = df_participantes.dropna(subset=["faixaEtaria", "sex_final"]).copy()

# Contagem por faixa e sexo
contagem = (
    df_idade
    .groupby(["faixaEtaria", "sex_final"])
    .size()
    .reset_index(name="Participantes")
)

# Ordem das faixas (ajuste se necessário)
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

# Tornar masculino negativo
contagem["valor_plot"] = contagem.apply(
    lambda row: -row["Participantes"] if row["sex_final"] == "Masculino"
    else row["Participantes"],
    axis=1
)

fig = px.bar(
    contagem,
    y="faixaEtaria",
    x="valor_plot",
    color="sex_final",
    orientation="h",
    barmode="relative",
    color_discrete_map={
        "Masculino": "#7A8FA6",
        "Feminino": "#5B7C99"
    }
)

fig.update_layout(
    xaxis_title="Participantes",
    yaxis_title="Faixa Etária",
    xaxis=dict(tickformat=","),
)

# Ajuste para mostrar valores absolutos no eixo
fig.update_xaxes(tickvals=list(range(-100,101,20)))

st.plotly_chart(fig, use_container_width=True)
# =========================
# 3️⃣ REGIÃO (BARRA)
# =========================

contagem = df_participantes["regiao"].value_counts().reset_index()
contagem.columns = ["Regiao", "Participantes"]

contagem["cor"] = contagem["Regiao"].apply(
        lambda x: "#5B7C99" if x in ["N", "NE", "Norte", "Nordeste"] else "#D3D3D3"
    )

fig = px.bar(
        contagem,
        x="Regiao",
        y="Participantes",
        color="cor",
        color_discrete_map="identity"
    )

fig.update_layout(title="Região", showlegend=False,
                     xaxis=dict(categoryorder="total descending"))
st.plotly_chart(fig, use_container_width=True)

# =========================
# 4️⃣ UF (BARRA)
# =========================

estados_norte = ["AC","AP","AM","PA","RO","RR","TO"]

contagem = df_participantes["siglaUf"].value_counts().reset_index()
contagem.columns = ["UF", "Participantes"]

contagem = contagem.sort_values("Participantes", ascending=False)

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

fig.update_layout(title="Estado (UF)", showlegend=False,
                     xaxis=dict(categoryorder="total descending"))
st.plotly_chart(fig, use_container_width=True)


# =========================
# OCUPAÇÃO (LINHA FINAL)
# =========================

st.divider()

contagem = df_participantes["ocupacao_grupo"].value_counts().reset_index()
contagem.columns = ["Ocupacao", "Participantes"]

contagem = contagem.sort_values("Participantes", ascending=False)

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

fig.update_layout(title="Ocupação", showlegend=False,
                 xaxis=dict(categoryorder="total descending"))

st.plotly_chart(fig, use_container_width=True)

# =========================
# RODAPÉ
# =========================
st.divider()
st.subheader('Autora do projeto')
st.write("Cristiane Lopes de Assis")
