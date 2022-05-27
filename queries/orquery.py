from .querycomponent import QueryComponent
from indexes import Index, Posting

from queries import querycomponent 

class OrQuery(QueryComponent):
    def __init__(self, components : list[QueryComponent]):
        self.components = components

    def get_postings(self, index : Index) -> list[Posting]:
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
        documents = []
        for term in self.components:
            documents.append([])
            for p in index.get_postings(str(term)):
                documents[-1].append(p.doc_id)
        curr = 1
        while curr < len(documents):
            first = documents[curr - 1]
            second = documents[curr]
            i, j = 0, 0
            out = []
            while i < len(first) and j < len(second):
                if first[i] == second[j]:
                    out.append(first[i])
                    i += 1
                    j += 1
                elif first[i] < second[j]:
                    out.append(first[i])
                    i += 1
                else:
                    out.append(first[j])
                    j += 1
            documents[curr] = out
            curr += 1
        return documents[-1]

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"