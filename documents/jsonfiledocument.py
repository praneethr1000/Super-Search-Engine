from io import TextIOWrapper
from pathlib import Path
from typing import Iterable
from .document import Document
import json


class JsonFileDocument(Document):
    """
    Represents a document that is saved as a json file in the local file system.
    """

    def __init__(self, id: int, path: Path):
        super().__init__(id)
        self.path = path

    @property
    def title(self) -> str:
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        return data['title']

    @property
    def fileName(self) -> str:
        return self.path.stem

    @property
    def author(self) -> str:
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        return data['author'] if 'author' in data else 'No info about author'

    # returnsJsonIOWrapper
    def get_content(self) -> Iterable[str]:
        with open(self.path, encoding='utf-8') as f:
            data = json.load(f)
        return data['body']

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> 'JsonFileDocument':
        """A factory method to create a JsonFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)
