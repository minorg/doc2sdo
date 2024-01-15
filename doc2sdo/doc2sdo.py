from hashlib import sha256
from pathlib import Path
from collections.abc import Iterable
from urllib.parse import urlparse
from urllib.request import urlopen

from rdflib import URIRef
from doc2sdo import defaults
from doc2sdo.named_entity_recognizer import NamedEntityRecognizer
from doc2sdo.spacy_model import SpacyModel

from doc2sdo.types.thing import Thing


def doc2sdo(
    doc: Path | str | URIRef,
    *,
    doc_uri: URIRef | None = None,
    spacy_model: SpacyModel = defaults.SPACY_MODEL,
    stopword_language: str = defaults.STOPWORD_LANGUAGE,
) -> Iterable[Thing]:
    # Convert doc to a string as needed and infer doc's URI as needed

    if isinstance(doc, Path):
        with Path.open(doc) as doc_file:
            doc_str = doc_file.read()
        if doc_uri is None:
            doc_uri = URIRef(doc.as_uri())
    elif isinstance(doc, URIRef):
        with urlopen(doc) as doc_url:  # noqa: S310
            doc_str = doc_url.read()
        if doc_uri is None:
            doc_uri = doc
    else:
        doc_parsed_url = urlparse(doc)
        if doc_parsed_url.scheme and doc_parsed_url.netloc:
            with urlopen(doc) as doc_url:  # noqa: S310
                doc_str = doc_url.read()
            if doc_uri is None:
                doc_uri = URIRef(doc)
        else:
            doc_str = doc
            if doc_uri is None:
                doc_uri = URIRef(
                    "urn:hash::sha25:" + sha256(doc_str.encode("utf-8")).hexdigest()
                )

    yield from NamedEntityRecognizer(
        spacy_model=spacy_model, stopword_language=stopword_language
    ).recognize(doc_str)
