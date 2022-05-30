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

    def get_postings(self, terms: list[str]) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given terms."""
        # TODO: implement this method.
        postings = []
        term1, term2 = terms[0], terms[1]
        if term1 not in self.document_mapping or term2 not in self.document_mapping:
            return postings
        term1_docs = self.document_mapping[term1]
        term2_docs = self.document_mapping[term2]
        i, j = 0, 0
        while i < len(term1_docs) and j < len(term2_docs):
            if term1_docs[i] == term2_docs[j]:
                postings.append(Posting(term1_docs[i]))
                i += 1
                j += 1
            elif term1_docs[i] < term2_docs[j]:
                i += 1
            else:
                j += 1
        return postings

    def get_vocabulary(self) -> Iterable[str]:
        vocabulary = list(sorted(self.document_mapping.keys()))
        return vocabulary


