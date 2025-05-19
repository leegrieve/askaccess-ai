# AskAccess

AskAccess is an AI assistant prototype designed to answer internal employee questions and customer queries. It leverages existing knowledge base articles and Salesforce cases to provide accurate and concise responses, functioning as a low-cost alternative to Clari.

## Features

- Natural language query processing
- Semantic search across knowledge base articles and Salesforce cases
- Concise and accurate responses using OpenAI's GPT models
- Query logging for future analysis
- Support for PDF, HTML, and plain text knowledge base articles
- Support for Salesforce case data

## Architecture

- **Backend**: Python with FastAPI
- **Document Processing**: LangChain for document ingestion and semantic search
- **Vector Store**: FAISS for efficient similarity search
- **LLM**: OpenAI GPT for response generation
- **Embeddings**: OpenAI Embeddings for document vectorization

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd askaccess
   ```

2. Install dependencies using Poetry:
   ```bash
   pip install poetry
   poetry install
   ```

   Alternatively, you can use pip:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

### Running the Application

1. Start the FastAPI server:
   ```bash
   python -m app.main
   ```

2. The API will be available at `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### API Endpoints

- **POST /query/ask**: Process a natural language query
  ```json
  {
    "query": "How do I reset my password?",
    "max_results": 4,
    "include_sources": true,
    "log_query": true
  }
  ```

- **GET /query/logs**: Retrieve recent query logs

- **POST /ingestion/upload**: Upload knowledge base articles
  - Supports PDF, HTML, and plain text files

- **POST /ingestion/salesforce**: Ingest Salesforce case data

### Document Ingestion

Before querying, you need to ingest documents into the system:

1. Upload knowledge base articles using the `/ingestion/upload` endpoint
2. Ingest Salesforce case data using the `/ingestion/salesforce` endpoint

## Testing

### Running Tests

Run the test suite using pytest from the project root:

```bash
pytest
```

For more verbose output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_query_accuracy.py -v
```

### Test Data

The test suite includes sample knowledge base articles and seed queries for testing query accuracy. The system aims to achieve:

- Response accuracy: 85%+
- Response latency: <3 seconds

Test results are saved to `reports/MVP_eval.md`.

## Project Structure

```
askaccess/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── document_store.py    # Document ingestion and retrieval
│   ├── query_processor.py   # Query processing logic
│   ├── response_generator.py # Response generation using LLM
│   ├── ingestion.py         # Document ingestion endpoints
│   └── query.py             # Query processing endpoints
├── data/
│   ├── uploads/             # Uploaded knowledge base articles
│   ├── vector_store/        # FAISS vector store
│   └── query_logs/          # Query logs
├── tests/
│   ├── test_ingestion.py    # Tests for document ingestion
│   └── test_query_accuracy.py # Tests for query accuracy
├── reports/
│   └── MVP_eval.md          # Evaluation report
├── .env                     # Environment variables
├── pyproject.toml           # Poetry configuration
└── README.md                # This file
```

## Future Enhancements

- Integration with Slack or internal web chat
- User feedback collection (thumbs up/down)
- Improved response accuracy through fine-tuning
- Support for more document formats
- Authentication and authorization

## License

[Specify license information]
