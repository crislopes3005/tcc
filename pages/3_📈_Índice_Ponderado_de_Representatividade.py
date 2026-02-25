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
Aplicação do Índice Ponderado de Representatividade com agregação linear,
permitindo simular cenários alternativos de priorização baseados em
critérios de vulnerabilidade socioeconômica.
""")

st.divider()

# =========================
# DEFINIÇÃO DOS PESOS
# =========================
st.sidebar.header("⚖️ Pesos das Características")

peso_pbf = st.sidebar.slider("Programa Bolsa Família", 0.0, 5.0, 2.0)
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

    # Programa Bolsa Família (robusto)
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
# ESCOLHA DO EIXO DE ORDENAÇÃO
# =========================

st.subheader("Configuração do Ranking")

soma_pesos = (
    peso_pbf + peso_renda + peso_raca +
    peso_gpte + peso_regiao + peso_sexo + peso_idade
)

criterio = st.radio(
    "Escolha o eixo de ordenação:",
    ["Automático", "Votos", "Índice (IPR)"],
    horizontal=True
)

if criterio == "Automático":
    if soma_pesos == 0:
        criterio_final = "votos"
    else:
        criterio_final = "IPR"
elif criterio == "Votos":
    criterio_final = "votos"
else:
    criterio_final = "IPR"

st.markdown(f"**Eixo aplicado:** {criterio_final}")

st.divider()

# =========================
# RANKINGS BASE
# =========================

ranking_votos = df.sort_values(by="votos", ascending=False).reset_index(drop=True)
ranking_votos["pos_votos"] = ranking_votos.index + 1

ranking_ipr = df.sort_values(by="IPR", ascending=False).reset_index(drop=True)
ranking_ipr["pos_ipr"] = ranking_ipr.index + 1

df_rank = df.merge(
    ranking_votos[["id_x", "pos_votos"]],
    on="id_x"
).merge(
    ranking_ipr[["id_x", "pos_ipr"]],
    on="id_x"
)

df_rank["Δ posição"] = df_rank["pos_votos"] - df_rank["pos_ipr"]

# Ordenação dinâmica
df_rank = df_rank.sort_values(by=criterio_final, ascending=False)

df_rank.index = range(1, len(df_rank) + 1)
df_rank.index.name = "Posição"

# =========================
# TABELA FINAL (COM EIXO)
# =========================

tabela_final = df_rank[
    ["titulo", "eixo", "votos", "IPR", "pos_votos", "Δ posição"]
].head(20)

# =========================
# ESTILIZAÇÃO
# =========================

def cor_delta(val):
    if val > 0:
        return "color: green; font-weight: bold;"
    elif val < 0:
        return "color: red; font-weight: bold;"
    else:
        return "color: gray;"

st.subheader("Ranking Comparativo")

st.dataframe(
    tabela_final.style
        .format({
            "IPR": "{:.2f}",
            "votos": "{:,.0f}"
        })
        .background_gradient(subset=["IPR"], cmap="Blues")
        .background_gradient(subset=["votos"], cmap="Greys")
        .applymap(cor_delta, subset=["Δ posição"]),
    use_container_width=True
)

st.divider()

# =========================
# RESUMO ANALÍTICO
# =========================

subiram = (df_rank["Δ posição"] > 0).sum()
cairam = (df_rank["Δ posição"] < 0).sum()

col1, col2 = st.columns(2)

with col1:
    st.metric("Propostas que subiram no ranking", subiram)

with col2:
    st.metric("Propostas que caíram no ranking", cairam)

st.markdown("""
### Interpretação

A variação de posição evidencia o impacto da incorporação de critérios
socioeconômicos na priorização das propostas.

Quando nenhum peso é aplicado, a ordenação reproduz a lógica majoritária
baseada exclusivamente em votos. Ao ativar pesos, observa-se alteração
na hierarquia das propostas, permitindo simular cenários de priorização
orientados por equidade e vulnerabilidade social.
""")

st.divider()
st.subheader("Autora do projeto")
st.write("Cristiane Lopes de Assis")
