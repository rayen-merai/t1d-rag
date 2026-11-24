from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")

def embed_passages(texts):
    return model.encode([f"passage: {t}" for t in texts],
                        normalize_embeddings=True, show_progress_bar=True).tolist()

def embed_query(q):
    return model.encode([f"query: {q}"], normalize_embeddings=True).tolist()