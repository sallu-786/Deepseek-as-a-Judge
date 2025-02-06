import streamlit as st
from dotenv import load_dotenv
from utils.generate_embeddings import retriever,handle_file_upload
from utils.get_response import response_chatgpt_az
from utils.judge import response_chatgpt_judge,parse_feedback

# Configuration
load_dotenv()
USER_NAME = "user"
ASSISTANT_NAME = "assistant"


def reset_conversation():
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        st.session_state.pop("messages", None)

def main():

    with open('css/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    st.markdown(
        '''
        <div id="root">
            <h1 class="title">DeepSeek As a Judge</h1>
           
        </div>
        ''', 
        unsafe_allow_html=True
    )


    # File Upload Sidebar option
    with st.sidebar:
        
        st.session_state.file = st.file_uploader("Upload File 📂", accept_multiple_files=False, type=['pdf', 'docx', 'pptx', 'xlsx', 'csv', 'txt'])
        send_button = st.button("submit", key="send_button")

        if send_button and st.session_state.file:
            try:                  
                text_chunks = handle_file_upload([st.session_state.file])
                if text_chunks:
                    st.session_state.text_chunks = text_chunks
                    st.session_state.file_name = st.session_state.file.name
            except Exception as e:
                st.error(f"File Processing Failed {e}")

    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    with st.sidebar:
        rst = st.button("Clear Chat🗑️", key="reset_button")
        if rst:
                st.session_state.chat_log = []

    for message in st.session_state.chat_log:
        with st.chat_message(message["role"]):
            if "content" in message:
                content = message["content"]
                if isinstance(content, str):
                    st.write(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            st.write(item["text"])
                        else:
                            st.write(item)

    message = st.chat_input("Enter your message here")

    if message:
        try:
            st.session_state.judge = False
            st.session_state.critique=""
            st.session_state.try_no=1
            st.session_state.least_bad_ans_marks=0
            st.session_state.least_bad_ans = ""

            with st.chat_message(USER_NAME):
                st.write(message)
            
            
            if "text_chunks" in st.session_state:
                
                reranked_results = retriever(st.session_state.text_chunks, message)
                doc_texts = [{"content": doc.page_content, "metadata": doc.metadata} for doc in reranked_results]
                
                while st.session_state.judge is False and st.session_state.try_no<=3:
                    
                    with st.spinner("Generating Response..."):
                        response = response_chatgpt_az(message, doc_texts,st.session_state.critique, chat_history=st.session_state.chat_log)
                        
                        st.write(f"***Try:***   {st.session_state.try_no}")
                        st.write(f"***LLM Response:***   {response["answer"]}")

                    with st.spinner("Getting Feedback..."):
                        judge_response = response_chatgpt_judge(message, doc_texts, response)
                        critique, marks=parse_feedback(judge_response["answer"])
                        
                        st.write(f"***Judge Feedback:*** {critique}")
                        st.write(f"***Marks:***          {marks}")

                        st.session_state.critique=critique
                        st.session_state.try_no+=1
                        st.session_state.judge = True if marks>=70 else False

                        if st.session_state.judge is False:
                            st.write(f"***Result:***          Fail")
                            if st.session_state.least_bad_ans_marks<marks:
                                st.session_state.least_bad_ans_marks=marks
                                st.session_state.least_bad_ans=response["answer"]
                        else:
                            st.write(f"***Result:***          Pass")
                            st.session_state.least_bad_ans=response["answer"]

                
        
            with st.chat_message(ASSISTANT_NAME):
                        assistant_msg = st.session_state.least_bad_ans
                        st.write(assistant_msg)
                        
            # st.session_state.chat_log.append({"role": "user", "content": [{"type": "text", "text": message}]})
            # st.session_state.chat_log.append({"role": "assistant", "content": [{"type": "text", "text": assistant_msg}]})
            st.session_state.chat_log.append({"role": "user", "content": message})
            st.session_state.chat_log.append({"role": "assistant", "content": assistant_msg})

        except Exception as e:
            st.error(f"Error Occurred {e}")

if __name__=="__main__":
    main()