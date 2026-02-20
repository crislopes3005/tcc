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
# GRÁFICOS REORGANIZADOS
# =========================

def grafico_barra_destacado(df_base, coluna, destaque_lista, titulo):
    contagem = df_base[coluna].value_counts().reset_index()
    contagem.columns = [coluna, "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=False)

    contagem["cor"] = contagem[coluna].apply(
        lambda x: "#5B7C99" if x in destaque_lista else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x=coluna,
        y="Participantes",
        color="cor",
        color_discrete_map="identity",
        text="Participantes"
    )

    fig.update_layout(
        title=titulo,
        showlegend=False,
        xaxis=dict(categoryorder="total descending")
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


def grafico_pizza_destacado(df_base, coluna, destaque_valor, titulo):
    contagem = df_base[coluna].value_counts().reset_index()
    contagem.columns = [coluna, "Participantes"]

    cores = []
    for valor in contagem[coluna]:
        if valor == destaque_valor:
            cores.append("#5B7C99")
        else:
            cores.append("#D3D3D3")

    fig = px.pie(
        contagem,
        names=coluna,
        values="Participantes",
        hole=0.4
    )

    fig.update_traces(
        marker=dict(colors=cores),
        textinfo="percent+label"
    )

    fig.update_layout(title=titulo)

    st.plotly_chart(fig, use_container_width=True)


# 1️⃣ Beneficiários PBF (pizza)
grafico_pizza_destacado(
    df_vulneraveis,
    "familiaBeneficiariaPBF",
    True,
    "Beneficiários do PBF"
)

# 2️⃣ Sexo (pizza)
grafico_pizza_destacado(
    df_vulneraveis,
    "sex_final",
    "Feminino",
    "Sexo"
)

# 3️⃣ Raça/Cor
grafico_barra_destacado(
    df_vulneraveis,
    "racaCor",
    ["Preta", "Parda", "Indígena"],
    "Raça/Cor"
)

# 4️⃣ Grupo Familiar (GPTE)
grafico_barra_destacado(
    df_vulneraveis,
    "gpte",
    ["Indígena", "Quilombola"],
    "Grupo Familiar (GPTE)"
)

# 5️⃣ Ocupação
grafico_barra_destacado(
    df_vulneraveis,
    "ocupacao_grupo",
    ["nao_informado", "nao_especificado"],
    "Ocupação"
)

# 6️⃣ Renda per capita
grafico_barra_destacado(
    df_vulneraveis,
    "faixaRendaFamiliarPerCapita",
    ["De 0 até R$ 109", "De R$ 109,01 até R$ 218"],
    "Renda Familiar per Capita"
)

# 7️⃣ Região
grafico_barra_destacado(
    df_vulneraveis,
    "regiao",
    ["N", "NE", "Norte", "Nordeste"],
    "Região"
)

# 8️⃣ Faixa Etária
grafico_barra_destacado(
    df_vulneraveis,
    "faixaEtaria",
    ["25 a 44 anos"],
    "Faixa Etária"
)

# =========================
# RODAPÉ
# =========================
st.divider()
st.subheader('Autora do projeto')
st.write("Cristiane Lopes de Assis")
