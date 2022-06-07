from typing import Iterable
from . import Posting, Index


class InvertedIndex(Index):
    """Implements an Inverted Index using a dictionary. Requires knowing the
    vocabulary during the construction."""

    def __init__(self):
        """Constructs an empty index using the given vocabulary."""
        self.document_mapping = {}

    def add_term(self, term: str, doc_id: int):
        """Records that the given term occurred in the given document ID."""
        if term in self.document_mapping:
            if self.document_mapping[term][-1] != doc_id:
                self.document_mapping[term].append(doc_id)
        else:
            self.document_mapping[term] = [doc_id]

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        # TODO: implement this method.
        postings = []
        if term in self.document_mapping:
            for doc in self.document_mapping[term]:
                postings.append(Posting(doc))
        return postings

    def get_vocabulary(self) -> Iterable[str]:
        vocabulary = list(sorted(self.document_mapping.keys()))
        return vocabulary


