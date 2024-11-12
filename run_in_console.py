from RAG.RAG import RAG

list_of_path_to_data = [
        r"./data/1",
        r"./data/2",
        ]
rag = RAG(list_of_path_to_data)

while True:
    question = input('Enter your question (or type "exit" to exit):')
    if question.lower() == "exit":
        print("The program completed execution.")
        break
    answer = rag.get_answer(question)
    print(answer)