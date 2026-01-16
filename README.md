# 🤖 Auto-DataScientist - Multi-Agent AI ML Pipeline

An **industry-grade automated machine learning system** powered by AI agents that handles the complete data science workflow from research to model deployment.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 What Does It Do?

Give it a goal like **"Train a model to predict diabetes risk"** and watch it:

1. 🔍 **Research** - Search Kaggle datasets + academic papers
2. ✅ **Validate** - HTTP check + browser verification with Human-in-the-Loop approval
3. 📊 **Engineer** - Generate EDA code with visualizations
4. 🤖 **Train** - Create ML models with preprocessing pipelines
5. 🌐 **Execute** - Run code in Google Colab browser automation
6. 🔧 **Debug** - Self-heal execution errors (max 3 attempts)
7. ✅ **Review** - Final satisfaction check with retry option

## 🎬 Demo

![Workflow Demo](docs/demo.gif)

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                     │
│            Real-time Timeline • HITL Modals • Logs           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│              Orchestrator Service (FastAPI)                  │
│   ┌──────────┐  ┌──────────┐  ┌────────┐  ┌──────────┐    │
│   │ Research │→ │  Critic  │→ │  Data  │→ │    ML    │    │
│   │  Agent   │  │  Agent   │  │Engineer│  │ Engineer │    │
│   └──────────┘  └──────────┘  └────────┘  └──────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST /execute
┌──────────────────────▼──────────────────────────────────────┐
│            Browser Agent Service (Playwright)                │
│     Google Colab Automation • Code Execution • Logs         │
└─────────────────────────────────────────────────────────────┘
```

### **Agent Responsibilities**

| Agent | Function | Tech Stack |
|-------|----------|------------|
| **Research Agent** | Search Kaggle datasets, Arxiv papers, create research plan | Tavily Search API, Gemini LLM |
| **Critic Agent** | HTTP validation, browser preview, HITL approval | httpx, Playwright, FastAPI |
| **Data Engineer** | Generate EDA code (pandas, matplotlib, seaborn) | Gemini LLM code generation |
| **ML Engineer** | Create training pipelines (sklearn, preprocessing) | Gemini LLM with anti-dummy-data rules |
| **Debugger Agent** | Fix runtime errors in generated code | Error log parsing + LLM |
| **Browser Agent** | Execute Python in Google Colab, capture outputs | Playwright headless automation |

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **Google API Key** (Gemini)
- **Tavily API Key** (search)

### 1. Clone Repository

```bash
git clone https://github.com/lakshmanbunny/Multi-Agentic-Major-Project.git
cd Multi-Agentic-Major-Project
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your API keys:
# GOOGLE_API_KEY=your_gemini_key_here
# TAVILY_API_KEY=your_tavily_key_here
```

### 3. Frontend Setup

```bash
cd ui
npm install
```

### 4. Run Services

**Terminal 1 - Orchestrator:**
```bash
python services/orchestrator/src/main.py
# Running on http://localhost:8000
```

**Terminal 2 - Browser Agent:**
```bash
python run_browser_robust.py
# Running on http://localhost:8001
```

**Terminal 3 - Frontend:**
```bash
cd ui
npm run dev
# Running on http://localhost:5173
```

### 5. Use the System

1. Open **http://localhost:5173**
2. Enter goal: *"Train a model to predict diabetes risk"*
3. Approve dataset in HITL modal
4. Review execution in browser window
5. Provide final feedback (satisfied/retry)

## 📂 Project Structure

```
auto-data-scientist/
├── services/
│   ├── orchestrator/
│   │   └── src/
│   │       ├── main.py              # FastAPI server + workflow logic
│   │       └── agents/
│   │           ├── research.py       # Research Agent
│   │           ├── critic.py         # Critic Agent (HITL)
│   │           ├── data_engineer.py  # EDA code generator
│   │           ├── ml_engineer.py    # ML code generator
│   │           └── debugger.py       # Error fixing agent
│   └── browser_agent/
│       └── src/
│           └── main.py              # Playwright automation
├── ui/                              # React frontend
│   ├── src/
│   │   └── App.jsx                  # Main UI component
│   └── package.json
├── libs/
│   └── core/
│       ├── state.py                 # Pydantic state models
│       └── logger.py                # JSON structured logging
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
└── README.md
```

## 🎨 Features

### ✅ Human-in-the-Loop (HITL) Approval
- **Dataset Approval Modal** - Review dataset before training
- **Final Satisfaction Loop** - Retry if results aren't satisfactory

### 🔄 Self-Healing Execution
- Automatically detects Python errors in browser logs
- Calls Debugger Agent to fix code
- Max 3 retry attempts with 5-second rate limiting

### 📊 Real-Time Frontend
- **Agent Timeline** - Live updates for each agent step
- **Logs Display** - See backend events in real-time
- **Status Polling** - 2-second interval checks

### 🚫 Anti-Dummy-Data Safeguards
- **Rule 1:** Never create hardcoded DataFrames
- **Rule 2:** Dynamically inspect `df.columns` if preview unavailable
- **Rule 3:** Smart target column detection (keywords + fallback)
- **Rule 4:** Safety checks before dropping columns

## 🛠️ Configuration

### Environment Variables (`.env`)

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_search_key_here

# Optional
PORT=8000
BROWSER_PORT=8001
LOG_LEVEL=INFO
```

## 🧪 API Endpoints

### Orchestrator (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/workflow/start` | Start new workflow |
| `GET` | `/workflow/{id}/status` | Poll workflow status |
| `POST` | `/workflow/{id}/approve` | Approve dataset (HITL) |
| `POST` | `/workflow/{id}/reject` | Reject dataset (retry research) |
| `POST` | `/workflow/{id}/feedback` | Final satisfaction check |
| `POST` | `/workflow/clear` | Clear all workflow state |

### Browser Agent (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/execute` | Execute Python code in Colab |

## 🐛 Troubleshooting

### Issue: HITL Modal Doesn't Appear
**Solution:** Check browser console logs for `HITL MODAL TRIGGERED!` and verify `state["next_step"] = "waiting_human_approval"` is set in backend.

### Issue: Workflow Gets Stuck
**Solution:** Look for `UnboundLocalError` in logs. Ensure `state = workflows[workflow_id]` is the **first line** in `run_workflow_simulation()`.

### Issue: Fake Accuracy Scores (1.0 or 0.5)
**Solution:** ML Engineer was generating dummy data. Verify the updated `ml_engineer.py` with anti-dummy-data rules is deployed.

### Issue: Browser Agent Not Reachable
**Solution:** Ensure `run_browser_robust.py` is running on port 8001. Check firewall settings.

## 📈 Performance

- **Research Phase:** ~10-15 seconds (Tavily search + Arxiv)
- **Critic Validation:** ~45-60 seconds (browser load + Kaggle download)
- **Code Generation:** ~5-10 seconds per agent (Gemini LLM)
- **Browser Execution:** ~60-120 seconds (full ML pipeline)

**Total Time:** ~2-4 minutes per workflow (excluding HITL approval time)

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** - Agent orchestration framework
- **Gemini** - Code generation LLM
- **Playwright** - Browser automation
- **Tavily** - Dataset search API
- **FastAPI** - Modern Python web framework
- **React** - Frontend UI library

## 📧 Contact

**Lakshman** - [@lakshmanbunny](https://github.com/lakshmanbunny)

**Project Link:** [https://github.com/lakshmanbunny/Multi-Agentic-Major-Project](https://github.com/lakshmanbunny/Multi-Agentic-Major-Project)

---

⭐ **Star this repo if you find it useful!**
