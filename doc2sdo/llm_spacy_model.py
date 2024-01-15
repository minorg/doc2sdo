from dataclasses import dataclass
from typing import Any

from doc2sdo.spacy_model import SpacyModel
from spacy.language import Language
import spacy


@dataclass(frozen=True)
class LlmSpacyModel(SpacyModel):
    tiktoken_name: str
    token_limit: int

    def load(self, *, task: Any) -> Language:  # type: ignore  # noqa: PGH003, ANN401
        result = spacy.blank("en")
        result.add_pipe(
            "llm",
            config={
                "task": task,
                "model": {
                    "@llm_models": self.name,
                },
            },
        )
        return result


GPT_3_5 = LlmSpacyModel(
    name="spacy.GPT-3-5.v1",
    tiktoken_name="gpt-3.5-turbo",
    token_limit=3500,  # Actually 4097, leave room for the prompt
)
