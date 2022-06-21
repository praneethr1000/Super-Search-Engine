from .querycomponent import QueryComponent
from indexes import Index, Posting


class NotQuery(QueryComponent):
    def __init__(self, component, is_negative):
        super().__init__(is_negative)
        self.component = component
        self.is_negative = is_negative

    def get_postings(self, index: Index, token_processor) -> list[Posting]:
        result = self.component.get_postings(index, token_processor)
        return result

    def __str__(self):
        return '"' + str(self.component) + '"'
