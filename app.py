import streamlit as st
from rag_core import answer_stream

st.title("Assistant de recherche sur le diabète de type 1")
st.caption("Les réponses proviennent uniquement de l'article de recherche. Ceci n'est pas un avis médical.")

if "history" not in st.session_state:
    st.session_state.history = []
for role, text in st.session_state.history:
    st.chat_message(role).write(text)

if q := st.chat_input("Posez votre question sur le diabète de type 1..."):
    st.chat_message("user").write(q)
    with st.chat_message("assistant"):
        a = st.write_stream(answer_stream(q))
    st.session_state.history += [("user", q), ("assistant", a)]