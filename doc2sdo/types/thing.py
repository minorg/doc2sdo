from __future__ import annotations
from typing import TYPE_CHECKING
from urllib.parse import quote
import stringcase

from rdflib import RDF, SDO, Graph, Literal, URIRef

from doc2sdo.namespaces.doc2sdo import DOC2SDO

if TYPE_CHECKING:
    from rdflib.resource import Resource


class Thing:
    class Builder:
        def __init__(self, *, rdf_type: URIRef, uri: URIRef):
            graph = Graph()
            self._resource = graph.resource(uri)
            self._resource.add(RDF.type, rdf_type)

        def build(self) -> Thing:
            raise NotImplementedError

        def set_name(self, name: Literal) -> Thing.Builder:
            self._resource.add(SDO.name, name)
            return self

    def __init__(self, resource: Resource):
        self.__resource = resource

    @property
    def name(self) -> Literal | None:
        name = self.resource.value(SDO.name)
        if name is None:
            return None
        assert isinstance(name, Literal)
        return name

    @property
    def resource(self) -> Resource:
        return self.__resource

    @property
    def uri(self) -> URIRef:
        return self.resource.identifier

    @classmethod
    def _uri_from_name(cls, name: Literal) -> URIRef:
        return DOC2SDO[
            stringcase.spinalcase(cls.__name__) + ":" + quote(name.value.lower())
        ]
