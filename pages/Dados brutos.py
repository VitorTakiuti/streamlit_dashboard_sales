import streamlit as st
import requests
import pandas as pd
import time

# Memória cache para converter textos em csv.
@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')
# Função para mostrar a mensagem de sucesso após o download do arquivo, e depois de 5 segundos, a mensagem desaparece.
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Pequeno desafio feito para mostrar o poder do query, usando os filtros de cada coluna para filtrar os dados
# Filtragem de dados com método query
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'):
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete da venda'):
    frete = st.slider('Frete', 0,250, (0,250))
with st.sidebar.expander('Data da compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação da compra',1,5, value = (1,5))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# Após os filtros das colunas, criamos a variável query que vai ser igual à três aspas simples consecutivas, para criar uma string de várias linhas.
# Na primeira linha, escrevemos Produto in @produtos. Essa string indica que selecionaremos na variável produtos apenas os elementos escolhidos
# no multiselect da coluna "Produto". Vamos fazer isso para cada uma das colunas.
# Colocamos um and e uma barra invertida (\) para saltar uma linha e poder adicionar mais uma filtragem na query.
# A próxima filtragem será @preco[0] menor ou igual à coluna Preço que é menor ou igual à @preco[1]. Essa filtragem indica que selecionaremos 
# os valores da coluna "Preço", com os valores mínimo e máximo escolhidos no slider e armazenados na variável preco.
# Por fim, colocamos and seguido da barra invertida para realizar a filtragem da coluna de "Data da Compra"
# Na próxima linha, escrevemos @data_compra[0] é menor ou igual à coluna Data da Compra que é menor ou igual à @data_compra[1]. Lembre-se que 
# o nome da coluna deve ser escrito com a letra "D" e "C" em maiúsculas.
#Como o nome da coluna "Data da Compra" contém espaços, devemos colocar o nome entre crases. A crase é o acento inverso do acento agudo 
# (aperte "Shift" e selecione a tecla de acento agudo).
# Assim, a filtragem selecionará os valores da coluna "Data da Compra", com os valores mínimo e máximo escolhidos no slider e armazenados na variável data_compra

query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedores and \
`Local da compra` in @local_compra and \
@avaliacao[0]<= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]

st.dataframe(dados_filtrados)

# Mostrando a quantidade de linhas e colunas da tabela filtrada, usando a função shape, onde o primeiro elemento é a quantidade de linhas e o segundo elemento é a quantidade de colunas.
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')
# Criando um botão para fazer o download da tabela filtrada em formato csv, usando a função download_button, onde o primeiro argumento é o texto do botão, 
# o segundo argumento é a função que converte a tabela em csv, o terceiro argumento é o nome do arquivo e o quarto argumento é o tipo do arquivo.
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
