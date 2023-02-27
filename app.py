import streamlit as st 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import networkx as nx
import streamlit.components.v1 as components

import plotly.graph_objects as go
from networkx.algorithms import community


from pyvis.network import Network
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('rslp')
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import kneighbors_graph



## CONFIGURAÇÕES DE PÁGINA PADRÃO
st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)



## FUNCIONS AUXILIARES

# Função para selecionar a quantidade de linhas do dataframe
def mostra_qntd_linhas(dataframe):

    qntd_linhas = st.sidebar.slider('Selecione a quantidade de linhas que deseja mostrar na tabela', min_value = 1, max_value = 10, step = 1)

    st.write(dataframe.head(qntd_linhas).style.format(subset = ['Sigla']))

st.image('logocrai.jpg', width=100)

st.title('Olá CRAI 2023 :sunglasses:')


## Criação de TABS

tab1,tab2, tab3 = st.tabs(['Base','Redes','GrafosFO'])



with tab1: 
    
    # importando os dados
    dados = pd.read_csv('TesesFOResumo2.csv', sep=';')

    # Títulos dentro da TAB
    st.title('Banco de Teses - FOUSP - Últimos 5 anos\n')
    st.write('Nesse projeto vamos analisar as teses de Doutorado da FOUSP')

    # filtros para a tabela
    opcao_1 = st.sidebar.checkbox('Mostrar tabela')
    if opcao_1:

        st.sidebar.markdown('## Filtro para a tabela')

        #categorias = list(dados['SIGLA'].unique())
        categorias = list(['ODB','ODD', 'ODE', 'ODM', 'ODP','ODS'])
        
        categorias.append('Todas')

        categoria = st.sidebar.selectbox('Selecione a SIGLA do departamento para apresentar na tabela', options = categorias)

        contarOdonto = dados.query("Sigla in ['ODB','ODD', 'ODE', 'ODM', 'ODP','ODS']")
        
        if categoria != 'Todas':
            df_categoria = dados.query('Sigla == @categoria')
            mostra_qntd_linhas(df_categoria)      
        else:
            mostra_qntd_linhas(dados)


        st.title('Navegar pela base de dados')

        # Usando componente AgGrid para navegar pela BASE DE DADOS
        
        gb = GridOptionsBuilder.from_dataframe(dados)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Selecione") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
            dados,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            theme='alpine', #Add theme color to the table
            enable_enterprise_modules=True,
            height=350, 
            width='100%',
            reload_data=True
        )

        #dados = grid_response['dados']
        #selected = grid_response['selected_rows'] 
        #df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df



            #dados.query('SIGLA'== categorias)

        st.write('Pesquisas da FOUSP - Últimos 5 anos')
                    
        st.write(contarOdonto['Sigla'].value_counts())
        
        
with tab2:
    # Read dataset (CSV)
    df_interact = pd.read_csv('fo_tri_2.CSV',sep=";",encoding='utf-8')

    # Set header title
    st.title('Visualização de Grafos por interação - SOMENTE TESTE')

    # Define list of selection options and sort alphabetically
    drug_list = ['laser', 'dente', 'microscopia', 'hiv',
                'gesso', 'molar', 'corante', 'tecido']
    drug_list.sort()

    # Implement multiselect dropdown menu for option selection (returns a list)
    selected_drugs = st.multiselect('Selecionar áreas', drug_list)

    # Set info message on initial site load
    if len(selected_drugs) == 0:
        st.text('Escolha uma palavra para começar ')

    # Create network graph when user selects >= 1 item
    else:
        df_select = df_interact.loc[df_interact['word1'].isin(selected_drugs) | \
                                    df_interact['word2'].isin(selected_drugs)] #| \
                                    # df_interact['word3'].isin(selected_drugs)]
        df_select = df_select.reset_index(drop=True)

        # Create networkx graph object from pandas dataframe
        G = nx.from_pandas_edgelist(df_select, source='word1', target='word2', edge_attr='word3')

        # Initiate PyVis network object
        drug_net = Network(
                        height='400px',
                        width='100%',
                        bgcolor='#222222',
                        font_color='white'
                        )

        # Take Networkx graph and translate it to a çççgraph format
        drug_net.from_nx(G)

        # Generate network with specific layout settings
        drug_net.repulsion(
                            node_distance=420,
                            central_gravity=0.33,
                            spring_length=110,
                            spring_strength=0.10,
                            damping=0.95
                        )

        # Save and read graph as HTML file (on Streamlit Sharing)
        try:
            path = '/tmp'
            drug_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Save and read graph as HTML file (locally)
        except:
            path = '/html_files'
            drug_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Load HTML file in HTML component for display on Streamlit page
        components.html(HtmlFile.read(), height=435)

    # Footer
    #st.markdown(
    #    """
    #    <br>
    #    <h6><a href="https://github.com/kennethleungty/Pyvis-Network-Graph-Streamlit" target="_blank">GitHub Repo</a></h6>
    #    <h6><a href="https://kennethleungty.medium.com" target="_blank">Medium article</a></h6>
    #    <h6>Disclaimer: This app is NOT intended to provide any form of medical advice or recommendations. Please consult your doctor or pharmacist for professional advice relating to any drug therapy.</h6>
    #    """, unsafe_allow_html=True
    #    )


with tab3:

    st.title('Dados da rede ficarão aqui!')
    
  
  
  

