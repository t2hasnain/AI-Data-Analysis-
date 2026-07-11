# AI-Powered Data Analysis Assistant

A professional, modular, production-ready **Streamlit** application that acts as an AI-powered Data Analysis Assistant for the **Track A – Explorer** challenge.

## Features

### Core (Steps 1–5)
| Step | Feature | Module |
|------|---------|--------|
| 1 | Multi-format loading (CSV, Excel, JSON, Parquet) | `analysis.py` |
| 2 | Dataset info, statistical summary, data-quality report | `analysis.py` |
| 3 | AI-powered Q&A — 3 predefined + custom questions | `ai_helper.py` |
| 4 | Interactive charts: bar, pie, histogram, correlation heatmap | `visualization.py` |
| 5 | AI-generated chart explanations & proactive insights | `ai_helper.py` |

### Bonus Features
- **Modern UI** — Dark/Light theme toggles, glassmorphism cards, animated metric cards
- **Multi-Agent Architecture** — 3 specialised AI agents (DataBot, ChartBot, InsightBot)
- **Multi-Format Upload** — drag-and-drop CSV, Excel, JSON, Parquet via sidebar
- **Multiple Chart Types** — 4 interactive Plotly chart variants
- **Chatbot Widget** — floating DataBot for persistent conversations
- **Export Analysis as PDF** — full report download (fpdf2) with safe Unicode encoding
- **Docker Support** — fully containerized application

## Multi-Agent Architecture

| Agent | Role | System Prompt Focus |
|-------|------|---------------------|
| 🤖 **DataBot** | Data Analyst | Answers dataset questions using exact mathematical stats |
| 🎨 **ChartBot** | Chart Explainer | Writes 2-sentence explanations of generated visualisations |
| 💡 **InsightBot** | Insight Generator | Proactively surfaces top-3 findings from the dataset |

All agents are powered by **Azure OpenAI (GPT-4o-mini)**, **Gemini**, or **Groq Llama 3 / Mixtral**.

## Project Structure

```
project/
├── main.py              # Streamlit UI — modern theme, multi-agent display
├── analysis.py          # Pandas/NumPy data loading + statistical analysis
├── visualization.py     # Plotly interactive chart generation
├── ai_helper.py         # Multi-agent system via LangChain/OpenAI SDK
├── requirements.txt     # Complete dependencies
├── Dockerfile           # Docker container configuration
├── README.md            # This file
├── .env                 # API credentials (GROQ_API_KEY, AZURE_API_KEY)
├── presentation.txt     # Presentation overview script
├── architecture.txt     # Architecture diagram
└── uploads/             # User-uploaded dataset cache
```

## Setup & Installation

1. **Create a virtual environment** (already provided as `venv/`):
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**: Copy `.env.example` to `.env` and fill in your API credentials (e.g., `GROQ_API_KEY`, `AZURE_API_KEY`, or `GEMINI_API_KEY`).

### Running via Docker
1. **Build the image:** `docker build -t data-assistant .`
2. **Run the container:** `docker run -p 8501:8501 data-assistant`

### Running Locally
```bash
streamlit run main.py
```

1. Upload a CSV file via the sidebar.
2. View automated dataset overview with metric cards.
3. Click predefined question buttons or type custom questions.
4. Browse multiple chart types in the tabbed view.
5. Read AI-generated explanations and insights.
6. Download charts as PNG or the full report as PDF.

## Tech Stack

- **UI**: Streamlit (Dark/Light themed, custom CSS)
- **Data Analysis**: Pandas, NumPy
- **Visualisation**: Plotly Express
- **AI Integration**: Azure OpenAI, Gemini, Groq (via OpenAI SDK and LangChain)
- **PDF Export**: fpdf2
- **Environment**: python-dotenv, Docker

## Sample Dataset

A `sample_data.csv` and `employee.xlsx` are included for testing all features and predefined questions across multiple file formats.
