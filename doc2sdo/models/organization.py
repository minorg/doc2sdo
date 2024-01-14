from __future__ import annotations

from rdflib import SDO, URIRef

from doc2sdo.models.thing import Thing


class Organization(Thing):
    class Builder(Thing.Builder):
        def build(self) -> Organization:
            return Organization(self._resource)

    @classmethod
    def rdf_type(cls) -> URIRef:
        return SDO.Organization
