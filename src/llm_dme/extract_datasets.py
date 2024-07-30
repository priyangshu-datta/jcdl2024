import re

import pydash as py_

from .googleLLM import LLM
from .keywords_regexs import (
    inside_bracket_regex,
    intext_citation_regex_1,
    intext_citation_regex_2,
    prompt_LLM,
)
from .retreive_passages import prepare_passages


def extract_datasets(gsc, full_text: str) -> list[str]:
    LLM_TEMPERATURE = 0.06

    if len(full_text) < 1:
        return []

    passages = prepare_passages(full_text)
    if len(passages) < 1:
        return []

    query = prompt_LLM

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

    datasets: set[str] = set()
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

        datasets = datasets.union(
            filter(
                lambda x: len(x.split(" ")) < 10 and "et al." not in x.lower(),
                map(py_.trim, attempted_answer.split(", ")),
            )
        )

    return list(datasets)
