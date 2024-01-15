from __future__ import annotations

from rdflib import SDO, URIRef

from doc2sdo.types.thing import Thing


class CreativeWork(Thing):
    class Builder(Thing.Builder):
        def build(self) -> CreativeWork:
            return CreativeWork(self._resource)

    @classmethod
    def builder(cls, *, uri: URIRef) -> Builder:
        return cls.Builder(rdf_type=SDO.CreativeWork, uri=uri)
