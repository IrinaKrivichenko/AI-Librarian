import gradio as gr
from RAG.RAG import RAG

list_of_path_to_data = [ r"./data/database_docx/"]
rag = RAG(list_of_path_to_data)

def chatbot_function(input_text, _):
       response = rag.get_answer(input_text)
       return response

gr.ChatInterface(chatbot_function).launch(server_name="0.0.0.0", server_port=7860)
