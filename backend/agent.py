import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def answer_query(db, query, level="beginner"):
    llm = get_llm()
    retriever = db.as_retriever(search_kwargs={"k": 5})

    # Retrieve relevant docs first
    retrieved_docs = retriever.invoke(query)
    context = format_docs(retrieved_docs)

    system_content = (
        f"You are a senior software engineer explaining a codebase.\n"
        f"Explain the answer at a {level} level.\n"
        "Use the following retrieved context to answer the question.\n"
        "If you don't know the answer, say so.\n"
        "Reference the source files when relevant.\n\n"
        f"Context:\n{context}"
    )

    # Pass messages directly — avoids LangChain template parsing
    # which breaks on curly braces in code (e.g. JSON, dicts, JS objects)
    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=query),
    ]

    response = llm.invoke(messages)
    answer = StrOutputParser().invoke(response)

    # Extract unique source files
    sources = list(set([
        doc.metadata.get("file", "Unknown") for doc in retrieved_docs
    ]))

    return answer, sources