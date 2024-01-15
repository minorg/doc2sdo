import logging
from pathlib import Path
import sys
from typing import Annotated, Optional
from rdflib import Graph, URIRef
import typer

from doc2sdo import defaults
from doc2sdo import llm_spacy_model
from doc2sdo.doc2sdo import doc2sdo
from doc2sdo.llm_spacy_model import LlmSpacyModel
from doc2sdo.spacy_model import SpacyModel


def _main(  # noqa: PLR0913
    *,
    doc: Annotated[
        Optional[str],  # noqa: UP007
        typer.Argument(
            help="path or URL to a PDF or text document; if not specified, read from stdin",
        ),
    ] = None,
    debug: Annotated[bool, typer.Option(help="enable debug logging")] = False,
    doc_uri: Annotated[
        Optional[str], typer.Option(help="override the URI of the doc")  # noqa: UP007
    ] = None,
    nltk_language: Annotated[
        str, typer.Option(help="NLTK language identifier")
    ] = defaults.NLTK_LANGUAGE,
    rdf_format: Annotated[
        str,
        typer.Option(
            help="RDF format to write to stdout, accepts any rdflib format string"
        ),
    ] = "turtle",
    spacy_model: Annotated[
        str, typer.Option(help="name of a spaCy model")
    ] = defaults.SPACY_MODEL.name
) -> None:
    # If debug specified, enable the DEBUG log level
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if spacy_model is not None:
        spacy_model_upper = spacy_model.upper()
        spacy_model_typed = None
        for attr in dir(llm_spacy_model):
            value = getattr(llm_spacy_model, attr)
            if not isinstance(value, LlmSpacyModel):
                continue
            if spacy_model_upper == attr or spacy_model_upper == value.name.upper():
                spacy_model_typed = value
                break
        if spacy_model_typed is None:
            spacy_model_typed = SpacyModel(spacy_model)
    else:
        spacy_model_typed = defaults.SPACY_MODEL

    doc_typed = doc if doc is not None else sys.stdin.buffer.read()

    union_graph = Graph()

    for thing in doc2sdo(
        doc=doc_typed,
        doc_uri=URIRef(doc_uri) if doc_uri is not None else None,
        nltk_language=nltk_language,
        spacy_model=spacy_model_typed,
    ):
        for triple in thing.resource.graph:
            union_graph.add(triple)

    union_graph.serialize(destination=sys.stdout.buffer, format=rdf_format)  # type: ignore  # noqa: PGH003


def main() -> None:
    # The Typer library uses the type annotations on _main to create a command line option parser,
    # parses the command line, does type conversion as necessary, then invokes _main.
    typer.run(_main)


if __name__ == "__main__":
    main()
