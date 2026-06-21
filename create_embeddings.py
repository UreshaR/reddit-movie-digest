import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

with open("documents.json", "r", encoding="utf-8") as f:
    documents = json.load(f)

for i, doc in enumerate(documents):
    embedding = model.encode(doc["text"])
    doc["embedding"] = embedding.tolist()
    print(f"Processed {i + 1}/{len(documents)}")

with open("documents_store.json", "w", encoding="utf-8") as f:
    json.dump(documents, f, ensure_ascii=False)

print("Embeddings created")
