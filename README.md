LearnEase AI
AI-powered Course Content Simplification Agent using IBM watsonx.ai and IBM Granite.
Features
Simple explanations
Structured notes
Examples
Exam questions and answers
Quick summaries
Downloadable study material
Run on Windows
Install Python 3.10+ and open this folder in VS Code.
Open Terminal > New Terminal.
Run:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Copy `.env.example` to `.env`.
Add your IBM Cloud API key, watsonx.ai Project ID, region URL, and an available Granite model ID.
Run:
```powershell
streamlit run app.py
```
Keep `.env` private. Never upload API keys to GitHub or show them in screenshots.
This starter is a single-prompt AI app. It does not claim to implement RAG or multiple autonomous agents.