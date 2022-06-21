from .querycomponent import QueryComponent
from indexes import Index, Posting


class AndQuery(QueryComponent):
    def __init__(self, components: list[QueryComponent]):
        self.components = components

    def and_not(self, first, second):
        out = []
        i, j = 0, 0
        while i < len(first) and j < len(second):
            if first[i] == second[j]:
                i += 1
                j += 1
            elif first[i] < second[j]:
                out.append(first[i])
                i += 1
            else:
                j += 1
        if i < len(first):
            out.extend(first[i:])
        return out

    def get_postings(self, index: Index, token_processor) -> list[Posting]:
        operation = []
        skip = set()
        for ind, i in enumerate(self.components):
            operation.append(i.is_negative)
            if i.is_negative:
                skip.add(ind+1)
        documents = []
        final_ope = []
        for ind, component in enumerate(self.components):
            if ind in skip:
                continue
            documents.append([])
            final_ope.append(operation[ind])
            s = component.get_postings(index, token_processor)
            for p in s:
                documents[-1].append(p.doc_id)
        curr = 1
        while curr < len(documents):
            first = documents[curr-1]
            second = documents[curr]
            if final_ope[curr-1]:
                documents[curr] = self.and_not(second, first)
            elif operation[curr]:
                documents[curr] = self.and_not(first, second)
            else:
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
