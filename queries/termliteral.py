from indexes.postings import Posting
from .querycomponent import QueryComponent


class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term: str, is_negative):
        super().__init__(is_negative)
        self.term = term
        self.is_negative = is_negative

    def get_postings(self, index, token_processor) -> list[Posting]:
        term = ''.join(token_processor.process_token_without_hyphen(self.term))
        return index.get_postings(term)

    def __str__(self) -> str:
        return self.term

    def __repr__(self):
        return str(self)
