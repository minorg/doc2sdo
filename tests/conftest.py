import os
from pathlib import Path
import pdftotext
import pytest


@pytest.fixture(scope="session")
def data_dir_path() -> Path:
    path_ = Path(__file__).parent.absolute() / "data"
    assert path_.is_dir()
    return path_


@pytest.fixture(scope="session")
def pdf_file_paths(data_dir_path: Path) -> tuple[Path, ...]:
    pdf_test_data_dir_path = data_dir_path / "pdf"
    return tuple(
        sorted(
            pdf_test_data_dir_path / file_name
            for file_name in os.listdir(pdf_test_data_dir_path)
            if file_name.startswith("test-document-") and file_name.endswith(".pdf")
        )
    )


@pytest.fixture(scope="session")
def pdf_texts(pdf_file_paths: tuple[Path, ...]) -> tuple[str, ...]:
    result: list[str] = []
    for pdf_file_path in pdf_file_paths:
        with Path.open(pdf_file_path, "rb") as pdf_file:
            pdf = pdftotext.PDF(pdf_file)  # type: ignore  # noqa: PGH003
            text: str = "\n\n".join(pdf)  # type: ignore  # noqa: PGH003
            result.append(text)
    return tuple(result)


@pytest.fixture(scope="session")
def text_file_paths(data_dir_path: Path) -> tuple[Path, ...]:
    pdf_test_data_dir_path = data_dir_path / "text"
    return tuple(
        sorted(
            pdf_test_data_dir_path / file_name
            for file_name in os.listdir(pdf_test_data_dir_path)
            if file_name.startswith("test-document-") and file_name.endswith(".txt")
        )
    )
