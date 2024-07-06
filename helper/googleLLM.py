from time import sleep, time

import google.ai.generativelanguage as glm

from init import generative_service_client


def prepare_grounding_passages(docs: list[str]):
    contents = [glm.Content(parts=[glm.Part(text=doc)]) for doc in docs]
    passages = [
        glm.GroundingPassage(content=content, id=str(index))
        for index, content in enumerate(contents)
    ]
    return glm.GroundingPassages(passages=passages)


def prepare_query_content(user_query: str):
    part = glm.Part(text=user_query)
    return glm.Content(parts=[part])


def generate_answer(
    grounding_passages: glm.GroundingPassages,
    query_content: glm.Content,
    temperature: float | None,
):
    answer_request = glm.GenerateAnswerRequest(
        model="models/aqa",
        contents=[query_content],
        inline_passages=grounding_passages,
        temperature=temperature,
        answer_style="EXTRACTIVE",  # or ABSTRACTIVE, EXTRACTIVE, VERBOSE
    )

    return generative_service_client.get().generate_answer(answer_request)


class LLM:
    last_accessed = 0

    @staticmethod
    def get_response(
        docs: list[str],
        query: str,
        temperature: None | float,
    ):
        grounding_passages = prepare_grounding_passages(docs)
        query_content = prepare_query_content(query)

        while time() - LLM.last_accessed < 1:
            sleep(0.5)
            continue

        LLM.last_accessed = time()
        response = generate_answer(grounding_passages, query_content, temperature)

        return response
