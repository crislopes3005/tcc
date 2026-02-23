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
# 2️⃣ PIRÂMIDE ETÁRIA
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Estrutura Etária por Gênero

O gráfico permite comparar a distribuição de homens e mulheres
em diferentes faixas etárias.

A visualização auxilia na identificação de concentrações
geracionais na participação.
""")

with col_grafico:
    df_idade = df_participantes.dropna(subset=["faixaEtaria", "sex_final"])

    contagem = (
        df_idade.groupby(["faixaEtaria", "sex_final"])
        .size()
        .reset_index(name="Participantes")
    )

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

    fig = px.bar(
        contagem,
        y="faixaEtaria",
        x="valor_plot",
        color="sex_final",
        orientation="h",
        barmode="relative",
        text="Participantes",
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

st.divider()

# =========================
# 3️⃣ REGIÃO
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Participação Regional

As regiões Norte e Nordeste são destacadas
por sua relevância no debate sobre desigualdade territorial.

O gráfico permite observar a concentração regional
dos participantes.
""")

with col_grafico:
    contagem = df_participantes["regiao"].value_counts().reset_index()
    contagem.columns = ["Regiao", "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=False)

    contagem["cor"] = contagem["Regiao"].apply(
        lambda x: "#5B7C99" if x in ["N", "NE", "Norte", "Nordeste"] else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x="Regiao",
        y="Participantes",
        color="cor",
        color_discrete_map="identity",
        text="Participantes"
    )

    fig.update_layout(showlegend=False,
                      xaxis=dict(categoryorder="total descending"))

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# 4️⃣ OCUPAÇÃO
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Perfil de Ocupação

Destacam-se servidores públicos e trabalhadores
de empresas públicas, considerando sua possível
maior familiaridade com processos institucionais.

A distribuição evidencia o perfil socioocupacional
dos participantes.
""")

with col_grafico:
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
        color_discrete_map="identity",
        text="Participantes"
    )

    fig.update_layout(showlegend=False,
                      xaxis=dict(categoryorder="total descending"))

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)
# =========================
# PERFIL DE OCUPAÇÃO - PARETO
# =========================

st.divider()

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Perfil de Ocupação (Análise de Pareto)

O gráfico apresenta a distribuição das ocupações em ordem decrescente,
acompanhada da curva de percentual acumulado.

A visualização permite identificar a concentração da participação
em determinadas categorias ocupacionais.
""")

with col_grafico:

    contagem = df_participantes["ocupacao_grupo"].value_counts().reset_index()
    contagem.columns = ["Ocupacao", "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=False)

    # Percentual acumulado
    contagem["Percentual"] = contagem["Participantes"] / contagem["Participantes"].sum() * 100
    contagem["Percentual_Acumulado"] = contagem["Percentual"].cumsum()

    # Destaque visual
    contagem["cor"] = contagem["Ocupacao"].apply(
        lambda x: "#5B7C99" if x in ["servidor_publico", "empresa_publica"] else "#D3D3D3"
    )

    # Gráfico de barras
    fig = px.bar(
        contagem,
        x="Ocupacao",
        y="Participantes",
        color="cor",
        color_discrete_map="identity",
        text="Participantes"
    )

    fig.update_traces(textposition="outside")

    # Linha acumulada
    fig.add_scatter(
        x=contagem["Ocupacao"],
        y=contagem["Percentual_Acumulado"],
        mode="lines+markers",
        name="% acumulado",
        yaxis="y2",
        line=dict(color="#2F4F4F", width=3)
    )

    # Segundo eixo Y
    fig.update_layout(
        yaxis=dict(title="Participantes"),
        yaxis2=dict(
            title="% acumulado",
            overlaying="y",
            side="right",
            range=[0, 100]
        ),
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)
# =========================
# RODAPÉ
# =========================
st.divider()
st.subheader('Autora do projeto')
st.write("Cristiane Lopes de Assis")
