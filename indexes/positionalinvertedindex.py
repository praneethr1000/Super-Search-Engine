from typing import Iterable
from . import Posting, Index
from bisect import bisect_left


class PositionalInvertedIndex(Index):
    """Implements an Inverted Index using a dictionary. Requires knowing the
    vocabulary during the construction."""

    def __init__(self):
        """Constructs an empty index using the given vocabulary."""
        self.document_mapping = {}

    def add_term(self, term: str, doc_id: int, position: int):
        """Records that the given term occurred in the given document ID."""
        if term in self.document_mapping:
            doc_index = bisect_left(self.document_mapping[term][0], doc_id)
            # Check to make sure the doc_id is actually in the list.
            if doc_index != len(self.document_mapping[term][0]) and self.document_mapping[term][0][doc_index] == doc_id:
                self.document_mapping[term][1][doc_index].append(position)
            else:
                self.document_mapping[term][0].append(doc_id)
                self.document_mapping[term][1].append([position])
        else:
            self.document_mapping[term] = [[doc_id], [[position]]]

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        # TODO: implement this method.
        postings = []
        if term in self.document_mapping:
            for doc in self.document_mapping[term][0]:
                postings.append(Posting(doc))
        return postings

    def get_vocabulary(self) -> Iterable[str]:
        # vocabulary = list(sorted(self.document_mapping.keys()))
        # return vocabulary
        return self.document_mapping
