import streamlit as st
from google import genai
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
 
# Carrega as variáveis de ambiente necessárias para a execução
load_dotenv() 

# st.cache_resource garante que o Streamlit execute isso APENAS UMA VEZ
@st.cache_resource
def setup_logging():
    """Configures the logging system with file rotation."""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_handler = RotatingFileHandler(
        "logs/app.log", 
        maxBytes=1024 * 1024 * 5, 
        backupCount=3,
        encoding='utf-8'
    )
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    
    logger = logging.getLogger("ChatBot")
    logger.setLevel(logging.INFO)
    
    # Limpa handlers antigos caso o Streamlit tente recriar por algum motivo
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(log_handler)
    logger.addHandler(logging.StreamHandler())
    return logger

# Inicializa o logger com segurança contra duplicações
logger = setup_logging()

# Inicializa o cliente do Gemini
# O SDK busca automaticamente a variável GEMINI_API_KEY no seu arquivo .env
client = genai.Client()

# Title
st.write("# ChatBot with AI")

if not "messages" in st.session_state:
    st.session_state["messages"] = []

# Text input
input = st.chat_input()

# Renderiza o histórico na tela
for message in st.session_state.messages:
    # Mapeia "model" para "assistant" ou mantém "ai" para o Streamlit renderizar o ícone correto
    role_display = "assistant" if message["role"] == "model" else "user"
    st.chat_message(role_display).write(message["content"])

if input:
    # 1. Mostra e salva a mensagem do usuário
    st.chat_message("user").write(input)
    st.session_state.messages.append({"role": "user", "content": input})
    
    # Loga a entrada do usuário
    logger.info(f"Usuário enviou uma mensagem. Tamanho do histórico atual: {len(st.session_state.messages)}")
    
    # 2. Prepara o histórico no formato que o Gemini espera
    # O Gemini precisa que as mensagens alternem entre "user" e "model"
    gemini_history = []
    for msg in st.session_state.messages:
        gemini_history.append(
            genai.types.Content(
                role=msg["role"],
                parts=[genai.types.Part.from_text(text=msg["content"])]
            )
        )
        
    # 3. Define o modelo (ex: gemini-2.5-flash) vindo do .env ou direto no código
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    try:
        logger.info(f"Chamando a API do Gemini usando o modelo: {model_name}")
        
        # 4. Cria a sessão de chat enviando o histórico atualizado
        chat = client.chats.create(
            model=model_name, 
            history=gemini_history
        )
        
        # 5. Envia a nova mensagem do usuário dentro do contexto do chat
        response = chat.send_message(input)
        ai_response = response.text
        
        # Log de sucesso (Se quiser monitorar custos, pode logar o uso de tokens aqui se disponível na response)
        logger.info("Resposta recebida com sucesso da API do Gemini.")
        
        # 6. Mostra e salva a resposta da IA
        st.chat_message("assistant").write(ai_response)
        st.session_state.messages.append({"role": "model", "content": ai_response})
        
    except Exception as e:
        # Se der erro (ex: falta de internet, chave inválida, erro na API), o log captura
        logger.error(f"Erro ao chamar a API do Gemini: {str(e)}", exc_info=True)
        st.error("Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente mais tarde.")
    