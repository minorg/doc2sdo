from pathlib import Path
from collections.abc import Iterable

from rdflib import URIRef
from doc2sdo import defaults
from doc2sdo.documents.document import Document
from doc2sdo.named_entity_recognizer import NamedEntityRecognizer
from doc2sdo.spacy_model import SpacyModel

from doc2sdo.types.thing import Thing


def doc2sdo(
    doc: bytes | Path | str | URIRef,
    *,
    doc_uri: URIRef | None = None,
    spacy_model: SpacyModel = defaults.SPACY_MODEL,
    stopword_language: str = defaults.STOPWORD_LANGUAGE,
) -> Iterable[Thing]:
    # Convert doc to a string as needed and infer doc's URI as needed

    document = Document.load(doc, uri=doc_uri)

    yield from NamedEntityRecognizer(
        spacy_model=spacy_model, stopword_language=stopword_language
    ).recognize(document.text)
