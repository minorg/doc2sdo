import logging
import re
import unicodedata
from copy import copy
from collections.abc import Iterable, Sequence
from rdflib import Literal

import tiktoken
from doc2sdo import defaults
from doc2sdo.llm_spacy_model import LlmSpacyModel
from doc2sdo.spacy_model import SpacyModel
from doc2sdo.types.organization import Organization
from doc2sdo.types.person import Person
from doc2sdo.types.place import Place
from doc2sdo.types.thing import Thing
from nltk import word_tokenize  # type: ignore  # noqa: PGH003
from nltk.corpus import stopwords  # type: ignore  # noqa: PGH003
from nltk.tokenize.treebank import TreebankWordDetokenizer  # type: ignore  # noqa: PGH003


class NamedEntityRecognizer:
    __WHITESPACE_RE = re.compile(r"\s+")

    def __init__(
        self,
        *,
        spacy_model: SpacyModel = defaults.SPACY_MODEL,
        stopword_language: str = defaults.STOPWORD_LANGUAGE,
    ):
        self.__detokenizer = TreebankWordDetokenizer()
        self.__logger = logging.getLogger(__name__)
        self.__model = spacy_model
        self.__stopwords = set(stopwords.words(stopword_language))
        if isinstance(spacy_model, LlmSpacyModel):
            self.__ent_labels_to_types = {
                ent_class.__name__.upper(): ent_class
                for ent_class in (Organization, Person, Place)
            }
            self.__ignore_ent_labels: frozenset[str] = frozenset()
            self.__nlp = spacy_model.load(
                task={
                    "@llm_tasks": "spacy.NER.v2",
                    "labels": list(self.__ent_labels_to_types),
                    "single_match": True,
                }
            )
            self.__tiktoken_encoding: tiktoken.Encoding | None = (
                tiktoken.encoding_for_model(spacy_model.tiktoken_name)
            )
        else:
            self.__ent_labels_to_types = {
                "FAC": Place,
                "GPE": Place,
                "LOC": Place,
                "ORG": Organization,
                "PERSON": Person,
            }
            self.__ignore_ent_labels = frozenset(
                (
                    "CARDINAL",
                    "DATE",
                    "LAW",
                    "MONEY",
                    "ORDINAL",
                    "PERCENT",
                    "QUANTITY",
                    "TIME",
                )
            )
            self.__nlp = spacy_model.load()
            self.__tiktoken_encoding = None
        self.__unrecognized_ent_labels: set[str] = set()

    def __chunk_text(self, text: str) -> Iterable[str]:
        if not isinstance(self.__model, LlmSpacyModel):
            yield text
            return

        text_split = text.split("\n")
        text_split.reverse()

        def join_text_chunks(text_chunks_seq: Sequence[str]) -> str:
            return "\n".join(text_chunks_seq)

        assert self.__tiktoken_encoding is not None
        text_chunks: list[str] = []
        yielded_text_len_sum = 0
        while text_split:
            text_chunk = text_split.pop()
            text_chunks.append(text_chunk)
            text_chunks_joined = join_text_chunks(text_chunks)
            text_chunks_token_count = len(
                self.__tiktoken_encoding.encode(text_chunks_joined)
            )

            if text_chunks_token_count > self.__model.token_limit:
                text_chunks.pop()
                assert text_chunks, "single text chunk is larger than the token limit"

                text_chunks_joined = join_text_chunks(text_chunks)
                self.__logger.info(
                    "text chunk len=%d tokens=%d",
                    len(text_chunks_joined),
                    len(self.__tiktoken_encoding.encode(text_chunks_joined)),
                )
                yield text_chunks_joined
                yielded_text_len_sum += len(text_chunks_joined)

                text_chunks = [text_chunk]

        if text_chunks:
            text_chunks_joined = join_text_chunks(text_chunks)
            text_chunks_token_count = len(
                self.__tiktoken_encoding.encode(text_chunks_joined)
            )
            assert text_chunks_token_count <= self.__model.token_limit
            self.__logger.info(
                "text chunk len=%d tokens=%d",
                len(text_chunks_joined),
                text_chunks_token_count,
            )
            yield text_chunks_joined
            yielded_text_len_sum += len(text_chunks_joined)

        # assert yielded_text_len_sum == len(
        #     text
        # ), f"{yielded_text_len_sum} vs. {len(text)}"

    def recognize(self, text: str) -> Iterable[Thing]:
        named_entities_dict: dict[type[Thing], dict[str, Thing]] = {}

        for text_chunk in self.__chunk_text(text):
            doc = self.__nlp(text_chunk)

            for ent in doc.ents:
                clean_ent_text = self.__WHITESPACE_RE.sub(" ", ent.text).strip()
                clean_ent_text = unicodedata.normalize("NFC", clean_ent_text)
                clean_ent_text = clean_ent_text.replace("\u2010", "-")
                clean_ent_text_tokens: list[str] = word_tokenize(clean_ent_text)
                clean_ent_text_tokens_without_stopwords: list[str] = copy(
                    clean_ent_text_tokens
                )
                while (
                    clean_ent_text_tokens_without_stopwords
                    and clean_ent_text_tokens_without_stopwords[0].lower()
                    in self.__stopwords
                ):
                    clean_ent_text_tokens_without_stopwords.pop(0)
                if clean_ent_text_tokens_without_stopwords and len(
                    clean_ent_text_tokens_without_stopwords
                ) < len(clean_ent_text_tokens):
                    clean_ent_text = self.__detokenizer.detokenize(  # type: ignore  # noqa: PGH003
                        clean_ent_text_tokens_without_stopwords
                    )

                named_entity_type = self.__ent_labels_to_types.get(ent.label_)
                if named_entity_type is None:
                    if (
                        ent.label_ not in self.__ignore_ent_labels
                        and ent.label_ not in self.__unrecognized_ent_labels
                    ):
                        self.__logger.info(
                            "unrecognized named entity label %s: %s",
                            ent.label_,
                            clean_ent_text,
                        )
                        self.__unrecognized_ent_labels.add(ent.label_.lower())
                    continue

                existing_named_entity = named_entities_dict.get(
                    named_entity_type, {}  # type: ignore  # noqa: PGH003
                ).get(clean_ent_text.lower())
                if existing_named_entity is not None:
                    existing_named_entity_text = existing_named_entity.name.value
                    if (
                        not existing_named_entity_text.islower()
                        and not existing_named_entity_text.isupper()
                    ):
                        # The existing named entity is mixed-case
                        self.__logger.debug(
                            "ignoring duplicate named entity %s: %s",
                            named_entity_type,
                            clean_ent_text,
                        )
                        continue
                    # else drop down to replace it with a mixed-case one

                named_entities_dict.setdefault(named_entity_type, {})[  # type: ignore  # noqa: PGH003
                    clean_ent_text.lower()
                ] = named_entity_type.builder(
                    name=Literal(clean_ent_text)
                ).build()

        return tuple(
            named_entity
            for named_entities_by_text in named_entities_dict.values()
            for named_entity in named_entities_by_text.values()
        )
