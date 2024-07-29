import re

import pydash as py_

from helper.googleLLM import LLM
from helper.keywords_regexs import (
    inside_bracket_regex,
    intext_citation_regex_1,
    intext_citation_regex_2,
    prompt_LLM,
    reduce_sentence_space_keywords,
)
from helper.retreive_passages import prepare_passages


def extract_datasets(chromaDB, gsc, full_text: str):
    LLM_TEMPERATURE = 0.06

    datasets: set[str] = set()

    if len(full_text) < 1:
        return list(datasets)

    keywords = reduce_sentence_space_keywords
    extra_prompt = ""

    while True:
        passages = prepare_passages(chromaDB, full_text, keywords, regex=len(datasets) < 1)
        if len(passages) < 1:
            return list(datasets)

        query = prompt_LLM + extra_prompt

        llm_answer: list[str] = []
        for _docs in py_.chunk(passages, 10) if len(passages) > 15 else [passages]:
            response = LLM.get_response(
                gsc,
                list(_docs),
                query,
                LLM_TEMPERATURE,
            )
            attempted_answer: str | Exception = py_.attempt(
                lambda _: response.answer.content.parts[0].text, None
            )

            if isinstance(attempted_answer, str):
                llm_answer.append(attempted_answer)
            else:
                return None if len(datasets) < 1 else list(datasets)

        temp_entities: set[str] = set()
        for attempted_answer in llm_answer:
            text_in_brackets: list[str] = re.findall(
                pattern=inside_bracket_regex, string=attempted_answer
            )

            for text in text_in_brackets:
                if not re.search(intext_citation_regex_1, text):
                    continue
                attempted_answer = re.sub(rf"\({text}\)", "", attempted_answer)

            attempted_answer = re.sub(
                intext_citation_regex_2, "", attempted_answer, flags=re.IGNORECASE
            )

            temp_entities = temp_entities.union(
                filter(
                    lambda x: len(x.split(" ")) < 10 and "et al." not in x.lower(),
                    map(py_.trim, attempted_answer.split(", ")),
                )
            )

        temp_entities = datasets.union(temp_entities)

        if temp_entities - datasets == set():
            break

        extra_prompt = (
            f"Example datasets are: {', '.join(datasets)}. Please find more datasets."
        )
        datasets = keywords = temp_entities

        for dataset in datasets:
            if match := re.findall(inside_bracket_regex, dataset):
                match: list[str] = [m.strip() for m in match]
                keywords = keywords.union(match)
                keywords = keywords.union(
                    {re.sub(rf"\({m}\)", "", dataset).strip() for m in match}
                )

    return list(datasets)
