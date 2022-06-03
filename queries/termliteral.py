from indexes.postings import Posting
from .querycomponent import QueryComponent


class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term: str):
        self.term = term

    def get_postings(self, index, token_processor) -> list[Posting]:
        term = ''.join(token_processor.process_token(self.term))
        return index.get_postings(term)

    def __str__(self) -> str:
        return self.term

    def __repr__(self):
        return str(self)
