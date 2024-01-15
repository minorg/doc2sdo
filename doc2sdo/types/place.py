from __future__ import annotations

from rdflib import SDO, Literal

from doc2sdo.types.thing import Thing


class Place(Thing):
    class Builder(Thing.Builder):
        def build(self) -> Place:
            return Place(self._resource)

    @classmethod
    def builder(cls, *, name: Literal) -> Builder:
        builder = cls.Builder(rdf_type=SDO.Place, uri=cls._uri_from_name(name))
        builder.set_name(name)
        return builder

    @property
    def name(self) -> Literal:
        name = super().name
        assert name is not None
        return name
