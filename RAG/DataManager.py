import os
import sys
import numpy as np
import pandas as pd
import boto3
from scipy.spatial import distance
import faiss
from tqdm import tqdm
from dotenv import load_dotenv
from RAG.LoggerSetup import LoggerSetup
from RAG.OpenAIHandler import OpenAIHandler

load_dotenv()

class DataManager:
# Responsible for handling all operations related to data storage and retrieval,
# including operations on the metadata, content, and embedding databases.

    def __init__(self, num_chunks_sent, data_bucket=None, openai_handler=None, logger=None):
        self.openai_handler = OpenAIHandler() if openai_handler is None else openai_handler
        self.logger = LoggerSetup() if logger is None else logger
        self.metadata_database = None
        self.content_database = None
        self.embeddings_database = faiss.IndexFlatIP(3072)# 3072 - embedding vector length
        self.embeddings_database_np = None
        self.CHUNK_SIZE = 1000
        self.CHUNKS_OVERLAP = 200
        self.NUM_CHUNKS_SENT = int(os.getenv("NUM_CHUNKS_SENT"))
        self.THRESHOLD_CHUNKS_SENT = float(os.getenv("THRESHOLD_CHUNKS_SENT"))
        self.load_databases_from_npy(data_bucket)


    def clean_up_temporary_files(self):
        """Удаляет все файлы в папке /tmp."""
        temp_dir = "/tmp"
        try:
            for file_name in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file_name)
                if os.path.isfile(file_path):  # Удаляем только файлы
                    os.remove(file_path)
                    self.logger.info(f"Deleted temporary file: {file_path}")
        except Exception as e:
            self.logger.error(f"Error cleaning up /tmp directory: {e}")

    def load_databases_from_npy(self, bucket_name: str):
        def download_file_from_s3(file_name):
            """ downloadfile from S3 into tmp folder."""
            try:
                temp_file_path = os.path.join("/tmp", file_name)
                s3_client.download_file(bucket_name, file_name, temp_file_path)
                return temp_file_path
            except Exception as e:
                self.logger.error(f"Error downloading {file_name} from S3: {e}")
                raise

        try:
            s3_client = boto3.client('s3')
            metadata_db_path = download_file_from_s3("metadata.npy")
            content_db_path = download_file_from_s3("content.npy")
            embeddings_db_path = download_file_from_s3("embedding.npy")

            self.metadata_database = np.load(metadata_db_path)
            self.content_database = np.load(content_db_path)
            temp_embeddings = np.load(embeddings_db_path)
            self.embeddings_database_np = temp_embeddings

            # Loading or creating embeddings
            for i in range(len(self.embeddings_database_np)):
                self.embeddings_database.add(np.expand_dims(self.embeddings_database_np[i], axis=0))

            self.logger.info(f"From S3 loaded:")
            self.logger.info(f"metadata_database.shape is {self.metadata_database.shape}")
            self.logger.info(f"content_database.shape is {self.content_database.shape}")
        except FileNotFoundError as e:
            self.logger.error(f"FileNotFoundError: {e.filename} not found.")
            self.metadata_database = None
            self.content_database = None
            self.embeddings_database_np = None
        except ValueError:
            self.logger.error("ValueError: The database files are not a valid numpy files.")
            self.metadata_database = None
            self.content_database = None
            self.embeddings_database_np = None
        finally:
            # clean tmp folder
            self.clean_up_temporary_files()

    def save_databases_to_npy(self, bucket_name: str):
        def save_file_to_s3(file_name, data):
            """ save data into file and load it to S3."""
            try:
                temp_file_path = os.path.join("/tmp", file_name)
                np.save(temp_file_path, data)
                self.logger.info(f"Temporary file saved: {temp_file_path}")

                s3_client.upload_file(temp_file_path, bucket_name, file_name)
                self.logger.info(f"File {file_name} uploaded to S3 bucket: {self.bucket_name}")
            except Exception as e:
                self.logger.error(f"Error saving {file_name} to S3: {e}")
                raise

        try:
            s3_client = boto3.client('s3')
            save_file_to_s3("metadata.npy", self.metadata_database)
            save_file_to_s3("content.npy", self.content_database)
            save_file_to_s3("embedding.npy", self.embeddings_database_np)
        except Exception as e:
            self.logger.error(f"Error saving databases to S3 bucket {self.bucket_name}: {e}")
        finally:
            # Очистка временной директории
            self.clean_up_temporary_files()




    def add_content_from_df(self, df: pd.DataFrame):
        for index, row in df.iterrows():
            file_name = row["file_name"]
            date_of_last_change = row["date_of_last_change"]
            last_modified_time = row["last_modified_time"]
            content = row["content"]

            # Delete rows from databases if exists
            if self.metadata_database is not None:
                condition = self.metadata_database[:, 0] == file_name
                indexes_to_delete = np.where(condition)[0]
                if len(indexes_to_delete) != 0:
                    curr_modified_time = float(self.metadata_database[indexes_to_delete[0], 1])
                    if curr_modified_time >= last_modified_time:
                        continue
                    self.content_database = np.delete(self.content_database, indexes_to_delete)
                    self.metadata_database = np.delete(self.metadata_database, indexes_to_delete, axis=0)
                    self.embeddings_database.remove_ids(faiss.IDSelectorBatch(indexes_to_delete))
                    self.embeddings_database_np = np.delete(self.embeddings_database_np, indexes_to_delete, axis=0)

            print("file_name", file_name)
            chunks = self.split_text_into_chunks(text=content, chunk_size=self.CHUNK_SIZE,
                                                 chunks_overlap=self.CHUNKS_OVERLAP)
            for i in tqdm(range(len(chunks)),
                          desc=f"Adding chunks to database from {file_name}"):  # Wrap your loop with tqdm for a progress bar
                self.__add_chunk_to_database(file_name=file_name,
                                             date_of_last_change=date_of_last_change,
                                             last_modified_time=last_modified_time,
                                             chunk_number=i, chunk_text=chunks[i])
        self.logger.info(f"metadata_database.shape is {self.metadata_database.shape}")
        self.logger.info(f"content_database.shape is {self.content_database.shape}")

    def __add_chunk_to_database(self, file_name: str, date_of_last_change: str, last_modified_time: float,
                                chunk_number: int, chunk_text: str):
        try:
            # Adding embedding to DB
            content_embedding = self.openai_handler.get_text_embedding(text=chunk_text)
            self.embeddings_database.add(content_embedding)
            if self.embeddings_database_np is None:
                self.embeddings_database_np = content_embedding
            else:
                self.embeddings_database_np = np.append(self.embeddings_database_np, content_embedding, axis=0)

            # Adding metadata to DB
            metadata = [file_name, last_modified_time, date_of_last_change, chunk_number]
            if self.metadata_database is None:
                self.metadata_database = [metadata]
            else:
                self.metadata_database = np.append(self.metadata_database, [metadata], axis=0)

            # Adding content to DB
            if self.content_database is None:
                self.content_database = [chunk_text]
            else:
                self.content_database = np.append(self.content_database, [chunk_text], axis=0)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error(f"An {exc_type} occurred: {e} in file {fname} at line {exc_tb.tb_lineno}")
            self.logger.warning("chunk was not added")

    def find_chunk_in_database(self, question_embedding: np.ndarray):
        try:
            if self.metadata_database is None:
                raise TypeError("THERE IS NO DATABASE!")

            # Looking for nearest indexes among all database
            nearest_indexes = self.embeddings_database.search(x=question_embedding, k=self.NUM_CHUNKS_SENT)[1]

            new_nearest_indexes = []
            for index in nearest_indexes[0]:
                if index == -1: continue
                file_name = self.metadata_database[index, 0]
                # self.logger.info(f"найденный чанк из файла {file_name} ")
                self.logger.info(f"найденный чанк c метаданными {self.metadata_database[index, :]} ")
                embedding = self.embeddings_database_np[index]
                cosine_distance = distance.cosine(embedding, question_embedding[0])
                self.logger.info(f"cosine_distance = {cosine_distance} ")
                self.logger.info(f"текст чанка: {self.content_database[index][:40]}")
                self.logger.debug(f".................")
                self.logger.debug(f"{self.content_database[index][-40:]}")
                if cosine_distance <= self.THRESHOLD_CHUNKS_SENT:
                    new_nearest_indexes.append(index)
            self.logger.info(f" found nearest_indexes={new_nearest_indexes}")
            context = self.join_chunks(new_nearest_indexes)
            num_of_chunks_found = len(new_nearest_indexes)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.logger.error(f"An {exc_type} occurred: {e} in file {fname} at line {exc_tb.tb_lineno}")
            context = ""
            num_of_chunks_found = 0
        return context, num_of_chunks_found


    @staticmethod
    # def split_text_into_chunks(text: str, chunk_size: int, chunks_overlap: int) -> list[str]:
    def split_text_into_chunks(text, chunk_size, chunks_overlap):
        if chunks_overlap >= chunk_size:
            raise Exception("overlap_size can not be greater than chunk_size")
        if chunk_size >= len(text) or chunks_overlap >= len(text):
            return [text]
        chunks = []
        i = 0
        while i < len(text):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
            i += chunk_size - chunks_overlap
        return chunks

    def join_chunks(self, chunk_indexes):
        if len(chunk_indexes) == 0:
            return ""
        chunk_indexes = sorted(chunk_indexes)
        context = ""
        prev_metadata = None
        for i in range(len(chunk_indexes)):
            curr_context = self.content_database[chunk_indexes[i]]
            if curr_context in context:
                continue
            curr_metadata = self.metadata_database[chunk_indexes[i]]
            metadata_info = f"// chunk number {curr_metadata[-1]} from file {curr_metadata[0]}: "
            if prev_metadata is not None and \
                    np.all(curr_metadata[:-1] == prev_metadata[:-1]) and \
                    int(curr_metadata[-1]) == int(prev_metadata[-1]) + 1:
                context += metadata_info + curr_context[self.CHUNKS_OVERLAP:]
            else:
                context += metadata_info + curr_context + "."
        return context

