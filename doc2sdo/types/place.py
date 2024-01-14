from __future__ import annotations

from rdflib import SDO, URIRef

from doc2sdo.types.thing import Thing


class Place(Thing):
    class Builder(Thing.Builder):
        def build(self) -> Place:
            return Place(self._resource)

    @classmethod
    def rdf_type(cls) -> URIRef:
        return SDO.Place
