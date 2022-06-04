from typing import Iterable
from . import Posting, Index


class SoundexIndex(Index):
    """Implements an Sounded Index using a dictionary. Requires knowing the
    vocabulary during the construction."""

    def __init__(self):
        """Constructs an empty index using the given vocabulary."""
        self.document_mapping = {}
        self.code_mapping = {}

    def add_term(self, term: str, doc_id: int):
        """Records that the given term occurred in the given document ID."""
        if term not in self.document_mapping:
            len_term = len(term)
            if len_term == 1:
                return term + '000'
            final_word = term[0]
            word = list(term)[1:]
            for index, letter in enumerate(word):
                if letter in ['a', 'e', 'i', 'o', 'u', 'h', 'w', 'y']:
                    word[index] = '0'
                elif letter in ['b', 'f', 'p', 'v']:
                    word[index] = '1'
                elif letter in ['c', 'g', 'j', 'k', 'q', 's', 'x', 'z']:
                    word[index] = '2'
                elif letter in ['d', 't']:
                    word[index] = '3'
                elif letter == 'l':
                    word[index] = '4'
                elif letter in ['m', 'n']:
                    word[index] = '5'
                elif letter == 'r':
                    word[index] = '6'
                else:
                    word[index] = ''
            index = 0
            while index < (len_term - 2):
                if word[index] == word[index + 1] and word[index] != '0':
                    final_word += word[index]
                    index += 1
                elif word[index] == word[index + 1]:
                    final_word += word[index]
                    index += 2
                else:
                    final_word += word[index]
                    index += 1
            if len(final_word) >= 4:
                final_word = final_word[:4]
            else:
                final_word = final_word + '0' * (4 - len(final_word))
            self.document_mapping[term] = final_word
            if final_word not in self.code_mapping:
                self.code_mapping[final_word] = [doc_id]
            else:
                if self.code_mapping[final_word][-1] != doc_id:
                    self.code_mapping[final_word].append(doc_id)
        else:
            if self.code_mapping[self.document_mapping[term]][-1] != doc_id:
                self.code_mapping[self.document_mapping[term]].append(doc_id)

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        # TODO: implement this method.
        postings = []
        if term in self.document_mapping:
            for doc in self.code_mapping[self.document_mapping[term]]:
                postings.append(Posting(doc))
        return postings

    def get_vocabulary(self) -> list[str]:
        vocabulary = list(sorted(self.document_mapping.keys()))
        return vocabulary
