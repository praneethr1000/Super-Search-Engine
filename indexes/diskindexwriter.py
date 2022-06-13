import struct

import pyodbc

from indexes.diskpositionalindex import DiskPositionalIndex


class DiskIndexWriter:
    def writeIndex(self, index, path):
        vocab = index.get_vocabulary()
        d = {}
        with open(str(path), 'wb') as f:
            for term in vocab:
                documents, positions = index.get_termInfo(term)
                len_documents = len(documents)
                doc_len = struct.pack('>i', len_documents)
                f.write(doc_len)
                prev_document = 0
                for i, document in enumerate(documents):
                    d[term] = f.tell()
                    doc_id = struct.pack('>i', document - prev_document)
                    prev_document = document
                    f.write(doc_id)
                    term_freq = struct.pack('>i', len(positions[i]))
                    f.write(term_freq)
                    prev_position = 0
                    for position in positions[i]:
                        f.write(struct.pack('>i', position - prev_position))
                        prev_position = position
        # with open(str(path), 'rb') as f:
        #     f.seek(4)
        #     print(struct.unpack('>i', f.read(4)))
        #     f.seek(20)
        #     print(struct.unpack('>i', f.read(4)))
        print(d)
        self.write_to_db(d)
        d = DiskPositionalIndex(path)
        d.get_postings('among')


    def write_to_db(self, vocab):
        # SQL CONNECTION
        try:
            conn = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-0BSMBQL\SQLEXPRESS;'
                                  'Database=search_engine;'
                                  'Trusted_Connection=yes;')
            cursor = conn.cursor()
            # To delete the table before inserting again
            try:
                cursor.execute("drop table vocabulary;")
            except Exception as e:
                print(e)
            # To create a table
            try:
                cursor.execute("create table vocabulary(term text, position int);")
            except Exception as e:
                print(e)
            # To insert positions
            for term in vocab:
                try:
                    cursor.execute("INSERT INTO vocabulary VALUES(?,?)", (term, vocab[term]))
                except Exception as e:
                    print(e)

            # connection is not autocommit by default. So we must commit to save our changes.
            conn.commit()
            conn.close()

        except Exception as e:
            print(e)
