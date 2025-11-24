# Fraud Detection Agent

## Project Structure

```
fraud-detection/
├── app.py                          
├── main.py                         
├── pre_processing.py               
├── pyproject.toml                  
├── README.md                       
├── assets/
│   └── fraud.csv                                        
└── src/
    ├── graph.py                    
    ├── core/
    │   ├── config.py              
    │   └── langfuse.py            
    ├── database/
    │   └── __init__.py            
    ├── modules/
    │   ├── agents/
    │   │   └── supervisor_agent.py
    │   ├── const/
    │   │   └── enum.py            
    │   ├── schemas/
    │   │   └── state_schema.py     
    │   ├── services/
    │   │   ├── pdf_service.py      
    │   │   └── tabular_data_service.py  
    │   ├── tools/
    │   │   ├── pdf_tool.py         
    │   │   └── tabular_data_tool.py 
    │   └── utils/
    │       └── supervisor_util.py
```

## Installation

1. **Clone the repository**:
   ```bash
   $ git clone https://github.com/rzkamalia/fraud-detection.git
   $ cd fraud-detection
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   $ uv venv
   $ source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   $ uv sync
   ```

4. **Set up environment variables**: Copy `.env.example` to `.env` and configure your settings.

5. **Set up the database**:
    ```bash
    $ docker pull pgvector/pgvector
    
    $ docker run -d \
      --name postgres-pgvector \
      -e POSTGRES_USER=... \
      -e POSTGRES_PASSWORD=... \
      -e POSTGRES_DB=postgres \
      -p 5432:5432 \
      pgvector/pgvector:pg15
    ```

5. **Run the application**:
    ```bash
    $ streamlit run app.py
    ```

The application will start on `http://localhost:8501`

## Framework

The following are frameworks used in this fraud detection system.

1. Database & Vector Storage
    - **PostgreSQL**: Primary relational database for structured data storage
    - **pgvector**: PostgreSQL extension for efficient vector similarity search and embedding storage

2. AI & Machine Learning Framework
    - **LangGraph**: Orchestrates complex AI workflows and agent interactions
    - **LangChain**: Provides the foundation for building language model applications
    - **LangFuse**: Observability and analytics platform for LLM applications, enabling monitoring and debugging

3. Language Model Integration
    - **OpenRouter**: Unified API gateway for accessing multiple AI models and providers

4. User Interface
    - **Streamlit**: Creates interactive web applications for data visualization and user interaction

## [Demo Videoscreen](https://github.com/rzkamalia/fraud-detection/blob/main/assets/demo.webm)