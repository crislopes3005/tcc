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
# CARREGAR DADOS (mesma lógica da página principal)
# =========================
if "df" not in st.session_state:
    st.warning("Nenhuma base foi carregada. Volte à página principal.")
    st.stop()

df = st.session_state["df"]


# =========================
# FILTRO: APENAS VULNERÁVEIS
# =========================
df_vulneraveis = df[
    (df['cadunico'] == 'Cadastrado')
]

# Remover duplicidade de participantes
df_vulneraveis = df_vulneraveis.drop_duplicates(subset='id_autor')

# =========================
# TÍTULO
# =========================
st.markdown('# Análise dos Participantes Socioeconomicamente Vulneráveis')

st.write("""
<div style="text-align: justify">

Esta seção apresenta a caracterização socioeconômica dos participantes considerados
em situação de vulnerabilidade social, identificados a partir do CadÚnico ou como
beneficiários do Programa Bolsa Família.

</div>
""", unsafe_allow_html=True)

st.divider()

# =========================
# KPI
# =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Número de participantes vulneráveis")
    st.metric("", df_vulneraveis['id_autor'].nunique())

with col2:
    percentual = round(
        (df_vulneraveis['id_autor'].nunique() /
         df['id_autor'].nunique()) * 100, 2
    )
    st.subheader("Percentual sobre o total de participantes")
    st.metric("", f"{percentual}%")

st.divider()

# =========================
# FUNÇÃO GRÁFICO
# =========================
def grafico_contagem(df, coluna, titulo):

    df_temp = df.dropna(subset=[coluna])

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
