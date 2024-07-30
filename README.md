# This is the LLM-DME method branch.

1. Clone the repo.
2. Use the `extract_datasets` function.

```py
from src.llm_dme import extract_datasets, GenerativeServiceClient
from dotenv import load_dotenv


load_dotenv()
gsc = GenerativeServiceClient()

print(extract_datasets(gsc=gsc, full_text=""))
```

## Dependencies
All the mentioned dependencies are mentioned in ``requirements.txt`` file, and is installed during setup.
1. Google's Generative Language API - the API for Google's AI models.
