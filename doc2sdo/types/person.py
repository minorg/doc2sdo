from __future__ import annotations

from rdflib import SDO, URIRef

from doc2sdo.types.thing import Thing


class Person(Thing):
    class Builder(Thing.Builder):
        def build(self) -> Person:
            return Person(self._resource)

    @classmethod
    def rdf_type(cls) -> URIRef:
        return SDO.Person
