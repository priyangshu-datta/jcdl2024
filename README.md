# This is the RAG-DME method branch.

1. Clone the repo.
2. Use the `extract_datasets` function.

```py
from src.rag_dme import extract_datasets, GenerativeServiceClient, ChromaPersist
from pathlib import Path

chromaDB = ChromaPersist(name="", path=Path(""))
gsc = GenerativeServiceClient()

print(extract_datasets(chromaDB=chromaDB, gsc=gsc, full_text=""))
```

## Dependencies
All the mentioned dependencies are mentioned in ``requirements.txt`` file, and is installed during setup.
1. ChromaDB - a vector database, used for storing documents and retrieving relevant documents.
2. Google's Generative Language API - the API for Google's AI models.