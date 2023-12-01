import streamlit as st

import utils
from pages.large_language_models import LLM_CONFIG
from src.generative_ai.large_language_models import ChatbotRAG

loader = utils.PageConfigLoader(__file__)
loader.set_page_config(globals())

st_ss = st.session_state


def main():
    return
    chosen_model = st.selectbox(
        label="Large Language Model:",
        placeholder="Choose an option",
        options=LLM_CONFIG.keys(),
        index=0,
        on_change=utils.reset_session_state_key,
        kwargs={"key": "chatbot_rag"},
    )

    with st.sidebar:
        st.header(body="Chat parameters", divider="gray")
        selected_language = st_ss.setdefault(
            "language_widget", utils.LanguageWidget()
        ).selected_language
        lakera_activated = st_ss.setdefault(
            "lakera_widget", utils.LakeraWidget()
        ).lakera_activated

    if chosen_model:
        chatbot = st_ss.setdefault("chatbot_rag", ChatbotRAG(**LLM_CONFIG[chosen_model]))
        for message in chatbot.history:
            st.chat_message(message["role"]).write(message["content"])
    else:
        st.info("Select a model above", icon="ℹ️")

    if prompt := st.chat_input(
        placeholder=f"Chat with {chosen_model}!" if chosen_model else "",
        disabled=not chosen_model,
    ):
        st.chat_message("human").write(prompt)
        if lakera_activated:
            flag, response = utils.LakeraWidget.flag_prompt(prompt=prompt)
            if flag:
                st.warning(body="Prompt injection detected", icon="🚨")
                st.expander(label="LOGS").json(response)
        with st.chat_message("ai"):
            chatbot.ask(
                query=prompt,
                language=selected_language,
            )
