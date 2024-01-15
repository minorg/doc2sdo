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
    document = Document.load(doc, uri=doc_uri)

    creative_work_builder = document.to_creative_work()

    for named_entity in NamedEntityRecognizer(
        spacy_model=spacy_model, stopword_language=stopword_language
    ).recognize(document.text):
        creative_work_builder.add_about(named_entity.uri)
        yield named_entity

    yield creative_work_builder.build()
