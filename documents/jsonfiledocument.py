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
        return self.path.stem

    # returns TextIOWrapper
    def get_content(self) -> Iterable[str]:
        dict_value = self.path.json()
        res = json.dumps(dict_value)
        d2 = json.loads(res)
        print(d2)
        return d2

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> 'JsonFileDocument':
        """A factory method to create a TextFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)
