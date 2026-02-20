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
Esta página aplica um Índice Ponderado de Representatividade (IPR),
estruturado em dimensões, inspirado na metodologia do Índice de Priorização
de Objetos de Auditoria (IPOA) :contentReference[oaicite:1]{index=1}.
""")

st.divider()

# =========================
# DEFINIÇÃO DOS PESOS
# =========================
st.sidebar.header("⚖️ Pesos das Dimensões")

peso_socio = st.sidebar.slider("Peso Dimensão Socioeconômica", 0.0, 5.0, 2.0)
peso_etnico = st.sidebar.slider("Peso Dimensão Étnico-Racial", 0.0, 5.0, 1.0)
peso_territorial = st.sidebar.slider("Peso Dimensão Territorial", 0.0, 5.0, 1.0)
peso_familiar = st.sidebar.slider("Peso Dimensão Familiar", 0.0, 5.0, 1.0)

# =========================
# CÁLCULO DOS SUBÍNDICES
# =========================
def calcular_subindices(row):

    # ------------------------
    # 1️⃣ Dimensão Socioeconômica
    # ------------------------
    socio = 0

    if row.get("cadunico") == 'Cadastrado':
        socio += 1

    if row.get("faixaRendaFamiliarPerCapita") in ['De 0 até R$ 109', 'De R$ 109,01 até R$ 218']:
        socio += 1


    # ------------------------
    # 2️⃣ Dimensão Étnico-Racial
    # ------------------------
    etnico = 0

    if row.get("racaCor") in ['Preta','Parda','Indígena']:
        etnico += 1

    if row.get("gpte_codigo") not in [0, "000", None, 'Nenhuma']:
        etnico += 1

    # ------------------------
    # 3️⃣ Dimensão Territorial
    # ------------------------
    territorial = 0

    if row.get("regiao") in ["NO", "NE"]:
        territorial += 1

    # ------------------------
    # 4️⃣ Dimensão Familiar
    # ------------------------
    familiar = 1 if row.get("quantidadePessoasFamilia", 0) >= 5 else 0

    return socio, etnico, territorial, familiar


df[["IS", "IE", "IT", "IF"]] = df.apply(
    lambda row: pd.Series(calcular_subindices(row)),
    axis=1
)

# =========================
# MODELO 1 — SOMA PONDERADA
# =========================
df["IPR_soma"] = (
    df["IS"] * peso_socio +
    df["IE"] * peso_etnico +
    df["IT"] * peso_territorial +
    df["IF"] * peso_familiar
)

# =========================
# MODELO 2 — MULTIPLICATIVO
# (inspirado no IPOA)
# =========================
df["IPR_multiplicativo"] = (
    (df["IE"] * peso_etnico +
     df["IT"] * peso_territorial +
     df["IF"] * peso_familiar)
    * (df["IS"] * peso_socio)
)

st.divider()

# =========================
# RANKING
# =========================
st.subheader("Ranking de Propostas")

modelo_escolhido = st.radio(
    "Escolha o modelo do índice:",
    ["IPR_soma", "IPR_multiplicativo"]
)

df_ranking = df.sort_values(
    by=modelo_escolhido,
    ascending=False
)[
    ["id_x", "titulo", "votos", modelo_escolhido]
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
    st.write(f"Top 10 por {modelo_escolhido}")
    st.dataframe(
        df.sort_values(by=modelo_escolhido, ascending=False)[
            ["id_x", "titulo", modelo_escolhido]
        ].head(10),
        use_container_width=True
    )

st.divider()

# =========================
# INTERPRETAÇÃO
# =========================
st.markdown("""
### Interpretação

O modelo de soma ponderada permite agregar dimensões de vulnerabilidade
de forma linear.

O modelo multiplicativo atribui efeito amplificador à dimensão
socioeconômica, alterando potencialmente a hierarquia das propostas.

A comparação entre modelos permite avaliar o impacto metodológico
da escolha da fórmula de agregação.
""")

st.divider()
st.subheader("Autora do projeto")
st.write("Cristiane Lopes de Assis")
