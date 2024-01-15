from io import BytesIO
from rdflib import URIRef
from doc2sdo.documents.document import Document
from pdfminer.pdfdocument import PDFDocument
import pdftotext


class PdfDocument(Document):
    def __init__(
        self, *, pdf_bytes: bytes, pdfminer_pdf_document: PDFDocument, uri: URIRef
    ):
        Document.__init__(self, uri=uri)
        self.__pdf_bytes = pdf_bytes
        self.__pdfminer_pdf_document = pdfminer_pdf_document

    @property
    def text(self) -> str:
        pdf = pdftotext.PDF(BytesIO(self.__pdf_bytes))
        text: str = "\n\n".join(pdf)
        return text
