import os
import sys
import numpy as np
from scipy.spatial import distance
from dotenv import load_dotenv
load_dotenv()

class HistoryManager:
    # Manages the history of conversation
    def __init__(self, logger):
        self.logger = logger
        self.history = []
        self.history = []
        self.NUM_NEAREST_PAIRS_FROM_HISTORY = int(os.getenv("NUM_NEAREST_PAIRS_FROM_HISTORY"))
        self.NUM_LAST_PAIRS_FROM_HISTORY = int(os.getenv("NUM_LAST_PAIRS_FROM_HISTORY"))
        self.THRESHOLD_PAIRS_SENT = float(os.getenv("THRESHOLD_PAIRS_SENT"))

    def add_message_to_history(self, question, answer, embedding):
        self.history.append({
            "question": question,
            "answer": answer,
            "embedding": embedding.tolist()
        })

    def select_from_history(self, question_embedding: np.ndarray) -> str:
        def join_question_answer(item):
            return ' '.join([item["question"], item["answer"]])

        try:
            # Forming latest content
            latest_memory_content = ""
            if len(self.history) > self.NUM_LAST_PAIRS_FROM_HISTORY:
                if self.NUM_LAST_PAIRS_FROM_HISTORY:
                    latest_items = self.history[-self.NUM_LAST_PAIRS_FROM_HISTORY:]
                else:
                    latest_items = []
            else:
                latest_items = self.history
            for item in latest_items:
                content = join_question_answer(item)
                latest_memory_content += f"{content}\n"
            self.logger.debug(f"-->Latest memory content: {latest_memory_content}", )

            # Forming nearest content
            nearest_memory_content = ''
            nearest_items = {}
            for i, item in enumerate(self.history):
                if i < (len(self.history) - self.NUM_LAST_PAIRS_FROM_HISTORY):
                    cos_distance = distance.cosine(question_embedding[0], item["embedding"][0])
                    if cos_distance < self.THRESHOLD_PAIRS_SENT:  # hyperparameter
                        nearest_items[i] = (item, cos_distance)
            self.logger.info(f"The system have found  {len(nearest_items)} nearest_items in previos conversation")
            sort_nearest_items = dict(sorted(nearest_items.items(), key=lambda x: x[1][1]))

            for i, value in enumerate(sort_nearest_items.values()):
                if i == self.NUM_NEAREST_PAIRS_FROM_HISTORY:
                    break
                nearest_memory_content += join_question_answer(value[0])
            self.logger.debug(f"-->Nearest memory content: {nearest_memory_content}")
            chosen_history = ' '.join([latest_memory_content, nearest_memory_content])
            return chosen_history
        except AttributeError:
            return '', ''
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error(f"An {exc_type} occurred: {e} in file {fname} at line {exc_tb.tb_lineno}")
            return '', ''

