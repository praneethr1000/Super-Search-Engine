from .querycomponent import QueryComponent
from indexes import Index, Posting


class AndQuery(QueryComponent):
    def __init__(self, components: list[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index, token_processor) -> list[Posting]:
        documents = []
        for component in self.components:
            documents.append([])
            s = component.get_postings(index, token_processor)
            for p in s:
                documents[-1].append(p.doc_id)

        curr = 1
        while curr < len(documents):
            first = documents[curr-1]
            second = documents[curr]
            i, j = 0, 0
            out = []
            while i < len(first) and j < len(second):
                if first[i] == second[j]:
                    out.append(first[i])
                    i += 1
                    j += 1
                elif first[i] < second[j]:
                    i += 1
                else:
                    j += 1
            documents[curr] = out
            curr += 1
        postings = []
        for doc in documents[-1]:
            postings.append(Posting(doc))
        return postings

    def __str__(self):
        return " AND ".join(map(str, self.components))
