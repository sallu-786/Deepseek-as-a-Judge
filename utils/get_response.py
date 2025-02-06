import streamlit as st
from litellm import completion
LLAMA="ollama/llama3.1"
DS="ollama/deepseek-r1:14b"
model = LLAMA


# Function to get response from LLM model (Chat-GPT-Azure)---------------------------------------------------


def response_chatgpt_az(message: str, input_documents, feedback="", chat_history: list = []):
    system_msg = (
            
           f"""You are a helpful Assistant named TB Chat.
           If some documents given to you, You always Answer the questions properly based on the provided document.
           Use the given feedback to improve upon the previous answer. If empty, just ignore it
           **Feedback:** {feedback}
           If the information is not in the documents or you can't find it, 
           then give your own information based answer after informing user. Don't hallucinate"""
        )

    messages = [{"role": "system", "content": system_msg}]

    # Add chat history
    for chat in chat_history[-4:]:
        if isinstance(chat, dict) and "role" in chat and "content" in chat:
            messages.append(chat)

    # Add user message
    messages.append({"role": "user", "content": message})

    # Add input documents
    for doc in input_documents:
        if isinstance(doc, dict) and "content" in doc:
            messages.append({"role": "user", "content": f"Document snippet:\n{doc['content']}"})

    try:
        response = completion(model=model, messages=messages, temperature=0)
        return {
            "answer": response.choices[0].message.content if response.choices else None,
            "sources": input_documents,
            
        }
    except Exception as e:
        st.error(f"Could not generate answer: {str(e)}")
        return None