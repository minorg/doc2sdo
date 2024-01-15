from __future__ import annotations

from rdflib import SDO, Literal, URIRef

from doc2sdo.types.thing import Thing


class CreativeWork(Thing):
    class Builder(Thing.Builder):
        def add_about(self, about: URIRef) -> CreativeWork.Builder:
            self._resource.add(SDO.about, about)
            return self

        def add_alternate_name(self, alternate_name: Literal) -> CreativeWork.Builder:
            self._resource.add(SDO.alternateName, alternate_name)
            return self

        def add_creator(self, creator: Literal) -> CreativeWork.Builder:
            self._resource.add(SDO.creator, creator)
            return self

        def build(self) -> CreativeWork:
            return CreativeWork(self._resource)

        def set_date_created(self, date_created: Literal) -> CreativeWork.Builder:
            self._resource.set(SDO.dateCreated, date_created)
            return self

        def set_date_modified(self, date_modified: Literal) -> CreativeWork.Builder:
            self._resource.set(SDO.dateModified, date_modified)
            return self

        def set_text(self, text: Literal) -> CreativeWork.Builder:
            self._resource.set(SDO.text, text)
            return self

    @classmethod
    def builder(cls, *, uri: URIRef) -> Builder:
        return cls.Builder(rdf_type=SDO.CreativeWork, uri=uri)
