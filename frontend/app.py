import streamlit as st
import requests

st.set_page_config(page_title="Repo Explainer", page_icon="🤖", layout="wide")

st.title("🤖 GitHub Repo Explainer Agent")
st.markdown("Ask questions about any GitHub repository.")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for Repository Ingestion
with st.sidebar:
    st.header("Repository Configuration")
    repo_url = st.text_input("Enter GitHub Repo URL")
    level = st.selectbox("Explanation Level", ["beginner", "intermediate", "expert"])
    
    if st.button("Ingest Repository"):
        if repo_url:
            with st.spinner("Cloning and processing repository... This may take a moment."):
                try:
                    res = requests.post("http://localhost:8000/ingest", params={"repo_url": repo_url})
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"{data.get('status')} ({data.get('documents_processed', 0)} chunks)")
                        # Clear chat history when new repo is ingested
                        st.session_state.messages = []
                    else:
                        st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")
        else:
            st.warning("Please enter a valid URL.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.code(source)

# Accept user input
if prompt := st.chat_input("Ask a question about the repository..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    "http://localhost:8000/query",
                    params={"query": prompt, "level": level}
                )
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "No answer found.")
                    sources = data.get("sources", [])
                    
                    message_placeholder.markdown(answer)
                    
                    if sources:
                        with st.expander("Sources"):
                            for source in sources:
                                st.code(source)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                else:
                    st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")