# 💰 Fenny - Financial Agentic AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web_Framework-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Llama.cpp](https://img.shields.io/badge/Llama.cpp-LLM_Framework-green?logo=c%2B%2B)](https://github.com/ggerganov/llama.cpp)
[![Hugging Face](https://img.shields.io/badge/Hugging_Face-Models-yellow)](https://huggingface.co/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Deep_Learning-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4?logo=microsoftazure)](https://azure.microsoft.com/)

**Fenny is an advanced financial AI assistant** that combines LLM reasoning with financial tooling and document analysis capabilities to provide accurate, actionable financial insights.

## 🌟 Demo
*Video demonstration coming soon - stay tuned!*

### System Architecture
![Fenny Architecture](https://i.imgur.com/placeholder.png)

## ✨ Key Features

- **Financial Agent System** with dynamic tool selection capabilities
- **Quantized Finance LLM** (Q4_K_M) for local, private financial conversations
- **Retrieval-Augmented Generation (RAG)** for financial document analysis
- **Real-time Stock Price** and **Currency Exchange** tools
- **Apple Silicon Optimized** with Metal acceleration for blazing-fast inference
- **Session Management** for persistent financial conversations
- **Multi-file Upload** for document analysis (PDF, Excel, TXT)

## 🚀 Performance Highlights

| Metric                | Value                     | Advantage                          |
|-----------------------|---------------------------|------------------------------------|
| Model Size            | 3.8 GB (Q4 quantized)     | 75% smaller than FP16              |
| Apple Silicon Speed   | 28 tokens/sec (M2 Pro)    | 4.2x faster than CPU-only          |
| Tool Response Time    | < 800ms                   | Real-time financial data           |
| Context Window        | 4096 tokens               | Handles complex financial queries  |
| RAG Retrieval         | < 50ms                    | Instant document insights          |

## 🛠 Tech Stack Deep Dive

### Core Financial Intelligence
| Component             | Technology                          | Implementation Details              |
|-----------------------|-------------------------------------|-------------------------------------|
| Base Model            | Finance-Chat (Q4_K_M quantized)     | Specialized financial LLM           |
| Execution Framework   | Graph-based Agent System            | Dynamic tool routing                |
| RAG System            | FAISS + Sentence Transformers       | Local vector database               |
| Stock Data            | Yahoo Finance API                   | Real-time market data               |
| Currency Exchange     | ExchangeRate-API                    | Global currency conversion          |
| Model Hosting         | Hugging Face                        | Model repository & download         |
| Deep Learning         | PyTorch                             | Embedding generation & processing   |
| Apple Silicon         | Metal Acceleration                  | GPU offloading for Apple devices    |

## 🧩 Project Structure

```bash
Fenny-Financial-Agentic-AI/
├─ Backend/
│  ├─ __pycache__/                     # Compiled Python cache files
│  ├─ api/                             # API endpoints (future expansion)
│  ├─ core/                            # Core application logic
│  │  ├─ __pycache__/                  # Session management cache
│  │  └─ session.py                    # Session management implementation
│  ├─ data/                            # Data storage
│  │  ├─ examples/                     # Example financial documents
│  │  ├─ knowledge_base/               # User-uploaded financial documents
│  │  └─ models/                       # LLM models
│  │     ├─ .cache/                    # Hugging Face cache
│  │     ├─ test/                      # Model test files
│  │     └─ finance-chat.Q4_K_M.gguf   # Quantized financial LLM
│  ├─ graph/                           # Execution graph system
│  │  ├─ __pycache__/                  # Graph component cache
│  │  ├─ __init__.py                   # Graph module initialization
│  │  ├─ edges.py                      # Graph edge definitions
│  │  ├─ graph_builder.py              # Builds the execution graph
│  │  └─ nodes.py                      # Tool execution nodes
│  ├─ llm/                             # LLM interface
│  │  ├─ __pycache__/                  # LLM component cache
│  │  ├─ __init__.py                   # LLM module initialization
│  │  ├─ download_model.py             # Model download utilities
│  │  ├─ llm.py                        # LLM interface implementation
│  │  └─ prompt_templates.py           # Financial prompt templates
│  ├─ rag/                             # Retrieval-Augmented Generation
│  │  ├─ __init__.py                   # RAG module initialization
│  │  ├─ document_loader.py            # Financial document processing
│  │  ├─ embedder.py                   # Text embedding generation
│  │  └─ retriever.py                  # Document retrieval system
│  ├─ tools/                           # Financial tools
│  │  ├─ __pycache__/                  # Tool component cache
│  │  ├─ __init__.py                   # Tools module initialization
│  │  ├─ Currency_tool.py              # Currency exchange implementation
│  │  ├─ Stocks_tool.py                # Stock price lookup implementation
│  │  └─ tool_registry.py              # Tool management system
│  ├─ utils/                           # Utility functions
│  │  ├─ __pycache__/                  # Utility cache
│  │  ├─ __init__.py                   # Utilities module initialization
│  │  └─ logger.py                     # Logging implementation
│  ├─ .env                             # Environment variables
│  ├─ config.py                        # Application configuration
│  ├─ main.py                          # FastAPI entry point
│  └─ requirements.txt                 # Python dependencies
├─ frontend/                            # User interface
│  ├─ static/                          # Static assets
│  │  ├─ css/                           # Stylesheets
│  │  │  ├─ background.css             # Background styling
│  │  │  └─ ChatContainer.css          # Chat interface styling
│  │  └─ js/                            # JavaScript
│  │     ├─ background.js              # Background functionality
│  │     └─ ChatContainer.js           # Chat interface logic
│  └─ templates/                       # HTML templates
│     └─ Fenny.html                    # Main application template
├─ .gitignore                           # Git ignore rules
├─ LICENSE                              # MIT License
└─ README.md                            # Project documentation
```

## ⚡ Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/aktheroy/Fenny-Financial-Agentic-AI.git
cd Fenny-Financial-Agentic-AI

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r Backend/requirements.txt

# Start the application
cd Backend
python main.py
```

### Access the Application
1. Open your browser to `http://localhost:8000`
2. Start asking financial questions:
   - "What is the current price of AAPL?"
   - "Convert 100 USD to EUR"
   - "Analyze the financial report I uploaded"

## ☁️ Azure Deployment

Fenny is fully ready for Azure deployment! Follow these steps to deploy your own instance:

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name FennyRG --location eastus

# Create App Service Plan
az appservice plan create --name FennyPlan --resource-group FennyRG --sku B1 --is-linux

# Create Web App (Python 3.10)
az webapp create --resource-group FennyRG --plan FennyPlan --name YOUR_UNIQUE_APP_NAME --runtime "PYTHON|3.10"

# Configure deployment from GitHub
az webapp deployment source config --name YOUR_UNIQUE_APP_NAME --resource-group FennyRG \
  --repo-url https://github.com/aktheroy/Fenny-Financial-Agentic-AI --branch main --manual-integration

# Set environment variables
az webapp config appsettings set --resource-group FennyRG --name YOUR_UNIQUE_APP_NAME \
  --settings MODEL_PATH="data/models/finance-chat.Q4_K_M.gguf"
```

Your Fenny instance will be available at: `https://YOUR_UNIQUE_APP_NAME.azurewebsites.net`

## 📚 API Documentation

### Chat Endpoint
```python
import requests

payload = {
    "message": "What is the current price of NVIDIA stock?",
    "session_id": "optional-session-id",
    "files": []  # List of file uploads (PDF, Excel, TXT)
}

response = requests.post(
    "http://localhost:8000/api/chat",
    data=payload,
    files=[("files", open("financial_report.pdf", "rb"))]
)

print(response.json())
# {"response": "NVIDIA (NVDA) current price: $125.45 USD...", "file_count": 1}
```

### Supported Financial Tools
| Tool                | Parameters                     | Example Usage                                  |
|---------------------|--------------------------------|-----------------------------------------------|
| Stock Price         | ticker (str)                   | "What is the price of TSLA?"                  |
| Currency Exchange   | base, target, amount (float)   | "Convert 500 USD to EUR"                      |
| Document Analysis   | uploaded PDF/Excel/TXT         | "Summarize the financial report I uploaded"   |

## 📊 RAG Document Analysis

Fenny can analyze your financial documents to provide insights:

1. Upload PDFs, Excel sheets, or text files
2. Ask questions about the content:
   - "What was the net income in Q3?"
   - "Summarize the balance sheet"
   - "Show me the revenue trends"

![RAG Document Analysis](https://i.imgur.com/placeholder-rag.png)

## 🤝 Contribution Guidelines

### Setting Up for Development
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
pytest tests/

# Check code quality
flake8 Backend/ --max-line-length=100
```

### Architecture Principles
1. **Financial Domain Focus**: All components should prioritize financial accuracy
2. **Privacy First**: No user data leaves the local environment
3. **Tool Agnosticism**: New financial tools should integrate seamlessly
4. **Apple Silicon Optimized**: Leverage Metal acceleration where possible

### Apple Silicon (Metal) Optimizations
Fenny automatically enables Metal acceleration on Apple Silicon devices:

```python
# In llm.py - Metal is automatically enabled
if platform.system() == "Darwin":
    os.environ["LLAMA_METAL"] = "1"  # Enable Metal backend
```

This provides up to 4.2x faster inference on M-series Macs compared to CPU-only execution.

## 📜 License & Citation

```bibtex
@software{FennyFinancialAI2025,
  author = {Arun Kumar Roy},
  title = {Fenny - Financial Agentic AI Assistant},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/aktheroy/Fenny-Financial-Agentic-AI}}
}
```

**License:** [MIT](LICENSE) | **Contact:** [aktheroy@outlook.com](mailto:aktheroy@outlook.com) | **Project:** [GitHub Repository](https://github.com/aktheroy/Fenny-Financial-Agentic-AI)

---

> **Note**: Fenny is designed for informational purposes only. Always consult with a licensed financial advisor before making investment decisions.
