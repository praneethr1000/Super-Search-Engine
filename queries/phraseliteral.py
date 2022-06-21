from indexes.postings import Posting
from .querycomponent import QueryComponent


class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: list[str], is_negative):
        super().__init__(is_negative)
        self.terms = [s for s in terms]

    def positional_merge(self, result):
        # Performs the positional merge
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
                        if first[1][i][pos1] == second[1][j][pos2] - 1:
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
        if len(self.terms) == 2:
            # Returns postings based on biword indexing
            postings = []
            terms = self.terms
            for i in range(len(terms)):
                terms[i] = ''.join(token_processor.process_token_without_hyphen(terms[i]))
            query = ' '.join(terms)
            document_mapping = index.get_biwordTermInfo(query)
            for doc in document_mapping:
                postings.append(Posting(doc))
            return postings
        else:
            # Returns postings based on positional inverted indexing
            processed_terms = []
            for term in self.terms:
                processed_terms.append(''.join(token_processor.process_token_without_hyphen(term)))
            postings_list = index.get_postings_with_positions_list(processed_terms)
            for term in processed_terms:
                result.append(postings_list[term])
            documents = self.positional_merge(result)
            postings = []
            if documents:
                for doc in documents[0]:
                    postings.append(Posting(doc))
            return postings

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
