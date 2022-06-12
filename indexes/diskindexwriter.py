import struct


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
                    doc_id = struct.pack('>i', document-prev_document)
                    prev_document = document
                    f.write(doc_id)
                    term_freq = struct.pack('>i', len(positions[i]))
                    f.write(term_freq)
                    prev_position = 0
                    for position in positions[i]:
                        f.write(struct.pack('>i', position-prev_position))
                        prev_position = position
        print(d)


