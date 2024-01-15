from io import BytesIO
import logging
import re
from typing import ClassVar
from rdflib import Literal, URIRef
from datetime import datetime
from doc2sdo.documents.document import Document
from pdfminer.pdfdocument import PDFDocument
import pdftotext
from dateutil.tz import tzoffset, tzutc

from doc2sdo.types.creative_work import CreativeWork


logger = logging.getLogger(__name__)


class PdfDocument(Document):
    __DATE_STRING_PATTERN = re.compile(
        "".join(  # noqa: FLY002
            [
                r"(D:)?",
                r"(?P<year>\d\d\d\d)",
                r"(?P<month>\d\d)",
                r"(?P<day>\d\d)",
                r"(?P<hour>\d\d)",
                r"(?P<minute>\d\d)",
                r"(?P<second>\d\d)",
                r"(?P<tz_offset>[+-zZ])?",
                r"(?P<tz_hour>\d\d)?",
                r"'?(?P<tz_minute>\d\d)?'?",
            ]
        )
    )

    __IGNORE_INFO_KEYS: ClassVar[set[str]] = {"Creator", "Producer"}

    def __init__(
        self, *, pdf_bytes: bytes, pdfminer_pdf_document: PDFDocument, uri: URIRef
    ):
        Document.__init__(self, uri=uri)
        self.__pdf_bytes = pdf_bytes
        self.__pdfminer_pdf_document = pdfminer_pdf_document

    def __parse_date_string(self, date_string: str) -> datetime | None:
        # https://stackoverflow.com/questions/16503075/convert-creationtime-of-pdf-to-a-readable-format-in-python

        match = self.__DATE_STRING_PATTERN.match(date_string)
        if not match:
            return None
        date_info = match.groupdict()

        for k, v in date_info.items():  # transform values
            if v is None:
                pass
            elif k == "tz_offset":
                date_info[k] = v.lower()  # so we can treat Z as z
            else:
                date_info[k] = int(v)

        if date_info["tz_offset"] in ("z", None):  # UTC
            date_info["tzinfo"] = tzutc()
        else:
            multiplier = 1 if date_info["tz_offset"] == "+" else -1
            date_info["tzinfo"] = tzoffset(
                None,
                multiplier
                * (3600 * date_info["tz_hour"] + 60 * date_info["tz_minute"]),
            )

        for k in ("tz_offset", "tz_hour", "tz_minute"):  # no longer needed
            del date_info[k]

        return datetime(**date_info)  # type: ignore  # noqa: DTZ001, PGH003

    @property
    def text(self) -> str:
        pdf = pdftotext.PDF(BytesIO(self.__pdf_bytes))
        text: str = "\n\n".join(pdf)
        normalized_text = text.replace("\u000A0", " ").replace("\u000C", "\n")
        return normalized_text  # noqa: RET504

    def to_creative_work(self) -> CreativeWork.Builder:
        builder = super().to_creative_work()

        for info in self.__pdfminer_pdf_document.info:  # type: ignore
            # https://www.oreilly.com/library/view/pdf-explained/9781449321581/ch04.html
            for key, value in info.items():  # type: ignore
                assert isinstance(key, str)
                assert isinstance(value, bytes)
                if key == "Author":
                    builder.add_creator(Literal(value.decode("utf-8")))
                elif key == "CreationDate":
                    creation_date = self.__parse_date_string(value.decode("ascii"))
                    if creation_date is not None:
                        builder.set_date_created(Literal(creation_date))
                elif key == "ModDate":
                    modification_date = self.__parse_date_string(value.decode("ascii"))
                    if modification_date is not None:
                        builder.set_date_modified(Literal(modification_date))
                elif key == "Title":
                    builder.add_alternate_name(Literal(value.decode("utf-8")))
                elif key in self.__IGNORE_INFO_KEYS:
                    logger.debug(
                        "ignoring PDF document info field %s",
                        key,
                    )
                else:
                    logger.warning(
                        "nknown PDF document info field %s: %s",
                        key,
                        value,
                    )

        return builder
