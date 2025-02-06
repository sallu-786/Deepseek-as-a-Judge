import os
import streamlit as st
from litellm import completion
LLAMA="ollama/llama3.1"
DS="ollama/deepseek-r1:14b"
model = DS
    
def response_chatgpt_judge(message, input_documents, response):
    judge_prompt = f"""
    You are an evaluator for a question-answering system.
    Evaluate whether the response adequately answers the user's question based on the retrieved document.
    
    User Message: "{message}"
    Retrieved Document: "{input_documents}"
    AI Response: "{response}"
    Your Reasoning should be:

    Your reply should strictly follow this format:
    **Reasoning:** <Your feedback>
    **Marks:** <0-100>


    Your Marks should be:
    - 0-69 if the response is incomplete, incorrect, or lacks support from the Retrieved Document. 
    - 70-100 if the response expertly answers the question with regards to Retrieved Document information.Be strict in marking


    Example:
    **Reasoning:**: The assistant correctly identifies information is missing but continues to answer and fabricates facts. 
    **Marks:** 47  
  
        """
    messages = [{"role": "system", "content": judge_prompt}]


    try:
        response = completion(model=model, messages=messages, temperature=0)
        return {
            "answer": response.choices[0].message.content if response.choices else None,
            
        }
    except Exception as e:
        st.error(f"LLM-Judge could not run: {str(e)}")
        return None
    

def parse_feedback(response):
    """
    Parse model response to extract reasoning and score.
    """
    try:
        # Split into lines and clean up
        lines = [line.strip() for line in response.split('\n') if line.strip()]

        critique = None
        marks = None

        for i, line in enumerate(lines):
            if line.startswith("**Reasoning:**"):
                critique = lines[i].replace("**Reasoning:**", "").strip()
            elif line.startswith("**Marks:**"):
                marks = lines[i].replace("**Marks:**", "").strip()

        # Remove style tag if present
        if critique and "<userStyle>" in critique:
            critique = critique.split("<userStyle>")[0].strip()
        return critique, int(marks)

    except Exception as e:
        print(f"Error parsing Judge response: {e}")
        return None, None
