from dataclasses import dataclass
from typing import Any
from spacy.language import Language
import spacy.cli

import spacy


@dataclass(frozen=True)
class SpacyModel:
    name: str

    def load(self, **_: dict[str, Any]) -> Language:
        try:
            return spacy.load(self.name)
        except OSError:
            spacy.cli.download(self.name)
            return spacy.load(self.name)
