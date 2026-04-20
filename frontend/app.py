import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="GenAI E-Commerce Assistant", layout="wide")

st.title("🚀 Rocket Lab: Agente GenAI de E-Commerce")
st.markdown("---")

st.sidebar.header("Sugestões de Perguntas")
examples = [
    "Top 10 produtos mais vendidos",
    "Receita total por categoria de produto",
    "Quantidade de pedidos por status",
    "% de pedidos entregues no prazo por estado dos consumidores",
    "Média de avaliação geral dos pedidos",
    "Média de avaliação por vendedor (top 10)",
    "Estados com maior volume de pedidos e maior ticket médio",
    "Estados com maior atraso",
    "Produtos mais vendidos por estado",
    "Categorias com maior taxa de avaliação negativa"
]

for ex in examples:
    if st.sidebar.button(ex):
        st.session_state.query = ex

user_input = st.text_input("Faça uma pergunta sobre a base de dados:", placeholder="Ex: Qual a categoria com mais avaliações negativas?", value=st.session_state.get("query", ""))

if st.button("Analisar") or user_input:
    if not user_input:
        st.warning("Por favor, digite uma pergunta.")
    else:
        with st.spinner("O Agente está consultando o banco de dados..."):
            try:
                response = requests.post("http://localhost:8000/api/analyze", json={"prompt": user_input})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Análise Concluída!")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("📊 Insights")
                        st.write(data["analysis"])
                        
                        with st.expander("Ver Pensamento do Agente"):
                            st.info(data["thought"])
                            st.code(data["sql"], language="sql")
                    
                    with col2:
                        st.subheader("🔢 Dados Brutos")
                        if data["results"]:
                            df = pd.DataFrame(data["results"])
                            st.dataframe(df)
                            
                            if len(df.columns) >= 2:
                                try:
                                    # Tenta inferir um gráfico (se houver pelo menos uma coluna numérica)
                                    num_cols = df.select_dtypes(include=['number']).columns
                                    cat_cols = df.select_dtypes(include=['object']).columns
                                    
                                    if len(num_cols) > 0 and len(cat_cols) > 0:
                                        fig = px.bar(df, x=cat_cols[0], y=num_cols[0], title=f"{num_cols[0]} por {cat_cols[0]}")
                                        st.plotly_chart(fig, use_container_width=True)
                                except:
                                    pass
                        else:
                            st.write("Nenhum dado retornado para esta consulta.")
                            
                else:
                    st.error(f"Erro na API: {response.json().get('detail', 'Erro desconhecido')}")
            except Exception as e:
                st.error(f"Não foi possível conectar ao backend. Certifique-se de que o uvicorn está rodando.\nErro: {e}")

st.markdown("---")
