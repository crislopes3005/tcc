# =========================
# IMPORTS
# =========================
import streamlit as st
import pandas as pd
import matplotlib.colors as mcolors

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
## O que é o Índice Ponderado de Representatividade?

O Índice Ponderado de Representatividade (IPR) é uma ferramenta de simulação
que permite testar diferentes critérios de priorização das propostas.

Enquanto a ordenação tradicional considera apenas o número de votos,
o IPR incorpora características socioeconômicas dos proponentes,
como renda, raça/cor, pertencimento a grupos tradicionais,
região, sexo e idade.

O objetivo não é substituir o critério majoritário,
mas demonstrar como a inclusão de critérios de equidade
pode alterar a hierarquia final das propostas.
""")
st.markdown("""
## Como aplicar o índice?

1. Utilize os controles na barra lateral para definir o peso
   de cada característica socioeconômica.
   
2. Quanto maior o peso atribuído, maior será a influência
   daquela característica na pontuação final.

3. Se todos os pesos forem definidos como zero,
   a ordenação será feita apenas pelo número de votos.

4. Caso algum peso seja ativado, o ranking passará
   a considerar os critérios de vulnerabilidade definidos.

5. É possível escolher manualmente o eixo de ordenação
   entre votos e índice, permitindo comparar os cenários.
""")
st.markdown("""
## Como interpretar os resultados?

- A coluna **IPR** mostra a pontuação obtida a partir
  dos critérios selecionados.

- A coluna **Δ posição** indica quanto a proposta subiu (▲)
  ou caiu (▼) no ranking em relação à ordenação por votos.

- Se uma proposta sobe no ranking,
  significa que ela é apresentada por grupos
  com maior vulnerabilidade segundo os critérios escolhidos.

- Se ela cai, significa que seu desempenho depende mais
  do volume de votos do que das características socioeconômicas.

Assim, o IPR permite simular diferentes cenários de política pública,
comparando uma lógica puramente majoritária com uma lógica orientada
por equidade social.
""")

# =========================
# FILTROS
# =========================
st.sidebar.header("🔎 Filtros")

df_filtrado = df.copy()

lista_processos = df["processo"].dropna().unique().tolist()
lista_processos.insert(0, "Todos")

processo_selecionado = st.sidebar.selectbox(
    "Selecione o processo:",
    lista_processos
)

if processo_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["processo"] == processo_selecionado]

st.divider()

# =========================
# PESOS
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
# FUNÇÃO IPR
# =========================
def calcular_ipr(row):

    score = 0

    valor_pbf = row.get("familiaBeneficiariaPBF")
    if pd.notnull(valor_pbf):
        if str(valor_pbf).strip().lower() in ["true", "sim", "1"]:
            score += peso_pbf

    if row.get("faixaRendaFamiliarPerCapita") in [
        "De 0 até R$ 109",
        "De R$ 109,01 até R$ 218"
    ]:
        score += peso_renda

    if row.get("racaCor") in ["Preta", "Parda", "Indígena"]:
        score += peso_raca

    if row.get("gpte") not in [0, "000", None, "Nenhuma"]:
        score += peso_gpte

    if row.get("regiao") in ["NO", "NE", "Norte", "Nordeste"]:
        score += peso_regiao

    if row.get("sex_final") == "Feminino":
        score += peso_sexo

    idade = row.get("idade_final")
    if isinstance(idade, (int, float)) and idade <= 29:
        score += peso_idade

    return score


df_filtrado["IPR"] = df_filtrado.apply(calcular_ipr, axis=1)


# =========================
# ESCOLHA DO EIXO
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
    criterio_final = "votos" if soma_pesos == 0 else "IPR"
elif criterio == "Votos":
    criterio_final = "votos"
else:
    criterio_final = "IPR"

st.markdown(f"**Eixo aplicado:** {criterio_final}")

st.divider()

# =========================
# RANKINGS BASE
# =========================
ranking_votos = df_filtrado.sort_values(by="votos", ascending=False).reset_index(drop=True)
ranking_votos["pos_votos"] = ranking_votos.index + 1

ranking_ipr = df_filtrado.sort_values(by="IPR", ascending=False).reset_index(drop=True)
ranking_ipr["pos_ipr"] = ranking_ipr.index + 1

df_rank = df_filtrado.merge(
    ranking_votos[["id_y", "pos_votos"]],
    on="id_y"
).merge(
    ranking_ipr[["id_y", "pos_ipr"]],
    on="id_y"
)

df_rank["Δ posição"] = df_rank["pos_votos"] - df_rank["pos_ipr"]

df_rank = df_rank.sort_values(by=criterio_final, ascending=False)
df_rank.index = range(1, len(df_rank) + 1)
df_rank.index.name = "Posição"

# =========================
# TABELA FINAL
# =========================
tabela_final = df_rank[
    ["titulo", "processo", "eixo", "votos", "IPR", "pos_votos", "Δ posição"]
].head(20).copy()

# =========================
# SETAS Δ
# =========================
def seta_delta(valor):
    if valor > 0:
        return f"▲ {valor}"
    elif valor < 0:
        return f"▼ {abs(valor)}"
    else:
        return "—"

tabela_final["Δ posição"] = tabela_final["Δ posição"].apply(seta_delta)

# =========================
# CORES Δ
# =========================
def cor_delta(val):
    if "▲" in str(val):
        return "color: #2E7D5A; font-weight: bold;"
    elif "▼" in str(val):
        return "color: #B04A4A; font-weight: bold;"
    else:
        return "color: #6E6E6E;"

# =========================
# COLORMAP PERSONALIZADO
# =========================
custom_blue = mcolors.LinearSegmentedColormap.from_list(
    "custom_blue",
    ["#FFFFFF", "#5B7C99"]
)

# =========================
# TABELA ESTILIZADA
# =========================
st.subheader("Ranking Comparativo")

st.dataframe(
    tabela_final.style
        .format({
            "IPR": "{:.2f}",
            "votos": "{:,.0f}"
        })
        .background_gradient(subset=["IPR"], cmap=custom_blue)
        .background_gradient(subset=["votos"], cmap="Greys")
        .applymap(cor_delta, subset=["Δ posição"]),
    use_container_width=True
)

st.divider()

# =========================
# RESUMO
# =========================
subiram = (df_rank["Δ posição"] > 0).sum()
cairam = (df_rank["Δ posição"] < 0).sum()

col1, col2 = st.columns(2)

with col1:
    st.metric("Propostas que subiram no ranking", subiram)

with col2:
    st.metric("Propostas que caíram no ranking", cairam)

