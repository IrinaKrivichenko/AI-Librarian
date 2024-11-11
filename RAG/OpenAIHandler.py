# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
# https://tiktokenizer.vercel.app/?model=gpt-4-1106-preview
# https://platform.openai.com/tokenizer
import tiktoken
import os
import numpy as np
import faiss
from openai import OpenAI, AuthenticationError, OpenAIError
from dotenv import load_dotenv
load_dotenv()

class OpenAIHandler:
# Responsible for all communications with the OpenAI API including fetching embeddings and generating completions.

    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.EMBEDDING_MODEL = "text-embedding-3-large"
        self.GENERATIVE_MODEL = "gpt-4-turbo-2024-04-09"

    def get_text_embedding(self, text: str) -> np.array:
       # try:
           response = self.openai_client.embeddings.create(input=text, model=self.EMBEDDING_MODEL)
           # print(f"Сколько токенов расходуется на prompt модели {self.EMBEDDING_MODEL}: {response.usage.prompt_tokens}")
           embedding = response.data[0].embedding
           embedding = np.array(embedding)
           embedding = embedding.astype("float32")
           embedding = np.expand_dims(embedding, axis=0)
           faiss.normalize_L2(embedding)
           return embedding
       # except AuthenticationError:
       #     raise Exception("An AuthenticationError occurred. The API key used for authentication might be invalid.")
       # except OpenAIError:
       #     raise Exception("An OpenAIError occurred. There might be an issue with the connection.")
       # return embedding

    def get_answer(self, prompt, temperature=0, seed=42):
        response = self.openai_client.chat.completions.create(
            model=self.GENERATIVE_MODEL,
            messages=prompt,
            temperature=temperature,
            seed=seed,
        )
        # print(f"Сколько токенов расходуется на prompt модели {self.GENERATIVE_MODEL}:"
        #       f" {response.usage.prompt_tokens}")
        # print(f"Сколько токенов расходуется на completion модели {self.GENERATIVE_MODEL}:"
        #       f" {response.usage.completion_tokens}")
        # print(f"И сколько всего токенов израсходовано на запрос и на ответ (суммарно) модели"
        #       f" {self.GENERATIVE_MODEL}:{response.usage.total_tokens}")
        answer = response.choices[0].message.content
        return answer


    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens


