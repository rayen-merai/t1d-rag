import sys
from rag_core import answer_stream

sys.stdout.reconfigure(encoding="utf-8")

print("Assistant diabète de type 1 — tapez 'quit' pour quitter")
while True:
    try:
        q = input("\nQuestion > ").strip()
    except (EOFError, KeyboardInterrupt):
        break
    if q.lower() in {"quit", "exit", "q"}:
        break
    if not q:
        continue
    print("\nRéponse :\n")
    for token in answer_stream(q):
        print(token, end="", flush=True)
    print()