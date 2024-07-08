import re

import numpy as np
import pydash as py_
from helper.sentence_splitter import sentence_splitter
from helper.keywords_regexs import semantic_search_query
from sentence_transformers.util import semantic_search


def reduce_sentence_space(
    sentences: list[str], keywords: set[str], regex: bool = False
):
    if not regex:
        keywords = [re.escape(keyword) for keyword in keywords]

    def isSentenceUseful(sentence: str):
        return any(re.search(keyword, sentence, flags=re.I) for keyword in keywords)

    return list(filter(isSentenceUseful, sentences))


def resolve_hit_documents(sentences: list[str], docs_hits: list) -> list[str]:
    indices = py_.uniq_with(
        sorted(
            py_.chain(docs_hits).flatten().value(),
            key=lambda passage: passage["score"],
            reverse=True,
        ),
        lambda a, b: a["corpus_id"] == b["corpus_id"],
    )

    return list(map(lambda x: sentences[x["corpus_id"]], indices))


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


def prepare_passages(chromaDB, full_text: str, keywords: set[str], regex: bool):
    # sentences = group_sentences(sentence_splitter(full_text), 200, 2)
    sentences = sentence_splitter(full_text)

    reduced_sentence_space = reduce_sentence_space(sentences, keywords, regex)

    if len(reduced_sentence_space) < 1:
        return reduced_sentence_space

    sentence_embeds = np.array(chromaDB.prepare_embeddings(reduced_sentence_space))
    query_embeds = np.array(chromaDB.prepare_embeddings(semantic_search_query))
    doc_hits = semantic_search(query_embeds, sentence_embeds)  # type: ignore
    reduced_relevant_sentences = resolve_hit_documents(reduced_sentence_space, doc_hits)

    # passages = reduced_relevant_sentences

    passages: list[str] = []
    for sentence in reduced_relevant_sentences:
        j = sentences.index(sentence)
        i = 0
        passage = ""
        while len(passage.split(" ")) < 200 and len(passage) < 1200 and i < j:
            passage = " ".join(
                sentences[max(0, j - i) : min(len(sentences), j + i + 1)]
            )
            i += 1

        if len(passage) > 1:
            passages.append(passage)

    return passages
