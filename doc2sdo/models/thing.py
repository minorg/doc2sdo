from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from urllib.parse import quote
import stringcase

from rdflib import RDF, SDO, Graph, Literal, URIRef

from doc2sdo.namespaces.doc2sdo import DOC2SDO

if TYPE_CHECKING:
    from rdflib.resource import Resource


class Thing(ABC):
    class Builder:
        def __init__(self, resource: Resource):
            self._resource = resource

        def build(self) -> Thing:
            raise NotImplementedError

    def __init__(self, resource: Resource):
        self.__resource = resource

    @classmethod
    def builder(cls, *, name: Literal) -> Builder:
        uri = DOC2SDO[
            stringcase.spinalcase(cls.__name__) + ":" + quote(name.value.lower())
        ]
        graph = Graph()
        resource = graph.resource(uri)
        resource.add(RDF.type, cls.rdf_type())
        resource.add(SDO.name, name)
        return cls.Builder(resource)

    @classmethod
    @abstractmethod
    def rdf_type(cls) -> URIRef:
        raise NotImplementedError

    @property
    def resource(self) -> Resource:
        return self.__resource

    @property
    def uri(self) -> URIRef:
        return self.resource.identifier
