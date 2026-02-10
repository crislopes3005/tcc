#importando as bibliotecas

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import locale
import plotly.io as pio
import requests
from geojson_rewind import rewind
import json
from PIL import Image
from streamlit_option_menu import option_menu


#carregando os dados
df = pd.read_csv('df_final.csv')

st.set_page_config(
    page_title='Análise de representatividade - Plataforma Brasil Participativo 🗣️ 🤝',
    page_icon='📊',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'http://www.meusite.com.br',
        'Report a bug': "http://www.meuoutrosite.com.br",
        'About': "Esse app foi desenvolvido no MBA de Ciências de Dados e Inteligência Artificial Aplicadas."
    }
)

st.markdown('# Análise de representatividade - Plataforma Brasil Participativo 🗣️ 🤝')


#criando as caixas de seleção
escolha = st.sidebar.selectbox("Deseja filtrar os resultados?", ['Não', 'Sim'])
df_filtrado = df
if escolha == 'Sim':
    lista_processos = df['processo'].unique().tolist()
    lista_processos.insert(0, "Marcar Todos")
    processo_selecionado = st.sidebar.selectbox("Selecione um processo:", lista_processos)

    if processo_selecionada != "Marcar Todos":
        df_filtrado = df[df['processo'] == processo_selecionado]

        lista_status = df_filtrado['state'].unique().tolist()
        lista_status.insert(0, "Marcar Todos")
        status_selecionado = st.sidebar.selectbox("Selecione o estado da proposta:", lista_status)

        if status_selecionado != "Marcar Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == status_selecionado]

            lista_cluster = df_filtrado['cluster_k3'].unique().tolist()
            lista_cluster.insert(0, "Marcar Todos")
            cluster_selecionado = st.sidebar.selectbox("Selecione a classificação do proponente:", lista_cluster)

            if cluster_selecionado != "Marcar Todos":
                df_filtrado = df_filtrado[df_filtrado['cluster_k3'] == cluster_selecionado]


#criando um espaço entre as visualizações
st.text("")

#criando o texto explicativo
st.write(
    """
    <div style="text-align: justify">
<p> Para análise da representatividade nos processos de participação hospedados na Plataforma Brasil Participativo, foram selecionados os processos do Plano Clima Participativo e do Novo Plano Nacional de Cultura. 

</p> Para cada um dos processos é possível avaliar o perfil socioeconômico dos proponentes pelo conjunto de propostas recebido e pelo conjunto de propostas que foram ou não selecionadas para análise das respectivas pastas. 

</p> É possível também analisar o perfil socioeconômico pela classificação dos proponentes, a saber: participantes de baixa mobilização, participantes altamente engajados e participantes socioeconomicamente vulneráveis. 

</p> Já na aba "índice de representatividade é possivel ....". </p>
</div>    
    """,
    unsafe_allow_html=True
)


#criando um espaço entre as visualizações
st.text("")

#criando os cartões com os valores totais 

col1, col2, col3= st.columns(3)

with col1 :
    st.write(
        """
        <h2 style="font-size: 24px;">Número de propostas recebidas</h2>
        """,
        unsafe_allow_html=True
    )
    st.write("{:,}".format(df_filtrado['id_x'].value_counts())
    
with col2 :
    st.write(
        """
        <h2 style="font-size: 24px;">Total de proponentes</h2>
        """,
        unsafe_allow_html=True
    )
    st.write("{:,}".format(df_filtrado['id_autor'].nunique())

with col3 :
    st.write(
        """
        <h2 style="font-size: 24px;">Valor médio do benefício por família</h2>
        """,
        unsafe_allow_html=True
    )
    st.write(df_filtrado[df_filtrado['state'] == 'Analisado']['state'].nunique())

st.text("")
#criando divisão na página
st.divider()
    
# Garante 1 linha por participante
df_participantes = df.drop_duplicates(subset='id_autor')

# =====================================================
# FUNÇÃO AUXILIAR PARA GRÁFICOS
# =====================================================
def grafico_contagem(df, coluna, titulo):
    contagem = (
        df[coluna]
        .value_counts()
        .reset_index()
        .rename(columns={'index': coluna, coluna: 'Participantes'})
    )

    fig = px.bar(
        contagem,
        x=coluna,
        y='Participantes',
        text='Participantes',
        title=titulo
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Nº de participantes",
        showlegend=False
    )

    return fig

# =====================================================
# LINHA 1 – SEXO | FAIXA ETÁRIA
# =====================================================
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        grafico_contagem(
            df_participantes,
            'Sexo',
            'Participantes por sexo'
        ),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        grafico_contagem(
            df_participantes,
            'faixaEtaria',
            'Participantes por faixa etária'
        ),
        use_container_width=True
    )

# =====================================================
# LINHA 2 – ESTADO | REGIÃO
# =====================================================
col3, col4 = st.columns(2)

with col3:
    st.plotly_chart(
        grafico_contagem(
            df_participantes,
            'regiao',
            'Participantes por região'
        ),
        use_container_width=True
    )

with col4:
    st.plotly_chart(
        grafico_contagem(
            df_participantes,
        'estado',
        'Participantes por estado'
        ),
        use_container_width=True
    )

# =====================================================
# LINHA 3 – OCUPAÇÃO/CADUNICO
# =====================================================
col5, col6 = st.columns(2)

with col5:
    st.plotly_chart(
        grafico_contagem(
            df_participantes,
            'ocupacao_grupo',
            'Participantes por tipo de ocupação'
        ),
        use_container_width=True
    )

with col4:
    st.plotly_chart(
        grafico_contagem(
            df_participantes,
        'cadunico',
        'Participantes cadastrados no CadÚnico'
        ),
        use_container_width=True
    )
#criando um espaço entre as visualizações
st.text("")

st.subheader('**Autora do projeto**') 

st.write(
    """
    <div style="text-align: justify">

<p> - Cristiane Lopes de Assis 

    """,
    unsafe_allow_html=True
)