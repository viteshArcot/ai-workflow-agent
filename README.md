AI Workflow Agent  🚀

A production-ready AI workflow orchestration system that combines LLM-powered task generation, ML-based prioritization, and full-stack dashboards for insights.

✨ Overview

The AI Workflow Agent  is a complete end-to-end orchestration platform. It intelligently processes natural language tasks, prioritizes them with machine learning, generates context-aware subtasks using an LLM, and stores results with full history and metrics tracking.

Built with a FastAPI backend and a React + Tailwind frontend, it delivers enterprise-grade features in a clean, modern UI with dashboards for monitoring system performance.

🎯 Key Features

Custom DAG Execution → Runs multi-node workflows with topological ordering.

ML-Powered Prioritization → DecisionTreeClassifier trained on labeled examples to classify tasks as urgent/normal.

LLM Integration → OpenRouter (Mistral-7B) for task generation and summarization.

Knowledge Base Ingestion → Supports CSV/JSON ingestion for contextual task enrichment.

Execution History → Queryable API with advanced filtering (priority, limits).

Metrics Dashboard → Track per-node latency and accuracy trends.

Modern Frontend → React + Tailwind + Recharts with smooth animations and responsive design.

🛠️ Tech Stack

Backend: FastAPI, scikit-learn, pandas, SQLite, OpenRouter API
Frontend: React, TailwindCSS, Framer Motion, Recharts, Axios
Architecture: Custom DAG orchestration, modular service design, REST APIs

📊 System Architecture

Task Prioritizer → ML classifier assigns urgency.

Task Generator → LLM expands input into subtasks.

Summarizer → LLM produces executive summaries.

Logger → SQLite database stores full history + metrics.

🚀 How It Works

User submits a natural language query.

System routes it through ML + LLM pipeline.

Workflow executes across nodes with tracked latency + accuracy.

Results are displayed in a dashboard (real-time updates).

📁 Project Structure
ai-workflow-agent/
├── app/                  # FastAPI backend
│   ├── main.py           # Entry point
│   ├── graph.py          # DAG runner
│   ├── prioritizer.py    # ML classifier
│   ├── generator.py      # LLM task generator
│   ├── summarizer.py     # LLM summarizer
│   ├── logger.py         # Database logger
│   ├── ingestion.py      # Knowledge ingestion
│   └── llm_client.py     # OpenRouter client
├── frontend/             # React frontend
│   ├── src/components/   # Reusable components
│   ├── src/pages/        # Dashboard, History, Metrics
│   └── App.jsx           # Main entry
└── data/                 # Training datasets

🖼️ Screenshots

<img width="1361" height="691" alt="workflow1" src="https://github.com/user-attachments/assets/01b82ea1-f59b-410a-8b52-f9bc1da832d1" />
<img width="1363" height="687" alt="workflow2" src="https://github.com/user-attachments/assets/c923d044-33ad-4ecd-afda-2e2a5eec0f32" />
<img width="1364" height="686" alt="workflow3" src="https://github.com/user-attachments/assets/1b3cd1d3-e0f3-45b8-9648-757845d8581f" />
<img width="1365" height="688" alt="workflow4" src="https://github.com/user-attachments/assets/524fafad-799f-4973-83d9-a7507d4a6231" />
<img width="1364" height="689" alt="workflow5" src="https://github.com/user-attachments/assets/33b55e5c-d251-4f24-9b8c-bfd8eaafbe9d" />






🎨 Why This Project Matters

This project demonstrates applied AI engineering across multiple layers:

Backend intelligence (ML + LLM integration).

Workflow orchestration (custom DAG execution).

Full-stack delivery (React dashboards with animations).

Production quality (error handling, async, modular design).

It mirrors the real-world systems used in enterprise AI orchestration platforms.

🧑‍💻 Setup Instructions
Backend
cd app
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend
cd frontend
npm install
npm run dev


Access app at: http://localhost:3000
