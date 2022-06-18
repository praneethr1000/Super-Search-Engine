import struct
from typing import Iterable
import pyodbc
from . import Posting


class DiskPositionalIndex:
    """Implements a Disk Positional Index."""

    def __init__(self, vocab_path, ld_path, biword_vocab_path):
        """Constructs an empty index using the given vocabulary."""
        self.vocab_path = vocab_path
        self.ld_path = ld_path
        self.biword_vocab_path = biword_vocab_path

    def create_db_connection(self):
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-0BSMBQL\SQLEXPRESS;'
                                  'Database=search_engine;'
                                  'Trusted_Connection=yes;')
            cursor = conn.cursor()
            return conn, cursor
        except Exception as e:
            print(e)

    def get_position_from_db(self, term, table):
        position = [[]]
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-0BSMBQL\SQLEXPRESS;'
                                  'Database=search_engine;'
                                  'Trusted_Connection=yes;')
            cursor = conn.cursor()
            try:
                if table == "vocab":
                    position = cursor.execute('select position from vocabulary where term LIKE ?', term).fetchall()[0]
                elif table == "biword_vocab":
                    position = \
                        cursor.execute('select position from biword_vocabulary where term LIKE ?', term).fetchall()[0]
                else:
                    position = cursor.execute('select position from documentWeight where doc_id = ?', term).fetchall()[
                        0]
            except Exception as e:
                print(e)
            # connection is not autocommit by default. So we must commit to save our changes.
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)
        return position

    def get_postings(self, term: str) -> Iterable[Posting]:
        """ Return postings for term literals and ranked queries without positions."""
        position = self.get_position_from_db(term, "vocab")
        postings = []
        with open(str(self.vocab_path), 'rb') as f:
            f.seek(position[0])
            doc_len = struct.unpack('>i', f.read(4))
            prev_document = 0
            for i in range(doc_len[0]):
                doc_id = struct.unpack('>i', f.read(4))
                postings.append(Posting(doc_id[0] + prev_document))
                prev_document = doc_id[0] + prev_document
                term_freq = struct.unpack('>i', f.read(4))
                for j in range(term_freq[0]):
                    f.read(4)
        return postings

    def get_postings_with_positions(self, term: str):
        """Returns doc_id's for phrase literals with positions."""
        position = self.get_position_from_db(term, "vocab")
        postings = [[], []]
        with open(str(self.vocab_path), 'rb') as f:
            for pos in position:
                f.seek(pos)
                doc_len = struct.unpack('>i', f.read(4))
                prev_document = 0
                for i in range(doc_len[0]):
                    doc_id = struct.unpack('>i', f.read(4))
                    if doc_id not in postings[0]:
                        postings[0].append(doc_id[0] + prev_document)
                        postings[1].append([])
                    prev_document = doc_id[0] + prev_document
                    term_freq = struct.unpack('>i', f.read(4))
                    prev_position = 0
                    for j in range(term_freq[0]):
                        term_pos = struct.unpack('>i', f.read(4))
                        postings[1][-1].append(term_pos[0] + prev_position)
                        prev_position = term_pos[0] + prev_position
        return postings

    def get_lds(self, doc_id: int):
        position = self.get_position_from_db(doc_id, "docWeights")
        doc_weight = 0
        with open(str(self.ld_path), 'rb') as f:
            for pos in position:
                f.seek(pos)
                doc_weight = struct.unpack('>d', f.read(8))[0]
        return doc_weight

    def get_termInfo(self, term):
        position = self.get_position_from_db(term, "vocab")
        if position[0]:
            return self.get_postings_with_positions(term)
        else:
            return [[], [[]]]

    def get_biwordTermInfo(self, term):
        position = self.get_position_from_db(term, "biword_vocab")
        postings = []
        with open(str(self.biword_vocab_path), 'rb') as f:
            for pos in position:
                f.seek(pos)
                doc_len = struct.unpack('>i', f.read(4))
                prev_document = 0
                for i in range(doc_len[0]):
                    doc_id = struct.unpack('>i', f.read(4))
                    postings.append(doc_id[0] + prev_document)
                    prev_document += doc_id[0]
        return postings

    def get_vocabulary(self):
        # SQL CONNECTION
        conn, cursor = self.create_db_connection()
        # To delete the table before inserting again
        vocabulary = []
        try:
            result = cursor.execute('select term from vocabulary').fetchall()
            for row in result:
                vocabulary.append(row[0])
        except Exception as e:
            print(e)
        # connection is not autocommit by default. So we must commit to save our changes.
        conn.commit()
        conn.close()
        return vocabulary

    def get_soundex_postings(self, term: str) -> Iterable[Posting]:
        """ Return postings for term literals and ranked queries without positions."""
        # TODO: Implement this
        return []
