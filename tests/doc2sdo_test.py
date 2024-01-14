from pathlib import Path
from doc2sdo.doc2sdo import doc2sdo


def test_doc2sdo(pdf_file_paths: tuple[Path, ...]) -> None:
    for pdf_file_path in pdf_file_paths:
        things = tuple(doc2sdo(pdf_file_path))
        # assert named_entities
        for thing in things:
            assert thing.name.value
            assert thing.uri
