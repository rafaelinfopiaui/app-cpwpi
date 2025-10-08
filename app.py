import streamlit as st
import pandas as pd
import re
import os
import time
from wordcloud import WordCloud, STOPWORDS
import matplotlib
matplotlib.use('Agg') # Define o modo não-interativo
import matplotlib.pyplot as plt
import base64

# --- 1. Configuração da Página e Estilo ---
st.set_page_config(
    page_title="Análise de Sentimentos CPWPI 2025",
    page_icon="🤖",
    layout="wide",
)

# CSS para o tema da Campus Party
st.markdown("""
<style>
    .stApp { background-color: #0A1A33; color: #FFFFFF; }
    h1, h2, h3 { color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #1E293B; }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; padding-left: 5rem; padding-right: 5rem; }
    .stButton > button {
        border: 2px solid #EC008C; color: #FFFFFF; background-color: #EC008C;
        border-radius: 8px;
    }
    .stButton > button:hover {
        border-color: #D1E038; color: #0A1A33; background-color: #D1E038;
    }
    .stTextArea > div > div > textarea {
        background-color: #1E2B3B; color: #FFFFFF; border: 1px solid #EC008C;
    }
    [data-testid="stProgressBar"] > div > div {
        background-image: linear-gradient(to right, #EC008C, #D1E038);
    }
    .logo-container {
        display: flex;
        justify-content: center; /* Alinha horizontalmente */
        align-items: center;    /* Alinha verticalmente */
        gap: 2rem;              /* Espaço entre as logos */
        padding-top: 2rem;      /* Espaço acima das logos */
    }
</style>
""", unsafe_allow_html=True)

# Função para converter imagens para Base64 de forma segura
def get_image_as_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- 2. Funções do Mock Model e Análise de Texto ---
def predict_mock_sentiment(texto_input):
    if not isinstance(texto_input, str) or not texto_input.strip(): return "Indefinido", 0.0
    texto = texto_input.lower()
    palavras_positivas = ['bom', 'ótimo', 'excelente', 'incrível', 'maravilhoso', 'adorei', 'gostei', 'recomendo', 'perfeito', 'fantástico', 'amei', 'sucesso', 'parabéns', 'top', 'show', 'curti']
    palavras_negativas = ['ruim', 'péssimo', 'horrível', 'terrível', 'odeio', 'detestei', 'lixo', 'fraude', 'enganação', 'não gostei', 'decepcionado', 'decepção', 'frustrante', 'esperava mais', 'lamentável', 'desagradável', 'deixou a desejar', 'problema', 'atraso', 'quebrado', 'falha', 'erro', 'defeito', 'complicado', 'não funciona', 'fraco', 'mal feito', 'desorganizado', 'confuso', 'difícil', 'pouco']
    if any(palavra in texto for palavra in palavras_positivas): return "Positivo", 0.95
    if any(palavra in texto for palavra in palavras_negativas): return "Negativo", 0.92
    return "Neutro", 0.85

# --- 3. Conexão com a Planilha Google (Método CSV) ---
SHEET_ID = "1J9x2c5js1FvVrLl5juaQSJPXn_tIvmsv5ee6slwqjbk"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        dados = pd.read_csv(CSV_URL)
        dados.dropna(how='all', axis=1, inplace=True)
        dados.dropna(how='all', axis=0, inplace=True)
        if not dados.empty:
            dados.columns = ['Timestamp', 'Comentário']
        return dados[['Comentário']]
    except Exception as e:
        return pd.DataFrame(columns=['Comentário'])

# --- 4. Páginas da Aplicação ---

st.sidebar.title("🚀 Navegação")
pagina = st.sidebar.radio("Escolha uma página:", ["Dashboard ao Vivo", "Analisador Individual"])

if pagina == "Dashboard ao Vivo":
    if os.path.exists("banner_home-CPWeekendPiaui2-2.png"):
        st.image("banner_home-CPWeekendPiaui2-2.png")

    st.title("📊 Dashboard de Sentimentos ao Vivo")
    st.markdown("Veja em tempo real o que as pessoas estão a comentar sobre o evento!")

    if st.button("🔄 Atualizar Dados"):
        st.cache_data.clear()

    dados_comentarios = carregar_dados()

    if dados_comentarios.empty:
        st.info("Ainda não há comentários. Seja o primeiro a participar!")
    else:
        sentimentos = dados_comentarios['Comentário'].apply(lambda x: predict_mock_sentiment(x)[0])
        contagem_sentimentos = sentimentos.value_counts()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sentimento Geral")
            if not contagem_sentimentos.empty:
                # --- MUDANÇA IMPORTANTE: Mapeamento de Cores ---
                color_map = {'Positivo': '#28a745', 'Negativo': '#dc3545', 'Neutro': '#ffc107'}
                labels = contagem_sentimentos.index
                pie_colors = [color_map.get(label, '#808080') for label in labels]

                fig, ax = plt.subplots()
                fig.patch.set_alpha(0.0)
                ax.pie(contagem_sentimentos, labels=labels, autopct='%1.1f%%', startangle=90, colors=pie_colors, textprops={'color':"w"})
                ax.axis('equal')
                st.pyplot(fig)

        with col2:
            st.subheader("Nuvem de Palavras")
            texto_completo = " ".join(comentario for comentario in dados_comentarios['Comentário'] if isinstance(comentario, str))
            if texto_completo.strip():
                stopwords_pt = set(STOPWORDS)
                stopwords_pt.update(["pra", "pro", "tá", "né", "da", "de", "do", "na", "no", "uma", "um", "que", "se", "por"])
                wordcloud = WordCloud(stopwords=stopwords_pt, background_color=None, mode="RGBA", colormap="viridis", width=800, height=400).generate(texto_completo)
                fig_wc, ax_wc = plt.subplots()
                fig_wc.patch.set_alpha(0.0)
                ax_wc.imshow(wordcloud, interpolation='bilinear')
                ax_wc.axis("off")
                st.pyplot(fig_wc)

        st.markdown("---")
        st.subheader("Últimos Comentários")
        st.dataframe(dados_comentarios.tail(10), use_container_width=True)


elif pagina == "Analisador Individual":
    unicet_logo = get_image_as_base64("unicet_white.png")
    cp_logo = get_image_as_base64("CPWeekend_Piaui.png")
    engcia_logo = get_image_as_base64("ENG-CIA logo.png")

    if unicet_logo and cp_logo and engcia_logo:
        st.markdown(f'''
        <div class="logo-container">
            <img src="data:image/png;base64,{unicet_logo}" width="200">
            <img src="data:image/png;base64,{cp_logo}" width="150">
            <img src="data:image/png;base64,{engcia_logo}" width="150">
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.title("🧠 Classificador de Sentimentos em Português")
    st.subheader("Teste o nosso modelo com qualquer texto que desejar.")

    texto_usuario = st.text_area(
        "Insira um texto para análise:",
        "A Campus Party Weekend Piauí é um evento incrível, mal posso esperar!",
        height=150,
        label_visibility="collapsed"
    )

    if st.button("Analisar Sentimento"):
        with st.spinner('A analisar o texto...'):
            time.sleep(1)
            sentimento, confianca = predict_mock_sentiment(texto_usuario)

        st.markdown("---")
        st.write("### Resultado da Análise:")
        # --- MUDANÇA IMPORTANTE: Cores alinhadas ---
        cor_sentimento = "#28a745" if sentimento == "Positivo" else "#dc3545" if sentimento == "Negativo" else "#ffc107"
        st.markdown(f"*Sentimento Identificado:* <span style='color:{cor_sentimento}; font-weight: bold;'>{sentimento}</span>", unsafe_allow_html=True)
        st.progress(float(confianca), text=f"Confiança: {confianca:.1%}")

        with st.expander("Ver Plano de Ação Sugerido", expanded=True):
            if sentimento == "Positivo": st.markdown("- *Prioridade:* Baixa\n- *Recomendações:* Agradecer o feedback.")
            elif sentimento == "Negativo": st.markdown("- *Prioridade:* Alta\n- *Recomendações:* Contacto urgente, analisar causa raiz.")
            else: st.markdown("- *Prioridade:* Média\n- *Recomendações:* Monitorizar a conversa.")

# --- 5. Barra Lateral ---
st.sidebar.markdown("---")
st.sidebar.success("Modelo de Demonstração Ativo!")
#st.sidebar.info("Este é um projeto educacional desenvolvido para fins de demonstração.")

st.sidebar.markdown("### Sobre o Projeto")
st.sidebar.markdown(f"*Desenvolvimento:* Equipe do Projeto de Extensão do Curso de Bacharelado em Engenharia de Computação da UNICET, com o objetivo de aplicar as técnica de Deep Learning e Machine Learning para análise de sentimentos.")
st.sidebar.markdown("\n### Equipe de Desenvolvimento \n- Rafael Oliveira \n- Ailton Medeiros \n- Laís Eulálio \n- Antônio Wilker \n- Isaac Bruno \n- Paula Iranda")
st.sidebar.markdown("\n### Docente Orientador \n- Prof. Dr. Artur Felipe da Silva Veloso")
