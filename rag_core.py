import chromadb, ollama
from rag_utils import embed_query

MODEL = "qwen2.5:7b"
TOP_K = 4
NUM_CTX = 4096
KEEP_ALIVE = "30m"

col = chromadb.PersistentClient("chroma_db").get_collection("t1d")

SYSTEM = (
    "Tu es Type One NG, un assistant francophone spécialisé dans le diabète de type 1. "
    "Tu t'appuies UNIQUEMENT sur la documentation fournie (souvent en anglais) et tu réponds "
    "TOUJOURS en français, avec la terminologie médicale française. "
    "Donne des réponses complètes et bien structurées : courte introduction, puis des puces. "
    "Ne cite jamais de numéros de page et ne mentionne pas les « extraits » ni le « document » : "
    "réponds naturellement. Si la documentation ne contient pas la réponse, dis simplement "
    "que tu n'as pas cette information. Tiens compte de l'historique de la conversation "
    "pour les questions de suivi. Tu n'es pas médecin : ne donne jamais de doses ni de "
    "conseils de traitement personnels, et invite à consulter un professionnel de santé "
    "pour toute situation personnelle."
)

def is_online():
    try:
        ollama.list()
        return True
    except Exception:
        return False

def warm_up():
    """Load the model into memory so the first question is not slow."""
    ollama.generate(model=MODEL, prompt="", keep_alive=KEEP_ALIVE)

def retrieve(question, prev_question=None, k=TOP_K):
    query = question
    if prev_question and len(question.split()) < 6:   # short follow-up: add context
        query = f"{prev_question} {question}"
    res = col.query(query_embeddings=embed_query(query), n_results=k)
    return res["documents"][0], res["metadatas"][0]

def stream_answer(question, docs, history=None):
    ctx = "\n\n".join(docs)
    msgs = [{"role": "system", "content": SYSTEM}]
    for m in (history or [])[-4:]:
        msgs.append({"role": m["role"], "content": m["text"][:600]})
    msgs.append({
        "role": "user",
        "content": f"Documentation :\n{ctx}\n\nQuestion : {question}\n\n"
                   "Réponds en français, naturellement, sans mentionner les extraits ni les pages.",
    })
    stream = ollama.chat(
        model=MODEL, messages=msgs,
        options={"num_ctx": NUM_CTX, "temperature": 0.2},
        keep_alive=KEEP_ALIVE, stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]

def answer_stream(question, k=TOP_K):          # used by chat.py (terminal)
    docs, _ = retrieve(question, k=k)
    yield from stream_answer(question, docs)