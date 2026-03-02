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
    st.metric("Número de propostas recebidas", df_filtrado['id_y'].count())

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
# CADÚNICO
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Participantes no CadÚnico

O destaque aos participantes cadastrados no CadÚnico tem como objetivo
evidenciar o grau de inclusão de grupos socioeconomicamente vulneráveis
nos processos participativos analisados.

Considerando que o CadÚnico é o principal instrumento de identificação
de famílias de baixa renda no Brasil, sua presença entre os participantes
constitui indicador relevante para avaliar se a participação social
alcança públicos historicamente sub-representados.
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
# PIRÂMIDE ETÁRIA COM %
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Estrutura Etária por Gênero

A visualização em formato de pirâmide permite analisar a composição
etária e de gênero dos participantes, identificando possíveis
concentrações geracionais e diferenças entre homens e mulheres.

A escolha desse formato facilita a comparação visual entre os sexos,
contribuindo para avaliar a diversidade demográfica da participação
e possíveis assimetrias na inclusão de determinados grupos.
""")

with col_grafico:

    df_idade = df_participantes.dropna(subset=["faixaEtaria", "sex_final"]).copy()

    contagem = (
        df_idade.groupby(["faixaEtaria", "sex_final"])
        .size()
        .reset_index(name="Participantes")
    )

    total = contagem["Participantes"].sum()
    contagem["Percentual"] = (contagem["Participantes"] / total * 100).round(1)

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

    contagem["label"] = (
        contagem["Participantes"].astype(str) +
        " (" + contagem["Percentual"].astype(str) + "%)"
    )

    fig = px.bar(
        contagem,
        y="faixaEtaria",
        x="valor_plot",
        color="sex_final",
        orientation="h",
        barmode="relative",
        text="label",
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
    
# =========================
# REGIÃO COM %
# =========================

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Participação Regional

A regiões Norte e Nordeste são destacadas por apresentarem,
historicamente, maiores indicadores de vulnerabilidade socioeconômica.

A análise territorial permite avaliar se os processos participativos
atingem de forma equilibrada diferentes regiões do país ou se há
concentração regional da participação, o que pode indicar desigualdades
no acesso às plataformas digitais e aos mecanismos de deliberação pública.
""")

with col_grafico:

    contagem = df_participantes["regiao"].value_counts().reset_index()
    contagem.columns = ["Regiao", "Participantes"]
    contagem = contagem.sort_values("Participantes", ascending=False)

    total = contagem["Participantes"].sum()
    contagem["Percentual"] = (contagem["Participantes"] / total * 100).round(1)

    contagem["label"] = (
        contagem["Participantes"].astype(str) +
        " (" + contagem["Percentual"].astype(str) + "%)"
    )

    contagem["cor"] = contagem["Regiao"].apply(
        lambda x: "#5B7C99" if x in ["N", "NE", "Norte","Nordeste"] else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        x="Regiao",
        y="Participantes",
        color="cor",
        color_discrete_map="identity",
        text="label"
    )

    fig.update_layout(
        showlegend=False,
        xaxis=dict(categoryorder="total descending")
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)

# =========================
# PERFIL DE OCUPAÇÃO 
# =========================

st.divider()

col_texto, col_grafico = st.columns([1, 2])

with col_texto:
    st.markdown("""
### Perfil de Ocupação

A distribuição ocupacional permite observar o perfil socioeconômico
dos participantes e identificar possíveis concentrações institucionais.

O destaque a servidores públicos e trabalhadores de empresas públicas
busca evidenciar a presença de grupos com maior proximidade ao Estado,
o que pode indicar maior familiaridade com mecanismos formais
de participação e influenciar o padrão de representatividade observado.
""")

with col_grafico:

    contagem = df_participantes["ocupacao_grupo"].value_counts().reset_index()
    contagem.columns = ["Ocupacao", "Participantes"]

    # 🔹 Ordenar decrescente (maior primeiro)
    contagem = contagem.sort_values("Participantes", ascending=True)

    total = contagem["Participantes"].sum()
    contagem["Percentual"] = (contagem["Participantes"] / total * 100).round(1)

    contagem["cor"] = contagem["Ocupacao"].apply(
        lambda x: "#5B7C99" if x in ["servidor_publico", "empresa_publica"]
        else "#D3D3D3"
    )

    fig = px.bar(
        contagem,
        y="Ocupacao",
        x="Participantes",
        orientation="h",
        color="cor",
        color_discrete_map="identity",
        text=contagem["Participantes"].astype(str) +
             " (" + contagem["Percentual"].astype(str) + "%)"
    )

    # 🔹 Aqui está o segredo para manter maior em cima
    fig.update_layout(
        showlegend=False,
        yaxis=dict(
            categoryorder="array",
            categoryarray=contagem["Ocupacao"]  # mantém a ordem exata
        )
    )

    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)
