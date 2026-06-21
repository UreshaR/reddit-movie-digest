"""
Optional: interactive Q&A over the embedded Reddit comments (run after
clean_data.py -> create_embeddings.py -> build_faiss_index.py).
Not required for the film-digest output - see summarize_movies.py for that.
"""

import json
import numpy as np
import faiss

from llm_client import ask_groq
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
index = faiss.read_index("reddit.index")

with open("documents_store.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

while True:
    question = input("\nAsk a question (or 'exit'): ")
    if question.lower() == "exit":
        break

    query_vector = model.encode(question)
    query_vector = np.array([query_vector]).astype("float32")

    distances, indices = index.search(query_vector, k=5)
    contexts = [docs[idx]["text"] for idx in indices[0]]

    prompt = (
        "You are analyzing Reddit discussions. Use ONLY these comments.\n\n"
        f"Comments:\n{chr(10).join(contexts)}\n\n"
        f"Question:\n{question}\n\n"
        "Provide:\n1. Overall opinion\n2. Positive opinions\n"
        "3. Negative opinions\n4. Final summary"
    )

    answer = ask_groq(prompt)

    print("\n========== ANSWER ==========\n")
    print(answer)

    print("\n========== RETRIEVED COMMENTS ==========\n")
    for idx in indices[0]:
        print("--------------------------------")
        print(docs[idx]["text"])
        print("Post:", docs[idx]["metadata"]["title"])
