# AI Librarian

## Overview
AI Librarian is a powerful application designed to search and retrieve information from a personal library of documents in DOCX and PDF formats. Utilizing advanced technologies such as Retrieval-Augmented Generation (RAG), it provides precise answers to user queries by understanding the context and content of the library's documents.

## Features
- **Document Support**: Processes both DOCX and PDF files to retrieve information.
- **Retrieval-Augmented Generation**: Integrates RAG to enhance the quality and relevance of search results.
- **Interactive Console**: Allows users to input queries and receive answers directly through a console interface.
- **REST API**: Includes a RESTful API to integrate the AI Librarian into other applications or services.

## Installation
To set up the AI Librarian, you need Python 3.8 or higher. Follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/IrinaKrivichenko/AI-Librarian.git
   cd AI_Librarian
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```


### Setup Environment Variables

Create a `.env` file in the root directory of the project and define all the necessary environment variables used by the application:

```
OPENAI_API_KEY="your_Open_AI_API_key"
NUM_CHUNKS_SENT=3
NUM_NEAREST_PAIRS_FROM_HISTORY=2
NUM_LAST_PAIRS_FROM_HISTORY=2
THRESHOLD_PAIRS_SENT=0.6
THRESHOLD_CHUNKS_SENT=0.6
```

Modify these values according to your requirements.

## Running the Application

The application can be run in two modes: **Console Mode** for a straightforward, terminal-based interaction and **Service Mode** that sets up a RESTful API using FastAPI.

### Running in Console Mode

To run the application in console mode:

```bash
python run_in_console.py
```

This will initiate a loop where the system waits for user queries. After providing a question, it retrieves and displays relevant information from the document library. Use the keyword "exit" to terminate the session.

### Running as a Service

To run the application as a web service:

```bash
python run_service.py
```

This will host a local web server on `http://0.0.0.0:8000/` which you can interact with using the `/ask` endpoint by sending it JSON-formatted POST requests:

```bash
curl -X 'POST' \
  'http://0.0.0.0:8000/ask' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "your question here"
}'
```

## Development
This project utilizes the following key components:

- **RAG.RAG**: Core module implementing the retrieval-augmented generation logic.
- **DataManager**: Manages data storage and retrieval operations.
- **HistoryManager**: Manages the history of interactions for better context understanding.
- **LoggerSetup**: Handles logging across the application.
- **OpenAIHandler**: Manages interactions with OpenAI's API for generating embeddings and answers.

## Contributing
Contributions to AI Librarian are welcome! Please fork the repository and submit pull requests with your proposed changes. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License