__import__("pysqlite3")
import sys

sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

from pathlib import Path
import dotenv
from utils import ChromaPersist, GenerativeServiceClient
from tqdm import tqdm


dotenv.load_dotenv()
tqdm.pandas()

chromaDB = ChromaPersist(name="embeddings", path=Path("./cache/db"))
generative_service_client = GenerativeServiceClient()
