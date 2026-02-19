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
# FUNÇÃO GRÁFICO
# =========================
def grafico_contagem(df_base, coluna, titulo):

    df_temp = df_base.dropna(subset=[coluna])

    contagem = df_temp[coluna].value_counts().reset_index()
    contagem.columns = [coluna, 'Participantes']

    fig = px.bar(
        contagem,
        x=coluna,
        y='Participantes',
        text='Participantes',
        title=titulo
    )

    fig.update_traces(textposition='outside')

    fig.update_layout(
        height=500,
        margin=dict(t=80)
    )

    return fig


# =========================
# GRÁFICOS
# =========================
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'familiaBeneficiariaPBF', 'Beneficiários do PBF'),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'racaCor', 'Participantes por raça/cor'),
        use_container_width=True
    )

col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'gpte', 'Grupo populacional tradicional/específico'),
        use_container_width=True
    )

with col4:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'sex_final', 'Participantes por sexo'),
        use_container_width=True
    )

col5, col6 = st.columns(2)

with col5:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'ocupacao_grupo', 'Participantes por ocupação'),
        use_container_width=True
    )

with col6:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'regiao', 'Participantes por região'),
        use_container_width=True
    )

col7, col8 = st.columns(2)

with col7:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'faixaRendaFamiliarPerCapita', 'Renda familiar per capita'),
        use_container_width=True
    )

with col8:
    st.plotly_chart(
        grafico_contagem(df_vulneraveis, 'faixaEtaria', 'Participantes por faixa etária'),
        use_container_width=True
    )

# =========================
# RODAPÉ
# =========================
st.divider()
st.subheader('Autora do projeto')
st.write("Cristiane Lopes de Assis")
