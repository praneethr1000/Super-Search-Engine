from indexes.postings import Posting
from .querycomponent import QueryComponent


class NearLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: list[str], is_negative):
        super().__init__(is_negative)
        self.terms = [s for s in terms]
        self.is_negative = is_negative

    def check_k_positions(self, result, k):
        # Check if the terms are k indexes near
        len_components = len(result)
        temp = result[0]
        curr = 1
        while curr < len_components:
            i, j = 0, 0
            first = temp
            second = result[curr]
            temp = []
            while i < len(first[0]) and j < len(second[0]):
                if first[0][i] == second[0][j]:
                    pos1, pos2 = 0, 0
                    while pos1 < len(first[1][i]) and pos2 < len(second[1][j]):
                        if 0 < (second[1][j][pos2] - first[1][i][pos1]) <= k:
                            if temp and temp[0][-1] != first[0][i]:
                                temp[0].append(first[0][i])
                                temp[1].append([second[1][j][pos2]])
                            elif temp and temp[0][-1] == first[0][i]:
                                temp[1][-1].append(second[1][j][pos2])
                            else:
                                temp = [[first[0][i]], [[second[1][j][pos2]]]]
                            pos1 += 1
                            pos2 += 1
                        elif first[1][i][pos1] == second[1][j][pos2]:
                            pos1 += 1
                            pos2 += 1
                        elif first[1][i][pos1] > second[1][j][pos2]:
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
        return temp

    def get_postings(self, index, token_processor) -> list[Posting]:
        result = []
        all_terms = self.terms
        k_index = []
        terms = []
        for i in range(len(all_terms)):
            if 'near' in all_terms[i].lower():
                k = all_terms[i].split("/")[1]
                k_index.append(int(k))
            else:
                terms.append(all_terms[i])
        for term in terms:
            term = ''.join(token_processor.process_token_without_hyphen(term))
            result.append(index.get_termInfo(term))
        documents = [result[0]]
        for i in range(1, len(k_index)+1):
            documents.append(result[i])
            documents = [self.check_k_positions(documents, k_index[i-1])]

        postings = []
        if documents[0]:
            for doc in documents[0][0]:
                postings.append(Posting(doc))
        return postings

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
