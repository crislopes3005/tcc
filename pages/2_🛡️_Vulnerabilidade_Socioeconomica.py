# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title='Participantes Socioeconomicamente Vulneráveis',
    page_icon='📊',
    layout='wide'
)

# =========================
# USAR BASE DA PÁGINA PRINCIPAL
# =========================
if "df" not in st.session_state:
    st.warning("Nenhuma base foi carregada. Acesse a página principal primeiro.")
    st.stop()

df = st.session_state["df"]

# =========================
# FILTROS SIDEBAR (REPLICADOS)
# =========================
st.sidebar.header("🔎 Filtros")

df_filtrado = df.copy()

escolha = st.sidebar.selectbox(
    "Deseja filtrar os resultados?",
    ['Não', 'Sim']
)

if escolha == 'Sim':

    # Processo
    lista_processos = df['processo'].dropna().unique().tolist()
    lista_processos.insert(0, "Marcar Todos")

    processo_selecionado = st.sidebar.selectbox(
        "Selecione um processo:",
        lista_processos
    )

    if processo_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[
            df_filtrado['processo'] == processo_selecionado
        ]

    # Estado da proposta
    lista_status = df_filtrado['state'].dropna().unique().tolist()
    lista_status.insert(0, "Marcar Todos")

    status_selecionado = st.sidebar.selectbox(
        "Selecione o estado da proposta:",
        lista_status
    )

    if status_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[
            df_filtrado['state'] == status_selecionado
        ]

    # Cluster
    lista_cluster = df_filtrado['cluster_k3'].dropna().unique().tolist()
    lista_cluster.insert(0, "Marcar Todos")

    cluster_selecionado = st.sidebar.selectbox(
        "Selecione a classificação do proponente:",
        lista_cluster
    )

    if cluster_selecionado != "Marcar Todos":
        df_filtrado = df_filtrado[
            df_filtrado['cluster_k3'] == cluster_selecionado
        ]

# =========================
# FILTRO DE VULNERABILIDADE
# =========================

df_vulneraveis = df_filtrado[
    df_filtrado['cadunico'].astype(str).str.strip().str.lower() == 'cadastrado'
].copy()

df_vulneraveis = df_vulneraveis.drop_duplicates(subset='id_autor')


# =========================
# TÍTULO
# =========================
st.markdown('# Análise dos Participantes Socioeconomicamente Vulneráveis')

st.write("""
<div style="text-align: justify">

Esta seção apresenta a caracterização socioeconômica dos participantes
identificados como cadastrados no CadÚnico ou beneficiários do Programa
Bolsa Família, considerando os filtros aplicados.

</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

total_participantes = df_filtrado['id_autor'].nunique()
total_vulneraveis = df_vulneraveis['id_autor'].nunique()

with col1:
    st.subheader("Participantes vulneráveis")
    st.metric("", total_vulneraveis)

with col2:
    percentual = round((total_vulneraveis / total_participantes) * 100, 2) if total_participantes > 0 else 0
    st.subheader("Percentual sobre o total filtrado")
    st.metric("", f"{percentual}%")

st.divider()

if df_vulneraveis.empty:
    st.warning("Nenhum participante vulnerável encontrado para os filtros aplicados.")
    st.stop()

# =========================
# SEÇÃO ANALÍTICA
# =========================

st.divider()

# =========================
# 1️⃣ PIRÂMIDE ETÁRIA (FAIXA + SEXO)
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Estrutura Etária por Gênero

A pirâmide permite visualizar a distribuição etária
dos participantes vulneráveis, comparando homens e mulheres.

A análise evidencia possíveis concentrações geracionais
na população cadastrada no CadÚnico.
""")

with col_grafico:

    df_idade = df_vulneraveis.dropna(subset=["faixaEtaria", "sex_final"])

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
# 2️⃣ GRUPO FAMILIAR (BARRA HORIZONTAL)
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Grupo Populacional Tradicional ou Específico (GPTE)

A distribuição evidencia a presença de grupos
historicamente vulnerabilizados.

Destacam-se povos indígenas e comunidades quilombolas.
""")

with col_grafico:

    contagem = df_vulneraveis["gpte"].value_counts().reset_index()
    contagem.columns = ["Grupo", "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=True)

    contagem["cor"] = contagem["Grupo"].apply(
        lambda x: "#5B7C99" if x in ["Indígena", "Quilombola"] else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        y="Grupo",
        x="Participantes",
        orientation="h",
        color="cor",
        color_discrete_map="identity",
        text="Participantes"
    )

    fig.update_layout(showlegend=False)
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# =========================
# 3️⃣ OCUPAÇÃO (BARRA HORIZONTAL)
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Perfil de Ocupação

A distribuição socioocupacional permite avaliar
o grau de institucionalização da participação.

Destacam-se categorias com possível maior
proximidade com o setor público.
""")

with col_grafico:

    contagem = df_vulneraveis["ocupacao_grupo"].value_counts().reset_index()
    contagem.columns = ["Ocupacao", "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=True)

    contagem["cor"] = contagem["Ocupacao"].apply(
        lambda x: "#5B7C99" if x in ["servidor_publico", "empresa_publica"] else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        y="Ocupacao",
        x="Participantes",
        orientation="h",
        color="cor",
        color_discrete_map="identity",
        text="Participantes"
    )

    fig.update_layout(showlegend=False)
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)
