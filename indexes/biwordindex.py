from typing import Iterable
from . import Posting, Index


class BiwordIndex(Index):
    """Implements Biword Index using a dictionary. Requires knowing the
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

    def get_postings(self, terms: list[str]) -> list[Posting]:
        """Returns a list of Postings for all documents that contain the given terms."""
        # TODO: implement this method.
        postings = []
        query = ' '.join(terms)
        if query in self.document_mapping:
            for doc in self.document_mapping[query]:
                postings.append(Posting(doc))
        return postings

    def get_vocabulary(self) -> Iterable[str]:
        vocabulary = list(sorted(self.document_mapping.keys()))
        return vocabulary


