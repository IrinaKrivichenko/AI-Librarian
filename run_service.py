from RAG.RAG import RAG
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

list_of_path_to_data = [
        r"./data/database_docx",
        r"./data/databasePDF"
        ]
rag = RAG(list_of_path_to_data)
app = FastAPI()
# Разрешаем Cross-Origin Resource Sharing для всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionItem(BaseModel):
    text: str


@app.post('/ask')
async def ask_question(question: QuestionItem):
    question = question.text
    if question.lower() == "конец":
        pass
    answer = rag.get_answer(question)
    return {"answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


