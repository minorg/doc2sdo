import os

import pytest
from doc2sdo import defaults

from doc2sdo.llm_spacy_model import GPT_3_5, LlmSpacyModel
from doc2sdo.named_entity_recognizer import NamedEntityRecognizer
from doc2sdo.spacy_model import SpacyModel


@pytest.mark.parametrize(
    "model",
    [defaults.SPACY_MODEL, GPT_3_5],
)
def test_recognizer(model: SpacyModel, pdf_texts: tuple[str, ...]) -> None:
    if isinstance(model, LlmSpacyModel) and (
        "OPENAI_API_KEY" not in os.environ or "OPENAI_API_ORG" not in os.environ
    ):
        return

    sut = NamedEntityRecognizer(spacy_model=model)
    for pdf_text in pdf_texts:
        named_entities = tuple(sut.recognize(pdf_text))
        # assert named_entities
        for named_entity in named_entities:
            assert named_entity.name.value
            assert named_entity.uri
