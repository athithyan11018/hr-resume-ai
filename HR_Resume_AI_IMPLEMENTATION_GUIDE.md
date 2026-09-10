# HR Resume AI — Step-by-Step Implementation Guide

This guide explains how to build the HR Resume AI project from scratch.

It is written so that another developer can clone the repository and follow the implementation steps without needing the original project discussion.

---

# 1. Project Overview

We are building a local AI-powered HR resume assistant.

The application will eventually allow an HR user to ask questions such as:

- Find candidates with Python and Azure experience.
- Which candidates have Kubernetes experience?
- Find data engineers with BigQuery and Dataflow experience.
- Which candidate best matches this job requirement?
- Why does this candidate match the requirement?

The initial implementation is intentionally **local-first**.

We will use:

- Python
- PyMuPDF
- JSON
- Sentence Transformers
- FAISS
- SQLite
- Ollama
- Streamlit
- FastAPI
- pytest
- Docker
- CI/CD

The project can later be extended to Azure or GCP.

---

# 2. Final Target Architecture

The final application is planned to look like:

```text
                         HR User
                            |
                            v
                      Streamlit UI
                            |
                            v
                    FastAPI / App Layer
                            |
              +-------------+-------------+
              |                           |
              v                           v
        Semantic Search            Metadata Search
            FAISS                      SQLite
              |                           |
              +-------------+-------------+
                            |
                            v
                    Candidate Ranker
                            |
                            v
                         RAG
                            |
                            v
                    Local LLM / Ollama
                            |
                            v
              Grounded Candidate Response
```

The ingestion pipeline is:

```text
PDF / DOCX
    |
    v
Parser
    |
    v
Text Cleaning
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
FAISS + Metadata
```

---

# 3. Prerequisites

Before starting, install:

- Python 3.x
- Git
- VS Code or another code editor
- Ollama

Verify Python:

```powershell
python --version
```

Verify Git:

```powershell
git --version
```

Verify Ollama:

```powershell
ollama --version
```

---

# 4. Clone the Repository

Clone the GitHub repository:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Enter the project:

```powershell
cd hr-resume-ai
```

---

# 5. Create the Project Structure

Create:

```text
hr-resume-ai/
│
├── data/
│   ├── resumes/
│   └── processed/
│
├── ingestion/
├── embeddings/
├── retrieval/
├── llm/
├── api/
├── ui/
├── evaluation/
├── tests/
│
├── .gitignore
├── README.md
├── IMPLEMENTATION_GUIDE.md
├── requirements.txt
└── app.py
```

On Windows PowerShell:

```powershell
mkdir data
mkdir data\resumes
mkdir data\processed
mkdir ingestion
mkdir embeddings
mkdir retrieval
mkdir llm
mkdir api
mkdir ui
mkdir evaluation
mkdir tests
```

---

# 6. Create the Python Virtual Environment

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify that Python is coming from the project environment:

```powershell
python -c "import sys; print(sys.executable)"
```

It should point to:

```text
...\hr-resume-ai\.venv\Scripts\python.exe
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

---

# 7. Install Initial Dependencies

Install the initial packages:

```powershell
pip install pymupdf streamlit ollama
```

Later, additional packages will be installed for:

- Embeddings
- FAISS
- FastAPI
- Testing
- Evaluation

After installing dependencies:

```powershell
pip freeze > requirements.txt
```

---

# 8. Set Up Ollama

Install Ollama on the development machine.

Pull a local model:

```powershell
ollama pull llama3.2
```

Another model can also be used:

```powershell
ollama pull qwen3:8b
```

List available models:

```powershell
ollama list
```

Example:

```text
NAME
llama3.2:latest
qwen3:8b
```

The application should initially use a local model rather than a paid cloud API.

---

# 9. Test Ollama

Run:

```powershell
ollama run llama3.2
```

Enter a simple question:

```text
Explain RAG in simple terms.
```

Exit Ollama when finished.

The goal is to confirm that the local model works before integrating it into Python.

---

# 10. Create the Ollama Python Client

Create:

```text
llm/ollama_client.py
```

Add:

```python
from ollama import chat


MODEL_NAME = "llama3.2"


def generate_response(prompt: str) -> str:
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.message.content
```

This separates LLM communication from the rest of the application.

The application can simply call:

```python
generate_response(prompt)
```

without knowing the details of Ollama.

---

# 11. Create the Initial Streamlit Application

Create:

```text
app.py
```

Add:

```python
import streamlit as st


st.title("HR Resume AI Assistant")

st.write("Local AI resume assistant")

query = st.text_input(
    "Ask an HR question",
    placeholder="Find candidates with Python and Azure..."
)

if query:
    st.write("Your query:", query)
```

Run Streamlit:

```powershell
streamlit run app.py
```

IMPORTANT:

Do NOT run:

```powershell
python app.py
```

Streamlit applications should be started with:

```powershell
streamlit run app.py
```

---

# 12. Connect Streamlit to Ollama

Update `app.py`:

```python
import streamlit as st

from llm.ollama_client import generate_response


st.set_page_config(
    page_title="HR Resume AI",
    page_icon="🤖",
)

st.title("HR Resume AI Assistant")

st.write("Ask questions about candidates and resumes.")

query = st.text_area(
    "Enter your HR query",
    placeholder="Example: Find candidates with Python and Azure experience.",
)

if st.button("Ask AI"):

    if not query.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Thinking..."):

            answer = generate_response(query)

        st.subheader("AI Response")

        st.write(answer)
```

Run:

```powershell
streamlit run app.py
```

At this stage the LLM does not know anything about resumes yet.

That is expected.

RAG will be added later.

---

# 13. Add Resume PDFs

Place resume PDFs inside:

```text
data/resumes/
```

Example:

```text
data/
└── resumes/
    ├── resume_1.pdf
    ├── resume_2.pdf
    └── resume_3.pdf
```

For development, use synthetic or anonymized resumes.

Do not commit real candidate resumes to a public GitHub repository.

---

# 14. Build the PDF Parser

Create:

```text
ingestion/pdf_parser.py
```

Add:

```python
import pymupdf


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from all pages of a PDF."""

    document = pymupdf.open(pdf_path)

    text = []

    for page in document:

        page_text = page.get_text()

        text.append(page_text)

    document.close()

    return "\n".join(text)
```

The responsibility of this module is simple:

```text
PDF
 ↓
PyMuPDF
 ↓
Extract text
 ↓
Return string
```

It should not know anything about:

- embeddings
- FAISS
- LLMs
- Streamlit
- candidate ranking

---

# 15. Test the PDF Parser

Create:

```text
ingestion/test_parser.py
```

Add:

```python
from pdf_parser import extract_text_from_pdf


pdf_path = "data/resumes/test_resume.pdf"

text = extract_text_from_pdf(pdf_path)


print("=" * 60)
print("EXTRACTED RESUME TEXT")
print("=" * 60)

print(text)
```

Run from the project root:

```powershell
python .\ingestion\test_parser.py
```

Expected result:

```text
============================================================
EXTRACTED RESUME TEXT
============================================================
<resume text appears here>
```

If the resume text appears, PDF parsing is working.

---

# 16. Build Multi-Resume Ingestion

Create:

```text
ingestion/ingest.py
```

Add:

```python
from pathlib import Path
import json

from pdf_parser import extract_text_from_pdf


RESUME_DIR = Path("data/resumes")
OUTPUT_DIR = Path("data/processed")


def ingest_resumes():
    """Extract text from all PDF resumes and save them as JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(RESUME_DIR.glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF resumes.")

    for pdf_path in pdf_files:

        print(f"Processing: {pdf_path.name}")

        text = extract_text_from_pdf(str(pdf_path))

        resume_data = {
            "resume_id": pdf_path.stem,
            "filename": pdf_path.name,
            "text": text,
        }

        output_path = OUTPUT_DIR / f"{pdf_path.stem}.json"

        with open(output_path, "w", encoding="utf-8") as file:

            json.dump(
                resume_data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    ingest_resumes()
```

---

# 17. Run Multi-Resume Ingestion

Run:

```powershell
python .\ingestion\ingest.py
```

Expected:

```text
Found 3 PDF resumes.

Processing: resume_1.pdf
Saved: data\processed\resume_1.json

Processing: resume_2.pdf
Saved: data\processed\resume_2.json

Processing: resume_3.pdf
Saved: data\processed\resume_3.json
```

Verify:

```powershell
Get-ChildItem .\data\processed
```

Inspect a JSON file:

```powershell
Get-Content .\data\processed\resume_1.json
```

---

# 18. Understand the Current Pipeline

At this point:

```text
                    PDF RESUMES
                         |
                         v
                 ingestion.py
                         |
                         v
                pdf_parser.py
                         |
                         v
                  Extracted Text
                         |
                         v
                data/processed/
                         |
                         v
                    JSON files
```

Example JSON:

```json
{
    "resume_id": "resume_1",
    "filename": "resume_1.pdf",
    "text": "John Doe..."
}
```

This is our current working ingestion layer.

---

# 19. Next Step — Resume Chunking

Do not immediately send entire resumes to the embedding model.

A resume can contain a lot of text.

Instead, split it into smaller pieces.

Example:

```text
Complete Resume
       |
       +---- Summary
       |
       +---- Skills
       |
       +---- Experience
       |
       +---- Projects
       |
       +---- Education
```

Initially we can use a simple character/token-based chunker.

Create:

```text
ingestion/chunker.py
```

The chunker will eventually convert:

```text
Large resume text
       ↓
Chunk 1
Chunk 2
Chunk 3
Chunk 4
```

Each chunk should retain enough context to be useful during retrieval.

---

# 20. Embeddings

After chunking, convert every chunk into a numerical vector.

Conceptually:

```text
"Python developer with 5 years Azure experience"
                    |
                    v
             Embedding Model
                    |
                    v
        [0.12, -0.44, 0.73, ...]
```

These vectors allow us to perform semantic similarity search.

A query such as:

```text
"Find Azure Python developers"
```

can then retrieve semantically relevant resume chunks.

---

# 21. FAISS Vector Search

FAISS will store the embeddings.

Architecture:

```text
Resume Chunk
     |
     v
Embedding Model
     |
     v
Vector
     |
     v
FAISS
```

During a query:

```text
HR Query
   |
   v
Query Embedding
   |
   v
FAISS Search
   |
   v
Most Similar Resume Chunks
```

---

# 22. SQLite Metadata

FAISS is primarily responsible for vector similarity.

We will use SQLite for structured metadata.

Example:

```text
candidate_id
name
filename
skills
years_experience
location
education
```

Eventually:

```text
                 Query
                   |
          +--------+--------+
          |                 |
          v                 v
       FAISS             SQLite
   semantic search    metadata search
          |                 |
          +--------+--------+
                   |
                   v
            Hybrid Retrieval
```

---

# 23. Hybrid Retrieval

Pure semantic search may not always be enough.

For example, an HR user may require:

```text
Python
Azure
Kubernetes
5+ years
```

We can combine:

- Semantic similarity
- Keyword matching
- Metadata filtering

Example:

```text
Query
  |
  +--> Semantic Search
  |
  +--> Keyword Search
  |
  +--> Metadata Filters
  |
  v
Combined Results
```

---

# 24. Candidate Ranking

After retrieval, multiple candidates may be relevant.

We can calculate a ranking score based on job-relevant criteria.

Example concept:

```text
Candidate Score
=
Semantic Match
+
Required Skill Match
+
Experience Match
+
Other Job Criteria
```

The exact scoring approach will be implemented and evaluated rather than assuming that the LLM should make all ranking decisions.

The system should provide evidence supporting the ranking.

---

# 25. RAG

Once retrieval works, introduce Retrieval-Augmented Generation.

The flow becomes:

```text
HR Question
     |
     v
Retriever
     |
     v
Relevant Resume Chunks
     |
     v
Prompt Builder
     |
     v
Ollama
     |
     v
Grounded Answer
```

Example:

```text
HR:
"Find candidates with Python and Azure."

Retriever:
Candidate A:
"5 years Python..."
"3 years Azure..."

Candidate B:
"Python..."
"No Azure experience..."

LLM:
Produces an explanation based on retrieved evidence.
```

The LLM should not invent candidate experience.

---

# 26. Evidence and Grounding

Responses should identify the resume evidence used.

Example:

```text
1. Aarav Sharma
   Match: High

   Evidence:
   - Python experience
   - Azure experience
   - Kubernetes experience

2. Priya Narayanan
   Match: High

   Evidence:
   - Python
   - Azure AI
   - Kubernetes
```

This makes the system easier for an HR user to review.

---

# 27. Evaluation

Create a small evaluation dataset.

Example:

```text
Query:
"Find candidates with Python and Azure"

Expected:
Aarav Sharma
Priya Narayanan
```

Another:

```text
Query:
"Find candidates with BigQuery and Dataflow"

Expected:
Aarav Sharma
Rohan Mehta
```

Measure:

- Retrieval accuracy
- Precision
- Recall
- Ranking quality
- Grounding
- Response quality

---

# 28. Automated Tests

Use pytest.

Tests should eventually cover:

```text
PDF parser
Chunker
Embedding pipeline
Retriever
Metadata filtering
Ranking
RAG prompt construction
API
```

Example structure:

```text
tests/
├── test_pdf_parser.py
├── test_chunker.py
├── test_retrieval.py
├── test_ranking.py
└── test_api.py
```

---

# 29. FastAPI

After the core functionality works, move application logic behind an API.

Architecture:

```text
Streamlit
    |
    v
FastAPI
    |
    +--> Retriever
    +--> Ranker
    +--> RAG
    +--> Ollama
```

This separates the frontend from the backend.

---

# 30. Docker

Containerize the application.

Potential containers:

```text
Streamlit
FastAPI
Supporting services
```

The goal is to make the application reproducible on another machine.

---

# 31. CI/CD

Add GitHub Actions.

Pipeline:

```text
Developer
    |
    v
Git Push
    |
    v
GitHub
    |
    v
CI
    |
    +--> Install dependencies
    +--> Run tests
    +--> Run linting
    |
    v
Build
    |
    v
Deploy
```

---

# 32. Observability

Eventually track:

- API latency
- Retrieval latency
- LLM latency
- Number of retrieved chunks
- Errors
- Request counts
- Model performance
- Evaluation metrics

This will introduce practical MLOps/AI engineering concepts.

---

# 33. Cloud Deployment — Later

After the local implementation works, the architecture can be mapped to Azure or GCP.

Possible cloud evolution:

```text
LOCAL
------------------------------------------------
Streamlit
FastAPI
FAISS
SQLite
Ollama
Local embeddings


CLOUD
------------------------------------------------
Frontend
    |
API
    |
Managed vector/search service
    |
Cloud database
    |
Managed AI/LLM service
    |
Cloud monitoring
```

Cloud deployment should happen after the local architecture is understood.

This project is primarily intended as a learning project, so unnecessary enterprise infrastructure should not be added too early.

---

# 34. Recommended Git Workflow

Before starting a feature:

```powershell
git checkout develop
git pull
```

Create a feature branch:

```powershell
git checkout -b feature/chunking
```

Implement and test the feature.

Then:

```powershell
git add .
git commit -m "Add resume chunking"
git push -u origin feature/chunking
```

Create a Pull Request into `develop`.

After testing, merge to `develop`.

Keep `main` stable.

---

# 35. Important Git Ignore Rules

Do not commit:

```text
.venv/
__pycache__/
.env
data/resumes/
data/processed/
*.faiss
*.db
```

Real resumes and generated vector databases should generally remain outside the public repository.

Synthetic test resumes can be committed if appropriate.

---

# 36. Troubleshooting

## Python is using the wrong environment

Run:

```powershell
python -c "import sys; print(sys.executable)"
```

Make sure it points to:

```text
hr-resume-ai\.venv\Scripts\python.exe
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## Streamlit warnings

If you see messages about:

```text
missing ScriptRunContext
```

you probably launched Streamlit using:

```powershell
python app.py
```

Use:

```powershell
streamlit run app.py
```

---

## PDF file not found

Check:

```powershell
Get-ChildItem .\data\resumes
```

The PDF must actually exist in:

```text
data/resumes/
```

---

## PDF parser import error

When running:

```powershell
python .\ingestion\test_parser.py
```

the import:

```python
from pdf_parser import extract_text_from_pdf
```

works because Python includes the script's directory during execution.

As the project grows, convert the directories into proper Python packages and use cleaner package/module imports.

---

# 37. Development Milestones

## Milestone 1 — Ingestion

```text
[x] Project setup
[x] Virtual environment
[x] Git
[x] Ollama
[x] Streamlit
[x] PDF parser
[x] Multi-resume ingestion
[x] JSON output
```

## Milestone 2 — Retrieval

```text
[ ] Chunking
[ ] Embeddings
[ ] FAISS
[ ] Semantic search
[ ] SQLite metadata
[ ] Hybrid retrieval
```

## Milestone 3 — AI

```text
[ ] RAG
[ ] Candidate ranking
[ ] Evidence
[ ] Recommendations
[ ] Conversational search
```

## Milestone 4 — Engineering

```text
[ ] Automated tests
[ ] FastAPI
[ ] Docker
[ ] CI/CD
[ ] Monitoring
[ ] Evaluation
```

## Milestone 5 — Cloud

```text
[ ] Azure/GCP architecture
[ ] Cloud deployment
[ ] Managed services
[ ] Cloud monitoring
[ ] Cost optimization
```

---

# 38. Current Status

The project has completed the initial ingestion stage.

Current working flow:

```text
Resume PDF
    |
    v
PyMuPDF
    |
    v
Extracted Text
    |
    v
JSON
```

The next implementation task is:

```text
JSON Resume
    |
    v
Chunking
    |
    v
Resume Chunks
```

After chunking, the next major step is:

```text
Chunks
   |
   v
Embedding Model
   |
   v
Vectors
   |
   v
FAISS
```

---

# 39. Complete Build Order

Follow this order rather than implementing everything at once:

```text
1.  Create project
2.  Create virtual environment
3.  Install dependencies
4.  Set up Git
5.  Set up Ollama
6.  Test local LLM
7.  Create Ollama client
8.  Create Streamlit UI
9.  Add sample resumes
10. Build PDF parser
11. Test PDF parser
12. Build multi-resume ingestion
13. Save processed JSON
14. Build chunker              <-- CURRENT NEXT STEP
15. Test chunking
16. Install embedding model
17. Generate embeddings
18. Build FAISS index
19. Implement semantic search
20. Test retrieval
21. Add SQLite metadata
22. Implement hybrid retrieval
23. Implement candidate ranking
24. Implement RAG
25. Add evidence/grounding
26. Add recommendations
27. Connect Streamlit to RAG
28. Add conversational search
29. Build evaluation dataset
30. Add automated tests
31. Build FastAPI
32. Dockerize
33. Add CI/CD
34. Add observability
35. Optimize
36. Deploy to Azure/GCP
```

---

# 40. Golden Rule for the Team

Do not build the entire system at once.

At every stage:

```text
Implement
    ↓
Run
    ↓
Test
    ↓
Understand
    ↓
Commit
    ↓
Move to next component
```

The objective is not just to make an HR chatbot work.

The objective is to understand how a complete AI engineering system is built from:

```text
Data
 ↓
Ingestion
 ↓
Processing
 ↓
Embeddings
 ↓
Vector Search
 ↓
Retrieval
 ↓
Ranking
 ↓
RAG
 ↓
LLM
 ↓
API
 ↓
UI
 ↓
Testing
 ↓
CI/CD
 ↓
Observability
 ↓
Cloud
```

This makes the project useful both as a working application and as a practical AI engineering learning project.
