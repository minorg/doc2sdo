from __future__ import annotations
from abc import ABC, abstractmethod
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from rdflib import Literal, URIRef

from doc2sdo.types.creative_work import CreativeWork


def _hash_uri(source_bytes: bytes) -> URIRef:
    return URIRef("urn:hash::sha256:" + sha256(source_bytes).hexdigest())


class Document(ABC):
    def __init__(self, *, uri: URIRef):
        self.__uri = uri

    @classmethod
    def load(  # noqa: C901, PLR0912
        cls, source: bytes | Path | str | URIRef, *, uri: URIRef | None = None
    ) -> Document:
        from doc2sdo.documents.pdf_document import PdfDocument
        from doc2sdo.documents.text_document import TextDocument

        from pdfminer.pdfdocument import PDFDocument
        from pdfminer.pdfparser import PDFParser, PDFSyntaxError

        if isinstance(source, str):
            if Path(source).is_file():
                source = Path(source)
            else:
                source_parsed_url = urlparse(source)
                if source_parsed_url.scheme and source_parsed_url.netloc:
                    source = URIRef(source)

        if isinstance(source, bytes):
            source_bytes = source
            if uri is None:
                uri = _hash_uri(source_bytes)
        elif isinstance(source, Path):
            with Path.open(source, "rb") as source_file:
                source_bytes = source_file.read()
            if uri is None:
                uri = URIRef(source.as_uri())
        elif isinstance(source, str):
            if uri is None:
                uri = _hash_uri(source.encode("utf-8"))
            return TextDocument(text=source, uri=uri)
        elif isinstance(source, URIRef):
            with urlopen(source) as doc_url:  # noqa: S310
                source_bytes = doc_url.read()
            if uri is None:
                uri = source
        else:
            raise TypeError(type(source))

        try:
            pdf_parser = PDFParser(BytesIO(source_bytes))
            pdfminer_pdf_document = PDFDocument(pdf_parser)
            return PdfDocument(
                pdf_bytes=source_bytes,
                pdfminer_pdf_document=pdfminer_pdf_document,
                uri=uri,
            )
        except PDFSyntaxError:
            return TextDocument(text=source_bytes.decode("utf-8"), uri=uri)

    @property
    @abstractmethod
    def text(self) -> str:
        pass

    def to_creative_work(self) -> CreativeWork.Builder:
        builder = CreativeWork.builder(uri=self.uri)
        builder.set_text(Literal(self.text))
        return builder

    @property
    def uri(self) -> URIRef:
        return self.__uri
