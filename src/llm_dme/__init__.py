from functools import partial
from dotenv import load_dotenv


load_dotenv()

from .extract_datasets import extract_datasets
from .goauth import GenerativeServiceClient

extract_datasets = partial(extract_datasets, gsc=GenerativeServiceClient())

__all__ = [
    "extract_datasets",
    "GenerativeServiceClient"
]