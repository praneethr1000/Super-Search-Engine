from . import Index


class PositionalInvertedIndex(Index):
    """Implements an Inverted Index using a dictionary. Requires knowing the
    vocabulary during the construction."""

    def __init__(self):
        """Constructs an empty index using the given vocabulary."""
        self.document_mapping = {}
        self.document_mapping_biword = {}

    def add_term(self, term: str, doc_id: int, position: int):
        """Records that the given term occurred in the given document ID."""
        if term in self.document_mapping:
            if doc_id in self.document_mapping[term][0]:
                doc_index = self.document_mapping[term][0].index(doc_id)
                self.document_mapping[term][1][doc_index].append(position)
            else:
                self.document_mapping[term][0].append(doc_id)
                self.document_mapping[term][1].append([position])
        else:
            self.document_mapping[term] = [[doc_id], [[position]]]

    def add_term_biword(self, term: str, doc_id: int):
        """Records that the given term occurred in the given document ID."""
        if term in self.document_mapping_biword:
            if self.document_mapping_biword[term][-1] != doc_id:
                self.document_mapping_biword[term].append(doc_id)
        else:
            self.document_mapping_biword[term] = [doc_id]

    def get_termInfo(self, term):
        if term in self.document_mapping:
            return self.document_mapping[term]
        else:
            return [[], [[]]]

    def get_vocabulary(self) -> list[str]:
        vocabulary = list(sorted(self.document_mapping.keys()))
        return vocabulary

    def get_biword_vocabulary(self):
        biword_vocabulary = dict(sorted(self.document_mapping_biword.items()))
        return biword_vocabulary
