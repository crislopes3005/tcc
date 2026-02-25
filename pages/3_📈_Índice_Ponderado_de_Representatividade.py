# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Índice Ponderado de Representatividade",
    page_icon="📈",
    layout="wide"
)

# =========================
# BASE DA PÁGINA PRINCIPAL
# =========================
if "df" not in st.session_state:
    st.warning("Carregue a base na página principal primeiro.")
    st.stop()

df = st.session_state["df"].copy()

st.title("Aplicação do Índice Ponderado de Representatividade")

st.markdown("""
Aplicação do Índice Ponderado de Representatividade com modelo
multiplicativo, inspirado na lógica de agregação do IPOA.
""")

st.divider()

# =========================
# DEFINIÇÃO DOS PESOS
# =========================
st.sidebar.header("⚖️ Pesos das Características")

peso_pbf = st.sidebar.slider("Programa Bolsa Família (Cadastrado)", 0.0, 5.0, 2.0)
peso_renda = st.sidebar.slider("Baixa Renda per capita", 0.0, 5.0, 2.0)
peso_raca = st.sidebar.slider("Raça Preta/Parda/Indígena", 0.0, 5.0, 1.0)
peso_gpte = st.sidebar.slider("GPTE", 0.0, 5.0, 1.5)
peso_regiao = st.sidebar.slider("Região Norte/Nordeste", 0.0, 5.0, 1.0)
peso_sexo = st.sidebar.slider("Sexo feminino", 0.0, 5.0, 1.0)
peso_idade = st.sidebar.slider("Jovens (até 29 anos)", 0.0, 5.0, 1.0)

# =========================
# FUNÇÃO DE CÁLCULO
# =========================
def calcular_ipr(row):

    score = 0

    # Programa Bolsa Família
    valor_pbf = row.get("familiaBeneficiariaPBF")
    if pd.notnull(valor_pbf):
        if str(valor_pbf).strip().lower() in ["true", "sim", "1"]:
            score += peso_pbf

    # Baixa renda
    if row.get("faixaRendaFamiliarPerCapita") in [
        "De 0 até R$ 109",
        "De R$ 109,01 até R$ 218"
    ]:
        score += peso_renda

    # Raça
    if row.get("racaCor") in ["Preta", "Parda", "Indígena"]:
        score += peso_raca

    # GPTE
    if row.get("gpte") not in [0, "000", None, "Nenhuma"]:
        score += peso_gpte

    # Região
    if row.get("regiao") in ["NO", "NE", "Norte", "Nordeste"]:
        score += peso_regiao

    # Sexo feminino
    if row.get("sex_final") == "Feminino":
        score += peso_sexo

    # Jovens até 29
    idade = row.get("idade_final")
    if isinstance(idade, (int, float)) and idade <= 29:
        score += peso_idade

    return score

df["IPR"] = df.apply(calcular_ipr, axis=1)

st.divider()

# =========================
# RANKING
# =========================
st.subheader("Ranking de Propostas pelo Índice Multiplicativo")

df_ranking = df.sort_values(
    by="IPR",
    ascending=False
)[
    ["id_x", "titulo", "votos", "IPR"]
]

st.dataframe(df_ranking.head(20), use_container_width=True)

st.divider()

# =========================
# COMPARAÇÃO COM VOTOS
# =========================
st.subheader("Comparação: Votos vs Índice")

col1, col2 = st.columns(2)

with col1:
    st.write("Top 10 por votos")
    st.dataframe(
        df.sort_values(by="votos", ascending=False)[
            ["id_x", "titulo", "votos"]
        ].head(10),
        use_container_width=True
    )

with col2:
    st.write("Top 10 por IPR")
    st.dataframe(
        df.sort_values(by="IPR", ascending=False)[
            ["id_x", "titulo", "IPR"]
        ].head(10),
        use_container_width=True
    )

st.divider()

st.markdown("""
### Interpretação

O índice ponderado permite simular mecanismos alternativos de priorização
baseados em critérios de vulnerabilidade socioeconômica.

A alteração dos pesos modifica a hierarquia das propostas,
permitindo avaliar diferentes cenários de política pública.
""")

st.divider()
st.subheader("Autora do projeto")
st.write("Cristiane Lopes de Assis")
