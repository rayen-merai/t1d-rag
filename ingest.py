import re, chromadb
from pypdf import PdfReader
from rag_utils import embed_passages

PDF = "data/paper.pdf"

def load_chunks(path, size=1500, overlap=250):
    chunks = []
    for page_no, page in enumerate(PdfReader(path).pages, 1):
        raw = page.extract_text() or ""
        m = re.search(r"^\s*References\s*$", raw, re.M)
        if m:
            raw = raw[:m.start()]
            print(f"References section found on page {page_no}, stopping there")
        text = " ".join(raw.split())
        for i in range(0, len(text), size - overlap):
            piece = text[i:i + size]
            # skip short pieces and anything that looks like a reference list
            if len(piece) > 150 and len(re.findall(r"\(\d{4}\)", piece)) < 3:
                chunks.append((piece, page_no))
        if m:
            break
    return chunks

chunks = load_chunks(PDF)
client = chromadb.PersistentClient("chroma_db")
try:
    client.delete_collection("t1d")
except Exception:
    pass
col = client.create_collection("t1d", metadata={"hnsw:space": "cosine"})

col.add(
    ids=[f"c{i}" for i in range(len(chunks))],
    documents=[c[0] for c in chunks],
    metadatas=[{"page": c[1]} for c in chunks],
    embeddings=embed_passages([c[0] for c in chunks]),
)
print(f"Indexed {len(chunks)} chunks")