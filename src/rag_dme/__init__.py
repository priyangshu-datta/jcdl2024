from functools import partial
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


from .extract_datasets import extract_datasets
from .goauth import GenerativeServiceClient
from .vectorDB import ChromaPersist

chromaDB = ChromaPersist(name="embeds", path=Path(".local"))
gsc = GenerativeServiceClient()
extract_datasets = partial(extract_datasets, chromaDB=chromaDB, gsc=gsc)

__all__ = ["extract_datasets", "GenerativeServiceClient", "ChromaPersist"]
