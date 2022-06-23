import collections
import heapq
import math
import os
from pathlib import Path
from documents import DirectoryCorpus
from indexes import PositionalInvertedIndex
from indexes.diskindexwriter import DiskIndexWriter
from indexes.diskpositionalindex import DiskPositionalIndex
from text import AdvancedTokenProcessor, EnglishTokenStream
from numpy import log


def index_corpus(corpus: DirectoryCorpus):
    print("\nIndexing started")
    token_processor = AdvancedTokenProcessor()
    document_index = PositionalInvertedIndex()
    ld = {}
    byteSize = {}
    docLenA = 0
    docLenD = {}
    aveTftd = {}
    for d in corpus:
        byteSize[d.id] = os.path.getsize(d.path)
        document_content = EnglishTokenStream(d.get_content())
        terms = []
        for term in document_content:
            terms.append(token_processor.process_token(term))
        len_document = len(terms)
        docLenD[d.id] = len_document
        docLenA += len_document
        tftd = {}
        for i in range(len_document - 1):
            term1 = terms[i]
            term2 = ''.join(terms[i + 1])
            document_index.add_term_biword(''.join(term1) + " " + term2, d.id)
            for token in term1:
                if token in tftd:
                    tftd[token] += 1
                else:
                    tftd[token] = 1
                document_index.add_term(token, d.id, i + 1)
        if len_document >= 1:
            final_term = terms[-1]
            for token in final_term:
                if token in tftd:
                    tftd[token] += 1
                else:
                    tftd[token] = 1
                document_index.add_term(token, d.id, len_document)
        wftd = 0
        len_tokens = len(tftd.keys())
        if len_tokens:
            aveTftd[d.id] = sum(tftd.values()) / len(tftd.keys())
        else:
            aveTftd[d.id] = 0
        for key in tftd:
            wftd += (1 + log(tftd[key])) ** 2
        ld[d.id] = math.sqrt(wftd)
    print("\nIndexing Done")
    docLenA = docLenA / len(corpus)
    disk_writer = DiskIndexWriter()
    directory_path = Path()
    disk_path = directory_path / 'index\\docWeights.bin'
    disk_writer.write_docAtt(disk_path, ld, docLenD, byteSize, aveTftd)
    disk_path = directory_path / 'index\\docLength.bin'
    disk_writer.write_docLen(disk_path, docLenA)
    return document_index, disk_writer


def write_to_disk(index, disk_writer):
    directory_path = Path()
    disk_path = directory_path / 'index\\postings.bin'
    disk_writer.writeIndex(index, disk_path)
    disk_path = directory_path / 'index\\postings_biword.bin'
    disk_writer.write_biword(index, disk_path)


def start_program():
    corpus_path = Path()
    # Build the index over the selected directory.
    corpus_path = corpus_path / 'relevance_cranfield'
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    index, disk_writer = index_corpus(corpus)
    write_to_disk(index, disk_writer)
    ranked_retrieval(corpus)


def default(disk_index, N, acc, postings_list, terms, strategy):
    for term in terms:
        postings = postings_list[term]
        Dft = len(postings[0])
        Wqt = log(1 + (N / Dft)) if strategy == "default" else log(N / Dft)
        for doc in postings[0]:
            tftd = len(postings[1][postings[0].index(doc)])
            wdt = 1 + log(tftd) if strategy == "default" else tftd
            acc[doc] += (Wqt * wdt)
    Ld = disk_index.get_docAtt_default(list(acc.keys()))
    for index, doc in enumerate(acc.keys()):
        acc[doc] /= Ld[doc]
    return acc


def okapi(disk_index, N, acc, postings_list, terms):
    doc_lenA = disk_index.get_docLen()
    docs = set()
    for term in terms:
        postings = postings_list[term]
        docs.update(postings[0])
    doc_lenD = disk_index.get_docAtt_okapi(list(docs))
    for term in terms:
        postings = postings_list[term]
        Dft = len(postings[0])
        Wqt = max(0.1, log((N - Dft + 0.5) / (Dft + 0.5)))
        for doc in postings[0]:
            tftd = len(postings[1][postings[0].index(doc)])
            val2 = (1.2 * (0.25 + (0.75 * (doc_lenD[doc] / doc_lenA)))) + tftd
            wdt = (2.2 * tftd) / val2
            acc[doc] += (Wqt * wdt)
    return acc


def wacky(disk_index, N, acc, postings_list, terms):
    docs = set()
    for term in terms:
        postings = postings_list[term]
        docs.update(postings[0])
    byte_sizeD, ave_tftdD = disk_index.get_docAtt_wacky(list(docs))
    for term in terms:
        postings = postings_list[term]
        Dft = len(postings[0])
        Wqt = max(0, log((N - Dft) / Dft))
        for doc in postings[0]:
            tftd = len(postings[1][postings[0].index(doc)])
            val2 = 1 + (log(ave_tftdD[doc]))
            wdt = (1 + log(tftd)) / val2
            acc[doc] += (Wqt * wdt)
    for doc in acc.keys():
        acc[doc] /= byte_sizeD[doc]
    return acc


def compare_with_relavant(nlargest, corpus):
    directory_path = Path()
    rel_docs_path = directory_path / 'relevance_cranfield\\relevance\\qrel'
    with open(str(rel_docs_path), 'r') as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]
    rel_ids = lines[0]
    print(rel_ids)
    ind = 0
    for score, doc_id in nlargest:
        ind += 1
        if str(doc_id+1) in rel_ids:
            file_name = str(corpus.get_document(int(doc_id)).path).split("\\")[1]
            print("Relevant: " + file_name + " at index " + str(ind))
            # print(f"{str(doc_id) + '. ' + str(corpus.get_document(int(doc_id)).path) + ' --- Acc: ' + str(score)}")


def ranked_retrieval(corpus):
    directory_path = Path()
    vocab_disk_path = directory_path / 'index\\postings.bin'
    ld_disk_path = directory_path / 'index\\docWeights.bin'
    biword_vocab_disk_path = directory_path / 'index\\postings_biword.bin'
    soundex_vocab_disk_path = directory_path / 'index\\postings_soundex.bin'
    disk_index = DiskPositionalIndex(vocab_disk_path, ld_disk_path, biword_vocab_disk_path, soundex_vocab_disk_path)
    N = len(corpus.documents())
    while True:
        ranking_strategy = input(
            "\nChoose a ranking strategy\n \n1.Default \n2.Traditional \n3.Okapi BM25 \n4.Wacky\n5.Quit\n")
        if ranking_strategy == '5':
            print("Thank you!")
            break
        query = input("\nEnter a query to search: ")
        terms = query.lower().split()
        # To handle exit
        if ranking_strategy == '5':
            print("Thank you!")
            break
        token_processor = AdvancedTokenProcessor()
        acc = collections.defaultdict(float)
        processed_terms = []
        for term in terms:
            processed_terms.append(''.join(token_processor.process_token_without_hyphen(term)))
        postings_list = disk_index.get_postings_with_positions_list(processed_terms)
        if ranking_strategy == '2':
            acc = default(disk_index, N, acc, postings_list, processed_terms, "traditional")
        elif ranking_strategy == '3':
            acc = okapi(disk_index, N, acc, postings_list, processed_terms)
        elif ranking_strategy == '4':
            acc = wacky(disk_index, N, acc, postings_list, processed_terms)
        else:
            acc = default(disk_index, N, acc, postings_list, processed_terms, "default")
        heap = [(score, doc_id) for doc_id, score in acc.items()]
        nlargest = heapq.nlargest(50, heap)
        compare_with_relavant(nlargest, corpus)
        # for score, doc_id in nlargest:
        #     print(f"{str(doc_id) + '. ' + str(corpus.get_document(int(doc_id)).path) + ' --- Acc: ' + str(score)}")


if __name__ == "__main__":
    disk = input(
        "\t  Choose the option \nEnter 1 to do indexing and write to disk \n\t\t\t or \nEnter other key to load from disk: ")
    if disk != '1':
        corpus_path = Path()
        # Build the index over the selected directory.
        corpus_path = corpus_path / 'relevance_cranfield'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        # To initialize title and author name
        for _ in corpus:
            pass
        ranked_retrieval(corpus)
    else:
        start_program()
