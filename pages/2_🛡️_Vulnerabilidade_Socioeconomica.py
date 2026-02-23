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
# BASE DA PÁGINA PRINCIPAL
# =========================
if "df" not in st.session_state:
    st.warning("Nenhuma base foi carregada. Acesse a página principal primeiro.")
    st.stop()

df = st.session_state["df"]

# =========================
# FILTROS
# =========================
st.sidebar.header("🔎 Filtros")

df_filtrado = df.copy()

escolha = st.sidebar.selectbox(
    "Deseja filtrar os resultados?",
    ['Não', 'Sim']
)

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
Esta seção apresenta a caracterização socioeconômica dos participantes
identificados como cadastrados no CadÚnico.
""")

st.divider()

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

total_participantes = df_filtrado['id_autor'].nunique()
total_vulneraveis = df_vulneraveis['id_autor'].nunique()

with col1:
    st.metric("Participantes vulneráveis", total_vulneraveis)

with col2:
    percentual = round((total_vulneraveis / total_participantes) * 100, 2) if total_participantes > 0 else 0
    st.metric("Percentual sobre o total filtrado", f"{percentual}%")

st.divider()

if df_vulneraveis.empty:
    st.warning("Nenhum participante vulnerável encontrado.")
    st.stop()

# ==========================================================
# 1️⃣ PIRÂMIDE ETÁRIA
# ==========================================================
col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Estrutura Etária por Gênero

A pirâmide permite comparar a distribuição de homens e mulheres
entre os participantes vulneráveis.
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
    fig.update_xaxes(showticklabels=False, showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================================================
# FUNÇÃO BARRA HORIZONTAL
# ==========================================================
def barra_horizontal(df_base, coluna, destaques, titulo, descricao):

    col_texto, col_grafico = st.columns([1, 2])

    with col_texto:
        st.markdown(f"### {titulo}\n\n{descricao}")

    with col_grafico:
        contagem = df_base[coluna].value_counts().reset_index()
        contagem.columns = ["Categoria", "Participantes"]
        contagem = contagem.sort_values("Participantes", ascending=True)

        contagem["cor"] = contagem["Categoria"].apply(
            lambda x: "#5B7C99" if x in destaques else "#D3D3D3"
        )

        fig = px.bar(
            contagem,
            y="Categoria",
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

# ==========================================================
# 2️⃣ PBF
# ==========================================================
col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Beneficiários do PBF

Destaca-se a proporção de beneficiários do Programa Bolsa Família.
""")

with col_grafico:
    contagem = df_vulneraveis["familiaBeneficiariaPBF"].value_counts().reset_index()
    contagem.columns = ["PBF", "Participantes"]

    cores = {True: "#5B7C99", False: "#D3D3D3"}

    fig = px.pie(contagem, names="PBF", values="Participantes", hole=0.4)

    fig.update_traces(
        marker=dict(colors=[cores.get(v, "#CCCCCC") for v in contagem["PBF"]]),
        textinfo="percent+label"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================================================
# 3️⃣ RAÇA
# ==========================================================
barra_horizontal(
    df_vulneraveis,
    "racaCor",
    ["Preta", "Parda", "Indígena"],
    "Raça/Cor",
    "Destacam-se grupos historicamente vulnerabilizados."
)

# ==========================================================
# 4️⃣ GPTE
# ==========================================================
barra_horizontal(
    df_vulneraveis,
    "gpte",
    ["Indígena", "Quilombola"],
    "Grupo Familiar (GPTE)",
    "Evidencia presença de grupos tradicionais."
)

# ==========================================================
# 5️⃣ OCUPAÇÃO
# ==========================================================
barra_horizontal(
    df_vulneraveis,
    "ocupacao_grupo",
    ["servidor_publico", "empresa_publica"],
    "Ocupação",
    "Perfil socioocupacional dos participantes."
)

# ==========================================================
# 6️⃣ RENDA
# ==========================================================
barra_horizontal(
    df_vulneraveis,
    "faixaRendaFamiliarPerCapita",
    ["De 0 até R$ 109", "De R$ 109,01 até R$ 218"],
    "Renda Familiar per capita",
    "Destacam-se faixas de maior vulnerabilidade."
)

# ==========================================================
# 7️⃣ REGIÃO
# ==========================================================
barra_horizontal(
    df_vulneraveis,
    "regiao",
    ["N", "NE", "Norte", "Nordeste"],
    "Região",
    "Regiões historicamente associadas a maior vulnerabilidade."
)
