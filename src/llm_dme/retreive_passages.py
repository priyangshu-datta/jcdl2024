from dotenv import load_dotenv
import pydash as py_
from .sentence_splitter import sentence_splitter

load_dotenv()


def group_sentences(sentences: list[str], max_tokens=100, overlap=1):
    chunks = []
    tokens_amount = 0
    chunk = []
    for sentence in sentences:
        if tokens_amount < max_tokens:
            chunk.append(sentence)
            tokens_amount += len(py_.strings.words(sentence))
        else:
            chunks.append(chunk)

            chunk = chunk[len(chunk) - overlap :] + [sentence]
            tokens_amount = py_.reduce_(
                chunk,
                lambda total, sentence: len(py_.strings.words(sentence)) + total,
                0,
            )
    else:
        chunks.append(chunk)

    return py_.chain(chunks).map_(lambda x: " ".join(x)).value()


def prepare_passages(full_text: str):
    passages = group_sentences(sentence_splitter(full_text), 200, 2)

    return passages
