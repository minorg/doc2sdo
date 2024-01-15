# doc2sdo

Extract entities from text documents and transform them to schema.org resources.

## Installation

    pip install doc2sdo

## Usage

### From the command line

    doc2sdo path/to/your.pdf

### From Python

    from pathlib import Path
    import sys

    from doc2sdo import doc2sdo

    for thing in doc2sdo(Path("/path/to/your.pdf")):
        thing.resource.graph.serialize(sys.stdout.buffer)

## Development

### Prerequisites

* [Python 3.10+](https://www.python.org/)
* [Python Poetry](https://python-poetry.org/)

### Install dependencies

    script/bootstrap

### Run tests

    script/test
