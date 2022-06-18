import struct
import pyodbc


class DiskIndexWriter:
    def __init__(self):
        self.db_drop = False
        self.db_create = False

    def writeIndex(self, index, path):
        vocab = index.get_vocabulary()
        d = {}
        index_pos = 0
        with open(path, 'wb') as f:
            for term in vocab:
                documents, positions = index.get_termInfo(term)
                len_documents = len(documents)
                doc_len = struct.pack('>i', len_documents)
                d[term] = index_pos
                f.write(doc_len)
                index_pos += 4
                prev_document = 0
                for i, document in enumerate(documents):
                    doc_id = struct.pack('>i', document - prev_document)
                    prev_document = document
                    f.write(doc_id)
                    index_pos += 4
                    term_freq = struct.pack('>i', len(positions[i]))
                    f.write(term_freq)
                    index_pos += 4
                    prev_position = 0
                    for position in positions[i]:
                        f.write(struct.pack('>i', position - prev_position))
                        index_pos += 4
                        prev_position = position
        self.write_to_db(d)

    def write_ld(self, path, ld):
        with open(str(path), 'wb') as f:
            d = {}
            index_pos = 0
            for doc in ld:
                d[doc] = index_pos
                ld_document = struct.pack('>d', float(ld[doc]))
                f.write(ld_document)
                index_pos += 8
        self.write_ld_to_db(d)

    def write_biword(self, index, path):
        vocab = index.get_biword_vocabulary()
        d = {}
        index_pos = 0
        with open(str(path), 'wb') as f:
            for term in vocab:
                documents = vocab[term]
                len_documents = len(documents)
                doc_len = struct.pack('>i', len_documents)
                d[term] = index_pos
                f.write(doc_len)
                index_pos += 4
                prev_document = 0
                for i, document in enumerate(documents):
                    doc_id = struct.pack('>i', document - prev_document)
                    prev_document = document
                    f.write(doc_id)
                    index_pos += 4
        self.write_to_db(d)

    def write_soundex(self, index, disk_path):
        pass
        # TODO: Implement this

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

    def write_ld_to_db(self, ld):
        # SQL CONNECTION
        conn, cursor = self.create_db_connection()
        # To delete the table before inserting again
        try:
            cursor.execute("drop table documentWeight;")
        except Exception as e:
            print(e)
        # To create a table
        try:
            cursor.execute("create table documentWeight(doc_id int, position int);")
        except Exception as e:
            print(e)
        # To insert positions
        for doc_id in ld:
            try:
                cursor.execute("INSERT INTO documentWeight VALUES(?,?)", (doc_id, ld[doc_id]))
            except Exception as e:
                print(e)

        # connection is not autocommit by default. So we must commit to save our changes.
        conn.commit()
        conn.close()

    def write_biword_to_db(self, vocab):
        # SQL CONNECTION
        conn, cursor = self.create_db_connection()
        # To delete the table before inserting again
        try:
            if not self.db_drop:
                cursor.execute("drop table biword_vocabulary;")
        except Exception as e:
            # print(e)
            pass
        self.db_drop = True
        # To create a table
        try:
            if not self.db_create:
                cursor.execute("create table biword_vocabulary(term text, position int);")
        except Exception as e:
            print(e)
        self.db_create = True
        # To insert positions
        for term in vocab:
            try:
                cursor.execute("INSERT INTO biword_vocabulary VALUES(?,?)", (term, vocab[term]))
            except Exception as e:
                print(e)

        # connection is not autocommit by default. So we must commit to save our changes.
        conn.commit()
        conn.close()

    def write_to_db(self, vocab):
        # SQL CONNECTION
        conn, cursor = self.create_db_connection()
        # To delete the table before inserting again
        try:
            if not self.db_drop:
                cursor.execute("drop table vocabulary;")
        except Exception as e:
            # print(e)
            pass
        self.db_drop = True
        # To create a table
        try:
            if not self.db_create:
                cursor.execute("create table vocabulary(term text, position int);")
        except Exception as e:
            print(e)
        self.db_create = True
        # To insert positions
        for term in vocab:
            try:
                cursor.execute("INSERT INTO vocabulary VALUES(?,?)", (term, vocab[term]))
            except Exception as e:
                print(e)

        # connection is not autocommit by default. So we must commit to save our changes.
        conn.commit()
        conn.close()
