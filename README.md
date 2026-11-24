# Type 1 Diabetes RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about type 1 diabetes
using a single research paper as its only source. Runs fully locally (no API key needed)
and answers in French, with page citations.

## Features
- Answers grounded only in the provided paper, with page references (p. X)
- Multilingual retrieval: ask in French or English
- Local LLM through Ollama (private and free)
- Two interfaces: terminal chat and Streamlit web app (reachable on your local network)

## How it works
1. `ingest.py` extracts the PDF text, drops the reference list, splits it into chunks
   and stores their embeddings in ChromaDB.
2. For each question, the 6 most similar chunks are retrieved.
3. A local LLM (Qwen 2.5 via Ollama) writes the answer from those chunks only.

## Requirements
- Python 3.10 to 3.12
- [Ollama](https://ollama.com) installed and running
- About 8 GB of RAM for the 7B model

## Setup
```bash
git clone https://github.com/rayen-merai/t1d-rag.git
cd t1d-rag

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
ollama pull qwen2.5:7b
```

Place your PDF at `data/paper.pdf`, then build the index:
```bash
python ingest.py
```

## Usage
Terminal chat:
```bash
python chat.py
```
Web app (also opens on your local network at `http://<your-ip>:8501`):
```bash
streamlit run app.py
```

Example questions:
- Quelles sont les causes du diabète de type 1 ?
- Comment le diagnostique-t-on ?
- Quelles sont les complications possibles ?

## Project structure
```
t1d-rag/
├── data/               # put paper.pdf here (not committed)
├── .streamlit/
│   └── config.toml     # network settings
├── ingest.py           # PDF -> chunks -> vector index
├── rag_utils.py        # embedding model
├── rag_core.py         # retrieval + answer generation
├── chat.py             # terminal interface
├── app.py              # Streamlit interface
├── test_retrieval.py   # check retrieved chunks
└── requirements.txt
```

## Configuration
- Change the LLM: edit `MODEL` in `rag_core.py` (for example `qwen2.5:3b` for low RAM).
- Change the embedding model in `rag_utils.py`, then re-run `ingest.py`.

## Disclaimer
This project is for educational purposes only. It is not medical advice.
Always consult a healthcare professional.

## Source
Nature Reviews Diseases Primers volume 3 article number 17016 (2017)
The paper is not included in this repository because of copyright.

Authors:
Anastasia Katsarou1, Soffia Gudbjörnsdottir2,3, Araz Rawshani2,3, Dana Dabelea4, Ezio Bonifacio5, Barbara J. Anderson6, Laura M. Jacobsen7, Desmond A. Schatz7 and Åke Lernmark1
Correspondence to Å.L. Department of Clinical Sciences, Lund University, Skåne University Hospital, Jan Waldenströms gata 35, 20502 Malmö, Sweden.
