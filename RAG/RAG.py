import os
from typing import Optional

from RAG.DataManager import DataManager
from RAG.HistoryManager import HistoryManager
from RAG.LoggerSetup import LoggerSetup
from RAG.OpenAIHandler import OpenAIHandler
from dotenv import load_dotenv
load_dotenv()

class RAG:
   def __init__(self, list_of_path_to_data):
        self.openai_handler = OpenAIHandler()
        self.logger = LoggerSetup()
        self.history_manager = HistoryManager(self.logger)
        self.NUM_CHUNKS_SENT = int(os.getenv("NUM_CHUNKS_SENT"))
        self.data_managers = []
        for path_to_data in list_of_path_to_data:
            data_manager = DataManager(self.NUM_CHUNKS_SENT, path_to_data, self.logger)
            self.data_managers.append(data_manager)

   def get_prompt(self, question: str, file_name: Optional[str] = None) -> list:
       question_embedding = self.openai_handler.get_text_embedding(question)
       history_content = self.history_manager.select_from_history(question_embedding=question_embedding)
       context = ""
       num_chunks_left = self.NUM_CHUNKS_SENT
       for data_manager in self.data_managers:
            curr_context, chunks_found = data_manager.find_chunk_in_database(question_embedding=question_embedding)
            context = context + curr_context
            num_chunks_left = num_chunks_left - chunks_found
            if num_chunks_left <= 0: break
       system_content = f"Always start with the source (name of the file) you have used to answer the question. " \
                        f"Use the provided chunks delimited by triple quotes to answer question. " \
                        f"Use the provided conversation context delimited by triple quotes to answer question if needed. " \
                        f"If you don't understand a question, don't guess, just ask to specify the answer.' " \
                        f"если ты считаешь , что в предоставленных чанках был рисунок , который может хорошо " \
                        "проилюстрировать вопрос пользователя, то добавь к ответу информацию " \
                        "' для лучшего понимания посмотрите рисунок {pic_name} в файле {file_name} номер чанка {chunk_number}'" \
                        f"Provided chunks: '''{context}'''. " \
                        f"Conversation context: '''{history_content}'''. " \
                        f"If the article does not provide the required information, please provide general recommendations or alternative sources upon user request."\
                        f"Answer in russian language"
       system_part = (
           {
               "role": "system",
               "content": system_content
           }
       )
       user_part = (
           {
               "role": "user",
               "content": question
           }
       )
       return [system_part, user_part]

   def get_answer(self, question: str,  file_name: Optional[str] = None) -> dict:
       question = question.lower()
       prompt = self.get_prompt(question=question)
       answer = self.openai_handler.get_answer(prompt)
       embedding = self.openai_handler.get_text_embedding(' '.join([question, answer]))
       self.history_manager.add_message_to_history(question, answer, embedding)
       return answer






