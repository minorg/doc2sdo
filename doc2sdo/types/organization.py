from __future__ import annotations

from rdflib import SDO, Literal

from doc2sdo.types.thing import Thing


class Organization(Thing):
    class Builder(Thing.Builder):
        def build(self) -> Organization:
            return Organization(self._resource)

    @classmethod
    def builder(cls, *, name: Literal) -> Builder:
        return cls.Builder(rdf_type=SDO.Organization, uri=cls._uri_from_name(name))

    @property
    def name(self) -> Literal:
        name = super().name
        assert name is not None
        return name
