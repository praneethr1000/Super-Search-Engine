from indexes.postings import Posting
from .querycomponent import QueryComponent


class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: list[str]):
        self.terms = [s for s in terms]

    def get_postings(self, index) -> list[Posting]:
        result = []
        for term in self.terms:
            result.append(index.get_postings(str(term)))
        len_components = len(self.terms)
        first, second = result[0], result[1]
        curr = 1
        temp = []
        while curr < len_components:
            i, j = 0, 0
            while i < len(first[0]) and j < len(second[0]):
                if first[0][i] == second[0][j]:
                    pos1, pos2 = 0, 0
                    while pos1 < len(first[1]) and pos2 < len(first[1]):
                        if first[1][i][pos1] == first[1][j][pos2] + 1:
                            if temp:
                                temp[-1][1].append(pos2)
                            else:
                                temp.append([[first[0][i]], [pos2]])
                            pos1 += 1
                            pos2 += 1
                        elif first[1][i][pos1] == first[1][j][pos2]:
                            pos1 += 1
                            pos2 += 1
                        elif first[1][i][pos1] > first[1][j][pos2]:
                            pos2 += 1
                        else:
                            pos1 += 1
                    i += 1
                    j += 1
                elif first[0][i] < second[0][j]:
                    i += 1
                else:
                    j += 1
            curr += 1
            first = temp
            second = result[curr]

        postings = []
        for doc in temp[0]:
            postings.append(Posting(doc))
        return postings

        # TODO: program this method. Retrieve the postings for the individual terms in the phrase,

    # and positional merge them together.

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
