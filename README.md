# HR Resume AI

A local AI-powered HR resume assistant that can ingest resumes, search candidates by skills and experience, rank relevant candidates, and use a local LLM to generate grounded responses.

The project is being built locally first for learning and portfolio purposes, with the option to later deploy the architecture to Azure or GCP.

---

## 1. Project Goal

The goal is to build an AI application where an HR user can ask questions such as:

- Find candidates with Python and Azure experience.
- Which candidates have Kubernetes experience?
- Find a data engineer with BigQuery and Dataflow experience.
- Compare candidates based on a job requirement.
- Explain why a candidate matches the requirement.

The planned application will combine:

- Resume ingestion
- Text extraction
- Text chunking
- Embeddings
- Vector search
- Metadata/keyword search
- Candidate ranking
- RAG
- Local LLM
- Streamlit UI
- FastAPI
- Testing and evaluation
- Docker
- CI/CD
- Monitoring
- Optional cloud deployment

---

# 2. Current Architecture

The planned high-level architecture is:

```text
                         HR User
                            |
                            v
                      Streamlit UI
                            |
                            v
                     FastAPI / App
                            |
             +--------------+--------------+
             |                             |
             v                             v
       Semantic Search              Metadata Search
          (FAISS)                      (SQLite)
             |                             |
             +--------------+--------------+
                            |
                            v
                    Candidate Ranker
                            |
                            v
                         RAG
                            |
                            v
                    Local LLM (Ollama)
                            |
                            v
                Grounded HR Response
```

The ingestion side is:

```text
Resume PDF
    |
    v
PDF Parser
    |
    v
Extracted Text
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
FAISS
```

---

# 3. Project Structure

Current/planned structure:

```text
hr-resume-ai/
│
├── data/
│   ├── resumes/
│   └── processed/
│
├── ingestion/
│   ├── pdf_parser.py
│   ├── test_parser.py
│   └── ingest.py
│
├── embeddings/
├── retrieval/
├── llm/
│   └── ollama_client.py
├── api/
├── ui/
├── evaluation/
├── tests/
│
├── .gitignore
├── README.md
├── requirements.txt
└── app.py
```

---

# 4. Development Environment

The project uses a project-specific Python virtual environment.

Project path:

```text
D:\Projects\Hr_chatbot\hr-resume-ai
```

Virtual environment:

```text
D:\Projects\Hr_chatbot\hr-resume-ai\.venv
```

It is important to use the project's `.venv` so that packages are installed into the correct environment.

Recommended check:

```powershell
python -c "import sys; print(sys.executable)"
```

Expected result should point to:

```text
D:\Projects\Hr_chatbot\hr-resume-ai\.venv\Scripts\python.exe
```

---

# 5. Git / GitHub

The project is maintained in a Git repository so multiple team members can work on it.

Recommended branch structure:

```text
main
  |
  develop
  |
  +-- feature/ingestion
  +-- feature/chunking
  +-- feature/embeddings
  +-- feature/retrieval
  +-- feature/rag
  +-- feature/ui
```

The `main` branch should contain stable code.

Feature branches should be used for individual pieces of work and merged through pull requests.

---

# 6. Python Dependencies Installed So Far

Important packages installed so far include:

- `ollama`
- `streamlit`
- `pymupdf`

The full environment has also been captured using:

```powershell
pip freeze > requirements.txt
```

This creates `requirements.txt` so the environment can be recreated later.

---

# 7. Local LLM Setup

The project uses Ollama so that the initial application can run without paid LLM APIs.

Local models available during development:

```text
qwen3:8b
llama3.2:latest
```

The project can therefore communicate with an LLM running locally.

This avoids sending resume data to an external API during local development.

---

# 8. Testing Python → Ollama

We successfully tested communication between Python and Ollama.

The LLM client is separated into:

```text
llm/ollama_client.py
```

Example implementation:

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

The purpose of this module is to provide a simple interface:

```text
Application
    |
    v
generate_response()
    |
    v
Ollama
    |
    v
Local LLM
```

The model can be changed later without changing the rest of the application.

---

# 9. Streamlit UI

A basic Streamlit application was created in:

```text
app.py
```

Basic version:

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

A later version connects the UI to the local LLM:

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

## Running Streamlit

Do not run the Streamlit application using:

```powershell
python app.py
```

Instead use:

```powershell
streamlit run app.py
```

Running it as a normal Python script produces Streamlit `ScriptRunContext` and session-state warnings because Streamlit expects to launch the application through its CLI.

---

# 10. PDF Parsing

The first actual resume-processing component is the PDF parser.

File:

```text
ingestion/pdf_parser.py
```

Current implementation:

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

## How it works

```text
PDF path
   |
   v
pymupdf.open()
   |
   v
PDF document
   |
   v
Loop through pages
   |
   v
page.get_text()
   |
   v
Collect page text
   |
   v
Join all pages
   |
   v
Return complete text
```

The parser is intentionally generic.

It does not know which specific resume it is processing.

It simply receives a PDF path and returns its extracted text.

---

# 11. PDF Parser Test

File:

```text
ingestion/test_parser.py
```

Current test:

```python
from pdf_parser import extract_text_from_pdf


pdf_path = "data/resumes/test_resume.pdf"

text = extract_text_from_pdf(pdf_path)


print("=" * 60)
print("EXTRACTED RESUME TEXT")
print("=" * 60)

print(text)
```

The test file is responsible for:

1. Selecting a PDF.
2. Calling the PDF parser.
3. Receiving the extracted text.
4. Printing the result.

The separation is:

```text
test_parser.py
      |
      | calls
      v
pdf_parser.py
      |
      | uses
      v
PyMuPDF
      |
      v
PDF text
```

The parser was successfully tested and the PDF was confirmed to be parsed correctly.

---

# 12. Multi-Resume Ingestion

After successfully parsing a single PDF, the next component is the multi-resume ingestion pipeline.

File:

```text
ingestion/ingest.py
```

Current implementation:

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
                ensure_ascii=False
            )

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    ingest_resumes()
```

---

# 13. How `ingest.py` Works

The ingestion pipeline is:

```text
data/resumes/
     |
     +-- resume_1.pdf
     +-- resume_2.pdf
     +-- resume_3.pdf
             |
             v
        ingest.py
             |
             v
        pdf_parser.py
             |
             v
      Extracted resume text
             |
             v
       Structured dictionary
             |
             v
        JSON output
             |
             v
data/processed/
     |
     +-- resume_1.json
     +-- resume_2.json
     +-- resume_3.json
```

---

# 14. Input and Output

Input:

```text
data/resumes/
├── resume_1_aarav_sharma.pdf
├── resume_2_priya_narayanan.pdf
└── resume_3_rohan_mehta.pdf
```

Output:

```text
data/processed/
├── resume_1_aarav_sharma.json
├── resume_2_priya_narayanan.json
└── resume_3_rohan_mehta.json
```

Each JSON file contains:

```json
{
    "resume_id": "resume_1_aarav_sharma",
    "filename": "resume_1_aarav_sharma.pdf",
    "text": "Extracted resume text..."
}
```

This gives us a clean intermediate representation of each resume.

---

# 15. Running the Ingestion Pipeline

From the project root:

```powershell
cd D:\Projects\Hr_chatbot\hr-resume-ai
```

Run:

```powershell
python .\ingestion\ingest.py
```

Expected output:

```text
Found 3 PDF resumes.

Processing: resume_1_aarav_sharma.pdf
Saved: data\processed\resume_1_aarav_sharma.json

Processing: resume_2_priya_narayanan.pdf
Saved: data\processed\resume_2_priya_narayanan.json

Processing: resume_3_rohan_mehta.pdf
Saved: data\processed\resume_3_rohan_mehta.json
```

To inspect the output files:

```powershell
Get-ChildItem .\data\processed
```

To inspect a JSON file:

```powershell
Get-Content .\data\processed\resume_1_aarav_sharma.json
```

---

# 16. Sample Test Resumes

Three synthetic sample resumes were created for local testing:

### Resume 1 — Cloud DevOps Engineer

Skills include:

```text
GCP
Azure
Kubernetes
GKE
Docker
Terraform
GitHub Actions
Jenkins
Python
BigQuery
Dataflow
```

### Resume 2 — AI / ML Engineer

Skills include:

```text
Python
Machine Learning
NLP
RAG
LangChain
FastAPI
PyTorch
Hugging Face
Azure AI
Azure AI Foundry
Docker
Kubernetes
Embeddings
Vector Databases
```

### Resume 3 — Data Engineer

Skills include:

```text
Python
SQL
GCP
BigQuery
Dataflow
Apache Beam
Cloud Storage
Apache Spark
Airflow
Kafka
Docker
Terraform
```

These different profiles will be useful later when testing semantic search and candidate ranking.

---

# 17. Current Progress

Completed:

```text
[x] Project goal defined
[x] Project structure created
[x] Git/GitHub workflow planned
[x] Project-specific Python virtual environment
[x] Ollama installed
[x] Local LLM models available
[x] Python → Ollama tested
[x] Streamlit installed
[x] Basic Streamlit application
[x] PyMuPDF installed
[x] PDF parser created
[x] PDF parser tested
[x] Multi-resume ingestion created
[x] JSON processing output created
[x] Sample resumes created
```

Current pipeline:

```text
PDF Resume
    |
    v
PDF Parser
    |
    v
Extracted Text
    |
    v
JSON
```

---

# 18. Next Step — Chunking

The next component is **resume chunking**.

Currently a resume is stored as one large piece of text:

```text
Entire Resume
--------------------------------
Summary
Experience
Skills
Education
Projects
Certifications
...
--------------------------------
```

For RAG and semantic search, we need to divide it into smaller meaningful chunks.

The next pipeline will be:

```text
JSON Resume
     |
     v
Text
     |
     v
Chunker
     |
     +--> Chunk 1
     +--> Chunk 2
     +--> Chunk 3
     +--> Chunk 4
     |
     v
Embedding Model
```

Example:

```text
Resume
   |
   +--> Summary chunk
   |
   +--> Skills chunk
   |
   +--> Experience chunk
   |
   +--> Education chunk
```

These chunks will eventually be converted into embeddings and stored in FAISS.

---

# 19. Overall Learning Roadmap

The complete planned build order is:

```text
1.  Project setup                    [DONE]
2.  PDF parsing                     [DONE]
3.  Multi-resume ingestion          [DONE]
4.  Resume chunking                  [NEXT]
5.  Embedding model
6.  FAISS vector store
7.  Semantic search
8.  Search validation
9.  SQLite candidate metadata
10. Hybrid retrieval
11. Ollama integration               [PARTIALLY DONE]
12. RAG
13. Candidate ranking
14. Recommendations
15. Evidence / grounding
16. Streamlit UI integration
17. Conversational search
18. Evaluation dataset
19. Automated tests
20. FastAPI
21. Docker
22. CI/CD
23. Observability
24. Performance optimization
25. Cloud deployment
```

---

# 20. Important Design Principles

### Local-first

The initial application should work without paid external APIs.

```text
Resume
  ↓
Local processing
  ↓
Local embeddings
  ↓
Local vector database
  ↓
Local LLM
```

### Modular design

Each component should have one primary responsibility:

```text
PDF Parser
    → Extract PDF text

Ingestion
    → Process multiple resumes

Chunker
    → Split text

Embedder
    → Create vectors

Retriever
    → Find relevant chunks

Ranker
    → Rank candidates

RAG
    → Build grounded LLM context

LLM
    → Generate response

UI
    → Interact with HR user
```

### Evidence-based responses

The final system should not simply ask an LLM to guess which candidate is best.

It should retrieve resume evidence first:

```text
HR Query
   |
   v
Retrieve relevant resume chunks
   |
   v
Rank candidates
   |
   v
Provide evidence
   |
   v
LLM generates explanation
```

### HR privacy

Real resumes should not be committed to the public Git repository.

Use synthetic/anonymized resumes for development whenever possible.

Candidate ranking should focus on job-relevant information and should support human review rather than making autonomous hiring decisions.

---

## Current Status

**Completed through multi-resume ingestion.**

**Next task: Build the resume chunking component.**
