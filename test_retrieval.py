import chromadb, textwrap
from rag_utils import embed_query

col = chromadb.PersistentClient("chroma_db").get_collection("t1d")
for q in ["What causes type 1 diabetes?", "How is type 1 diabetes diagnosed?"]:
    res = col.query(query_embeddings=embed_query(q), n_results=4)
    print("\n" + "=" * 80 + f"\nQ: {q}")
    for d, m in zip(res["documents"][0], res["metadatas"][0]):
        print(f"\n[p. {m['page']}]\n{textwrap.fill(d, 100)}")