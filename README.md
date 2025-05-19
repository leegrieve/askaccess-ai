# AskAccess AI Assistant (Prototype)

AskAccess is an internal AI assistant prototype designed to answer queries from Access employees and customers. It leverages existing knowledge base articles and Salesforce cases to provide concise, relevant responses — acting as a low-cost alternative to tools like Clari.

---

## 🔧 Features

- ✅ **Natural Language Processing** using OpenAI
- ✅ **Document Ingestion** via LangChain (PDF, HTML, plain text)
- ✅ **Vector Search** with local embeddings for fast, relevant results
- ✅ **FastAPI Backend** written in Python
- ✅ **Comprehensive Logging** of user queries and responses
- ✅ **Evaluation Report** showing 90% accuracy and <3s latency
- ✅ **Slack/Web UI Integration Ready**

---

## 📂 Project Structure

```bash
.
├── app/                    # Core FastAPI application
├── ingest/                # Document loaders & embedding logic
├── models/                # Prompt and response schema
├── tests/                 # Automated test suite
├── reports/               # Evaluation results and test metrics
└── README.md              # You are here
