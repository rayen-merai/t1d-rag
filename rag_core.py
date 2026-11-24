import chromadb, ollama
from rag_utils import embed_query

MODEL = "qwen2.5:7b"
col = chromadb.PersistentClient("chroma_db").get_collection("t1d")

SYSTEM = (
    "Tu es un assistant qui répond aux questions sur le diabète de type 1 "
    "en utilisant UNIQUEMENT les extraits fournis, issus d'un article de recherche "
    "(souvent en anglais). Réponds TOUJOURS en français, avec la terminologie "
    "médicale française, même si la question ou les extraits sont dans une autre langue. "
    "Donne une réponse complète et structurée : courte introduction, puis des puces "
    "couvrant tous les détails pertinents des extraits. "
    "Si la réponse n'est pas dans les extraits, dis que tu ne la trouves pas dans le document. "
    "Cite les pages sous la forme (p. 3). "
    "Tu n'es pas médecin : ne donne jamais de doses ni de conseils de traitement personnels."
)

def answer_stream(question, k=6):
    res = col.query(query_embeddings=embed_query(question), n_results=k)
    ctx = "\n\n".join(f"[p. {m['page']}] {d}"
                      for d, m in zip(res["documents"][0], res["metadatas"][0]))
    stream = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",
             "content": f"Extraits :\n{ctx}\n\nQuestion : {question}\n\nRéponds en français."},
        ],
        options={"num_ctx": 8192, "temperature": 0.2},
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]