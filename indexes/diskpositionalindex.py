import struct
from typing import Iterable

import pyodbc

from . import Posting, Index


class DiskPositionalIndex:
    """Implements an Inverted Index using a dictionary. Requires knowing the
    vocabulary during the construction."""

    def __init__(self, path):
        """Constructs an empty index using the given vocabulary."""
        self.path = path

    #
    # def add_term(self, term: str, doc_id: int):
    #     """Records that the given term occurred in the given document ID."""
    #     if term in self.document_mapping:
    #         if self.document_mapping[term][-1] != doc_id:
    #             self.document_mapping[term].append(doc_id)
    #     else:
    #         self.document_mapping[term] = [doc_id]

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        position = [[]]
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-0BSMBQL\SQLEXPRESS;'
                                  'Database=search_engine;'
                                  'Trusted_Connection=yes;')
            cursor = conn.cursor()
            try:
                position = cursor.execute('select position from vocabulary where term LIKE ?', term).fetchall()[0]
            except Exception as e:
                print(e)

            # connection is not autocommit by default. So we must commit to save our changes.
            conn.commit()
            conn.close()

        except Exception as e:
            print(e)

        postings = []
        with open(str(self.path), 'rb') as f:
            for pos in position:
                f.seek(pos)
                print(struct.unpack('>i', f.read(4)))

        # if term in self.document_mapping:
        #     for doc in self.document_mapping[term]:
        #         postings.append(Posting(doc))
        return postings
    #
    # def get_vocabulary(self) -> Iterable[str]:
    #     vocabulary = list(sorted(self.document_mapping.keys()))
    #     return vocabulary
