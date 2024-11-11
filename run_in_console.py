from RAG.RAG import RAG

list_of_path_to_data = [
        r"./data/1",
        r"./data/2",
        ]
rag = RAG(list_of_path_to_data)

while True:
    question = input("Введите ваш вопрос (или напишите 'конец' для выхода): ")
    if question.lower() == "конец":
        print("Программа завершена.")
        break
    answer = rag.get_answer(question)
    print(answer)