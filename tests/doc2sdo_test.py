from pathlib import Path
from doc2sdo.doc2sdo import doc2sdo
from doc2sdo.types.creative_work import CreativeWork


def test_doc2sdo(
    pdf_file_paths: tuple[Path, ...], text_file_paths: tuple[Path, ...]
) -> None:
    for file_path in list(pdf_file_paths) + list(text_file_paths):
        things = tuple(doc2sdo(file_path))
        # assert named_entities
        for thing in things:
            assert thing.uri
            if isinstance(thing, CreativeWork):
                continue
            assert thing.name is not None
            assert thing.name.value
