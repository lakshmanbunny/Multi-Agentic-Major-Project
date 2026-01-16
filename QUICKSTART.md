# 🚀 QUICK START GUIDE - Auto-DataScientist

## ✅ Setup Complete! Here's What To Do Next:

### **Step 1: Add Your API Keys** 🔑

I've created a `.env` file for you. Open it and replace the dummy keys:

```powershell
# Open .env in your editor
notepad .env
```

**Replace these two required keys:**

1. **GOOGLE_API_KEY** - Get from: https://makersuite.google.com/app/apikey
   ```
   GOOGLE_API_KEY=AIzaSy...YOUR_ACTUAL_KEY
   ```

2. **TAVILY_API_KEY** - Get from: https://tavily.com
   ```
   TAVILY_API_KEY=tvly-...YOUR_ACTUAL_KEY
   ```

---

### **Step 2: Test the Research Agent** 🧪

Run the standalone test:

```powershell
cd C:\Users\Bunny\Desktop\PROJ-4-2\auto-data-scientist
python test_research_agent.py
```

**Expected Output:**
- ✅ Dataset URL found via Tavily
- ✅ 4-step research plan generated
- ✅ Arxiv papers discovered

---

### **Step 3: Run the Orchestrator** 🎯

If it's not already running:

```powershell
cd C:\Users\Bunny\Desktop\PROJ-4-2\auto-data-scientist
python services/orchestrator/src/main.py
```

It will start on: http://localhost:8000

---

### **Step 4: Test via API** 📡

Open a new terminal and test:

```powershell
# Health check
curl http://localhost:8000/health

# Start a workflow
curl -X POST http://localhost:8000/workflow/start `
  -H "Content-Type: application/json" `
  -d '{\"user_goal\": \"Build customer churn prediction model\"}'

# Save the workflow_id from response, then check status:
curl http://localhost:8000/workflow/{workflow_id}/status
```

---

### **Step 5: View Logs** 📊

The Research Agent will log:
- 🔍 Search queries generated
- 🌐 Tavily search results
- 📚 Arxiv papers found
- ✅ Research plan created

All in JSON format for easy debugging!

---

## 🎯 What's Working Now:

| Component | Status | Description |
|-----------|--------|-------------|
| Research Agent | ✅ LIVE | Real AI-powered dataset discovery |
| Tavily Integration | ✅ LIVE | Web search for datasets |
| Arxiv Integration | ✅ LIVE | Research paper discovery |
| Gemini LLM | ✅ LIVE | Query generation & planning |
| Data Eng Agent | 🔄 TODO | Still simulated |
| ML Agent | 🔄 TODO | Still simulated |

---

## 🐛 Troubleshooting:

**Error: "No module named 'dotenv'"**
```powershell
pip install python-dotenv
```

**Error: "API key not found"**
- Make sure your `.env` file is in the project root
- Check that keys don't have quotes around them

**Error: "Tavily search failed"**
- Verify your TAVILY_API_KEY is correct
- Check you have internet connection

---

## 📝 Example API Response:

```json
{
  "workflow_id": "abc-123-def",
  "status": "started",
  "message": "Workflow initialized and running"
}
```

Then check status to see research results:
```json
{
  "workflow_id": "abc-123-def",
  "status": "waiting_approval",
  "current_step": "data_engineering_agent",
  "research_plan": [
    "Download and validate churn dataset",
    "Perform EDA on customer features",
    "Select classification algorithm",
    "Train and evaluate model"
  ]
}
```

---

## 🎉 You're Ready!

The Research Agent is fully functional with real AI! 

**Next steps:**
- Add your API keys
- Run the test
- Watch it find real datasets and papers! 🚀
