from pathlib import Path

from chromadb import PersistentClient
from chromadb.utils import embedding_functions

from helper.basics import chcksum
from chromadb.config import Settings

class ChromaPersist:
    def __init__(self, path: Path, name: str):
        chroma_client = PersistentClient(path=path.as_posix(), settings=Settings(anonymized_telemetry=False))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2",
            cache_folder="./cache/model/sentence_transformer",
        )
        self.collection = chroma_client.get_or_create_collection(
            name=name,
            embedding_function=ef,  # type: ignore
        )

    def prepare_embeddings(self, texts: list[str]):
        embed_obj = [{"id": chcksum(text), "text": text} for text in list(set(texts))]

        in_DB = self.collection.get(ids=[obj["id"] for obj in embed_obj]).get("ids")
        out_DB = list(set(obj["id"] for obj in embed_obj) - set(in_DB))

        if len(out_DB) > 0:
            self.collection.add(
                ids=out_DB,
                documents=[obj["text"] for obj in embed_obj if obj["id"] in out_DB],
            )

        embeddings = self.collection.get(
            ids=[obj["id"] for obj in embed_obj], include=["embeddings"]
        ).get("embeddings")

        return embeddings
