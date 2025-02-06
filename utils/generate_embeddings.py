from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from utils.file_format_handler import get_pdf_text,get_text,get_word_text,get_ppt_text,get_excel_text,get_csv_text
from langchain_ollama import OllamaEmbeddings
from langchain.retrievers import EnsembleRetriever
from dotenv import load_dotenv
import time
import streamlit as st
from langchain.schema import Document

load_dotenv()

embedding_model = "nomic-embed-text:latest"
#Handle multiple files
def get_file(files):
    if isinstance(files, list):
        text_chunks = []
        for file in files:
            filename = file.name 
            if filename.endswith('.pdf'):
                text_chunks.extend(get_pdf_text(file))
            elif filename.endswith('.txt'):
                text_chunks.extend(get_text(file))
            elif filename.endswith(('.docx', '.doc')):
                text_chunks.extend(get_word_text(file))
            elif filename.endswith(('.pptx', '.ppt')):
                text_chunks.extend(get_ppt_text(file))
            elif filename.endswith(('.xlsx', '.xls')):
                text_chunks.extend(get_excel_text(file))
            elif filename.endswith('.csv'):
                text_chunks.extend(get_csv_text(file))
            else: 
                raise ValueError(f"Unsupported file type: {filename}")
        
        return text_chunks
    
    #single file
    else:
        filename = files.name 
        if filename.endswith('.pdf'):
            return get_pdf_text(files)
        elif filename.endswith('.txt'):
            return get_text(files)
        elif filename.endswith(('.docx', '.doc')):
            return get_word_text(files)
        elif filename.endswith(('.pptx', '.ppt')):
            return get_ppt_text(files)
        elif filename.endswith(('.xlsx', '.xls')):
            return get_excel_text(files)
        elif filename.endswith('.csv'):
            return get_csv_text(files)
        else: 
            raise ValueError(f"Unsupported file type: {filename}")


def get_text_chunks(pages):  # divide text of file into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10, 
                                          length_function=len)
    chunks = []
    for text, page_number in pages:
        for chunk in text_splitter.split_text(text):
            chunks.append({"text": chunk, "page_number": page_number})
    return chunks



#Document Retriever-------------------------------------------------------------------------------------------- 
def retriever(text_chunks, query):
  
    embeddings = OllamaEmbeddings(model=embedding_model)
    documents = [Document(page_content=chunk['text'], metadata={'page': chunk['page_number']}) 
                 for chunk in text_chunks]

    vector_store = FAISS.from_documents(documents, embeddings)

    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    ensemble_retriever = EnsembleRetriever(
        retrievers=[faiss_retriever],
        weights=[1.0]  
    )
    final_result = ensemble_retriever.invoke(query)
    return final_result


# when file is uploaded by user, create new vector data for that file
def create_new_vector_db(file):
    with st.spinner("Creating vector data"):
        text = get_file(file)
        text_chunks = get_text_chunks(text)
    return text_chunks

def handle_file_upload(file):
    if file:
        text_chunks = create_new_vector_db(file)
        alert=st.success("Vector data created successfully.")
        time.sleep(2)
        alert.empty()
        return text_chunks

    else:                             
        pass
