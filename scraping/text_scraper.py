import os
import pandas as pd
from datetime import datetime

from scraping.docx_scraper import get_docx_text
from scraping.pdf_scraper import get_pdf_text


def create_dataframe(folder_path):
    """Функция для создания датафрейма с именами файлов и их содержимым."""
    data = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            last_modified_time = os.path.getmtime(file_path)
            date_of_last_change = datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d %H:%M:%S')
            if filename.endswith(".docx"):
                text = get_docx_text(file_path)
            elif filename.endswith(".pdf"):
                text = get_pdf_text(file_path)
            else:
                continue
            data.append({
                "file_name": filename,
                "content": text,
                "last_modified_time": last_modified_time,
                "date_of_last_change": date_of_last_change
            })
    df = pd.DataFrame(data)
    return df

