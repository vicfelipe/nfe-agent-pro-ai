import streamlit as st
import requests
import json

LLM_GATEWAY_URL = "http://core_service:8002/llm/chat/invoke"

st.title("Chat Interface para Testar LLM")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite sua mensagem aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {"prompt": prompt}

    try:
        response = requests.post(LLM_GATEWAY_URL, json=payload)
        response.raise_for_status()
        try:
            llm_response_data = response.json()
            assistant_response = llm_response_data["response"]

        except json.JSONDecodeError:
            assistant_response = f"Erro ao decodificar JSON da resposta do LLM Gateway. Resposta recebida: {response.text}"
        except Exception as e:
            assistant_response = f"Erro ao processar resposta do LLM: {str(e)}"

    except requests.exceptions.RequestException as e:
        assistant_response = f"Erro ao conectar com o LLM Gateway: {str(e)}"
    except Exception as e:
        assistant_response = f"Ocorreu um erro inesperado: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)