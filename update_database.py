from RAG.DataManager import DataManager
from scraping.text_scraper import create_dataframe

# folder_path_to_docs = r"/media/alex/DATA1/OBSIDIAN/PROGRAMMING"
# folder_path_to_database = r"./data/databaseDoc"

folder_path_to_docs = r"/media/alex/DATA1/OBSIDIAN/ProgrammingPDF"
folder_path_to_database = r"./data/databasePDF"

data_manager = DataManager(0, folder_path_to_database)
dataframe = create_dataframe(folder_path_to_docs)
print(dataframe)
data_manager.add_content_from_df(dataframe)
data_manager.save_databases_to_npy(folder_path_to_database)

