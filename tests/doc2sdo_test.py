from pathlib import Path
from doc2sdo.doc2sdo import doc2sdo


def test_doc2sdo(
    pdf_file_paths: tuple[Path, ...], text_file_paths: tuple[Path, ...]
) -> None:
    for file_path in list(pdf_file_paths) + list(text_file_paths):
        things = tuple(doc2sdo(file_path))
        # assert named_entities
        for thing in things:
            assert thing.name.value
            assert thing.uri
