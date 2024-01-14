import os

import pytest

from doc2sdo.llm_metadata import LlmMetadata, GPT_3_5
from doc2sdo.named_entity_recognizer import NamedEntityRecognizer


@pytest.mark.parametrize(
    "model",
    [("en_core_web_md",), (GPT_3_5,)],
)
def test_recognizer(model: LlmMetadata | str, pdf_texts: tuple[str, ...]) -> None:
    if isinstance(model, LlmMetadata) and (
        "OPENAI_API_KEY" not in os.environ or "OPENAI_API_ORG" not in os.environ
    ):
        return

    sut = NamedEntityRecognizer(language="english", model=model)
    for pdf_text in pdf_texts:
        named_entities = tuple(sut.recognize(pdf_text))
        # assert named_entities
        for named_entity in named_entities:
            assert named_entity.name.value
            assert named_entity.uri
