import json
import numpy as np
import faiss

with open("documents_store.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

vectors = np.array([d["embedding"] for d in docs]).astype("float32")
dimension = vectors.shape[1]

index = faiss.IndexFlatL2(dimension)
index.add(vectors)

faiss.write_index(index, "reddit.index")

print("FAISS index saved")
