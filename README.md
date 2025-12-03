# Smart Resume & Cover Letter Generator — Backend  
FastAPI backend powering AI-driven resume improvement, summary rewriting, and cover-letter generation.


---

## Overview  
This backend system enables users to:

- Upload their resume (.pdf or .txt)
- Provide a job description
- Receive AI-generated resume improvement suggestions
- Rewrite the resume summary to match a job posting  
- Generate a personalized cover letter based on resume + JD  
- Receive structured, clean JSON responses that the frontend can directly render

The system emphasizes:

- **Truthful, non-hallucinated AI responses**
- **ATS-friendly output**
- **Fast, reliable API performance**
- **Robust, consistent architecture**
- **Separation of concerns: routers → services → AI client**

---

# Features

### Resume Upload & Parsing  
- Supports PDF and plain-text files  
- Uses PyPDF2 for extraction  
- Cleans/normalizes text before sending to AI  
- Automatically handles messy, differently formatted resumes  

### ✔ Smart Resume Suggestions  
Given a resume + job description, backend returns:

```json
{
  "suggestions": [
    "Add a measurable impact to bullet: 'reduced processing time by 30%'",
    "Highlight technologies from JD that you already use in your experience",
    "Strengthen action verbs in weaker bullets"
  ]
}
```

Suggestions are:
- Based ONLY on real resume content  
- Never fabricated  
- Highly actionable  
- Aimed at matching ATS scoring patterns  

### Summary Rewriter  
Uploads a resume → system extracts text → rewrites the summary ONLY.

The rewrite:
- Must stay factual  
- Must match the JD requirements  
- Must remain concise and professional  

### Cover Letter Generator  
User enters:
- job title  
- company  
- job description  
- resume text extracted from upload  

System returns:
- A 3–5 paragraph personalized cover letter  
- In JSON form  
- Professional, specific, and role-aligned  

### HuggingFace AI Integration  
Backend uses:
- `google/gemma-2-2b-it`  
- HuggingFace **InferenceClient**  
- Automatic fallback between:
  - `.text_generation` (if supported)
  - `.chat.completions` (conversational mode)

### Strict Anti-Hallucination Prompts  
Prompts explicitly instruct the model:

- **Do NOT create skills or experiences**
- **Use ONLY the resume + JD**
- **Follow exact JSON output structure**

---

# Architecture

## High-Level System Architecture
```
Frontend (React)
    |
    |  POST resume + JD
    v
FastAPI Backend
    |
    ├── Routers (career.py)
    ├── Services (CareerService)
    │       ├── ResumeTextExtractor
    │       └── HuggingFaceClient
    ├── Models (Pydantic)
    └── Utils (PDF parser)
    |
    v
HuggingFace Inference API
```

This separation of layers ensures maintainability, testability, and clean data flow.

---

# API Endpoints

### 1. Upload Resume → Suggestions  
`POST /api/career/smart-resume-upload`

### 2. Upload Resume → Rewritten Summary  
`POST /api/career/rewrite-summary-upload`

### 3. Cover Letter Generator  
`POST /api/career/cover-letter`

All responses are JSON.

---

# Installation & Setup

Copy/paste these instructions into your development runbook.

### **1. Clone repository**
```bash
git clone https://github.com/Sandeeparavind/SmartResume-CoverLetterGenerator-backend.git
cd SmartResume-CoverLetterGenerator-backend
```

### **2. Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
```

### **3. Install dependencies**
```bash
pip install -r requirements.txt
```

### **4. Set up `.env`**
Create a `.env` file at project root:

```
HF_API_KEY=your_huggingface_api_key_here
HF_MODEL=google/gemma-2-2b-it
```

### **5. Run the backend**
```bash
uvicorn app.main:app --reload
```

Open API docs:  
    http://127.0.0.1:8000/docs

---

# Testing

### Run all tests:
```bash
pytest -vv
```

### How tests work
- Uses `TestClient` from FastAPI  
- **HuggingFace API is monkeypatched** so no calls hit the real network  
- Tests are deterministic and fast  
- No tokens or external dependencies required  

---

# Security & Privacy

This project handles resumes →  make strong design choices:

### ✔ No resume text is ever logged  
### ✔ HF token is stored only in `.env`  
### ✔ Backend does short-lived, in-memory processing  
### ✔ Frontend-to-backend communication uses structured JSON  
### ✔ AI prompts include anti-hallucination constraints  

---

# Deployment

You may deploy using:

- Docker  
- Render  
- Railway  
- Azure App Service  
- AWS Lightsail  
- HuggingFace Spaces (as API-only backend)

**Important:** Always add your HF API key as an environment secret, never commit `.env`.

---

# Technical Challenges & Solutions

### **1. HuggingFace Model Compatibility Issues**
- Some endpoints deprecated (`api-inference.huggingface.co`)
- Model supports conversational → not text-generation
- Solution: **Fallback mechanism** in `_call_model()`

### **2. PDF Parsing Warnings**
- Solved by robust extraction + normalization  
- Warnings are harmless, handled gracefully  

### **3. Preventing Hallucinations**
- Heavy prompt engineering  
- Explicit rules like:  
  > "Use only the resume and JD. Do not invent details."

### **4. Clean JSON Parsing**
- Strict format enforcement  
- Auto-correction for malformed AI outputs  

---


# Lessons Learned

- AI integration requires flexibility due to rapid API changes  
- Clear prompts dramatically improve output consistency  
- Robust architecture reduces debugging time  
- Test mocks (monkeypatching) are essential for LLM-based systems  
- Separating routers → services → AI client is the correct architecture  

---

# 📄 License  
For academic and demonstration purposes only.

---


