from rdflib import Literal, URIRef
from doc2sdo.documents.document import Document
from doc2sdo.types.creative_work import CreativeWork


class TextDocument(Document):
    def __init__(self, *, text: str, uri: URIRef):
        Document.__init__(self, uri=uri)
        self.__text = text

    @property
    def text(self) -> str:
        return self.__text
