import collections
import heapq
import math
from pathlib import Path
from documents import DirectoryCorpus
from indexes import PositionalInvertedIndex, SoundexIndex
from indexes.diskindexwriter import DiskIndexWriter
from indexes.diskpositionalindex import DiskPositionalIndex
from queries import BooleanQueryParser
from text import AdvancedTokenProcessor, EnglishTokenStream, BasicTokenProcessor
import time
from numpy import log


def index_corpus(corpus: DirectoryCorpus, index: str):
    token_processor = AdvancedTokenProcessor()
    if index == "positional inverted indexing":
        document_index = PositionalInvertedIndex()
    else:
        document_index = SoundexIndex()
    ld = {}
    for d in corpus:
        document_content = EnglishTokenStream(d.get_content())
        # Performs both positional inverted indexing and biword indexing
        if index == "positional inverted indexing":
            terms = []
            for term in document_content:
                terms.append(token_processor.process_token(term))
            len_document = len(terms)
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
            for key in tftd:
                wftd += (1 + log(tftd[key])) ** 2
            ld[d.id] = math.sqrt(wftd)
        # Performs soundex indexing
        else:
            for document in document_content:
                tokens = token_processor.process_token(document)
                for token in tokens:
                    document_index.add_term(token, d.id, "body")
            token_processor = BasicTokenProcessor()
            documents_author = EnglishTokenStream(d.author)
            for author in documents_author:
                token = token_processor.process_token(author)
                document_index.add_term(token, d.id, "author")
    disk_writer = DiskIndexWriter()
    directory_path = Path()
    disk_path = directory_path / 'index\\docWeights.bin'
    disk_writer.write_ld(disk_path, ld)
    return document_index, disk_writer


def write_to_disk(index, disk_writer):
    directory_path = Path()
    disk_path = directory_path / 'index\\postings.bin'
    disk_writer.writeIndex(index, disk_path)
    disk_path = directory_path / 'index\\postings_biword.bin'
    disk_writer.write_biword(index, disk_path)


def start_program(directory):
    corpus_path = Path()
    starttime = time.time()
    # Build the index over the selected directory.
    if directory == '1':
        corpus_path = corpus_path / 'Json Documents'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        index, disk_writer = index_corpus(corpus, "positional inverted indexing")
        write_to_disk(index, disk_writer)
    elif directory == '2':
        disk_path = corpus_path / 'index\\postings_soundex.bin'
        corpus_path = corpus_path / 'Mlb Documents'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        index, disk_writer = index_corpus(corpus, "soundex indexing")
        disk_writer.write_soundex(index, disk_path)
    else:
        corpus_path = corpus_path / 'MobyDicks Text Documents'
        corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
        index, disk_writer = index_corpus(corpus, "positional inverted indexing")
        write_to_disk(index, disk_writer)
    query_type = input(
        "\n\t  Choose the option \nEnter 1 for Boolean Retrieval \n\t\t\t or \nEnter other key for Ranked Retrieval: ")
    if query_type == '1':
        process_queries(corpus, starttime, directory)
    else:
        ranked_retrieval(corpus)


def process_queries(corpus, starttime, directory):
    endtime = time.time()
    print('\nTime taken to load documents is: ', round(endtime - starttime), 'seconds')
    while True:
        display_options()
        query = input("\nEnter a query to search: ")
        directory_path = Path()
        vocab_disk_path = directory_path / 'index\\postings.bin'
        ld_disk_path = directory_path / 'index\\docWeights.bin'
        biword_vocab_disk_path = directory_path / 'index\\postings_biword.bin'
        soundex_vocab_disk_path = directory_path / 'index\\postings_soundex.bin'
        disk_index = DiskPositionalIndex(vocab_disk_path, ld_disk_path, biword_vocab_disk_path, soundex_vocab_disk_path)
        words = query.lower().split()
        first_word = words[0]

        # To handle Special queries
        if first_word == ':q':
            print("Thank you!")
            break
        elif first_word == ':stem':
            token_processor = AdvancedTokenProcessor()
            print(*token_processor.stem_tokens(words[1:]))
        elif first_word == ':index':
            pair = {'json': '1', 'author': '2'}
            second_word = words[1]
            if second_word in pair:
                start_program(pair[second_word])
            else:
                start_program('3')
            break
        elif first_word == ':vocab':
            vocabulary = disk_index.get_vocabulary(directory)
            len_vocab = len(vocabulary)
            print()
            if len_vocab < 1000:
                for vocab in range(len_vocab):
                    print(vocabulary[vocab])
            else:
                for vocab in range(1000):
                    print(vocabulary[vocab])
            print("\nTotal number of vocabulary terms: ", len(vocabulary))
        else:
            normal_query_parser(first_word, query, corpus, disk_index)


def normal_query_parser(first_word, query, corpus, disk_index):
    parser = BooleanQueryParser()
    token_processor = AdvancedTokenProcessor()
    if first_word == ':author':
        # Checks if it needs basic or advanced token processing based on the Soundex algorithm
        token_processor = BasicTokenProcessor()
        query = token_processor.process_token(query.split()[1])
        found_documents = disk_index.get_soundex_postings(query + " author")
    else:
        q = parser.parse_query(query)
        found_documents = q.get_postings(disk_index, token_processor)
    if not found_documents:
        print("\nNone of the document contains the term searched for!")
    else:
        print("\nThe documents with the searched term \n")
        for doc in found_documents:
            # Prints the author name with title if available else prints the title alone
            if first_word == ':author' or corpus.get_document(int(doc.doc_id)).author != "No info about author":
                print(
                    f"{str(doc.doc_id) + '. ' + corpus.get_document(int(doc.doc_id)).title + ' by ' + corpus.get_document(int(doc.doc_id)).author}")
            else:
                print(f"{str(doc.doc_id) + '. ' + corpus.get_document(int(doc.doc_id)).title}")

        print("\nNumber of documents with the term: ", len(found_documents))

        see_document_content = input(
            "\nDo you want to view a document? Type Yes to view a document or any other word to skip: ")
        if see_document_content.lower() == 'yes':
            document_id = input("\nEnter the document id that you want to view: ")
            print()
            try:
                print(corpus.get_document(int(document_id)).get_content())
            except Exception:
                print("\nPlease enter integer value")


def ranked_retrieval(corpus):
    query = input("\nEnter a query to search: ")
    directory_path = Path()
    vocab_disk_path = directory_path / 'index\\postings.bin'
    ld_disk_path = directory_path / 'index\\docWeights.bin'
    biword_vocab_disk_path = directory_path / 'index\\postings_biword.bin'
    soundex_vocab_disk_path = directory_path / 'index\\postings_soundex.bin'
    disk_index = DiskPositionalIndex(vocab_disk_path, ld_disk_path, biword_vocab_disk_path, soundex_vocab_disk_path)
    terms = query.lower().split()
    acc = collections.defaultdict(float)
    N = len(corpus.documents())
    token_processor = AdvancedTokenProcessor()
    for term in terms:
        term = ''.join(token_processor.process_token_without_hyphen(term))
        postings = disk_index.get_postings_with_positions(term)
        Dft = len(postings[0])
        Wqt = log(1 + (N / Dft))
        for doc in postings[0]:
            tftd = len(postings[1][postings[0].index(doc)])
            wdt = 1 + log(tftd)
            acc[doc] += (Wqt * wdt)

    for doc in acc.keys():
        Ld = disk_index.get_lds(doc)
        acc[doc] /= Ld
    heap = [(score, doc_id) for doc_id, score in acc.items()]
    nlargest = heapq.nlargest(10, heap)
    for score, doc_id in nlargest:
        print(f"{str(doc_id) + '. ' + corpus.get_document(int(doc_id)).title + ' Acc: ' + str(score)}")


def display_options():
    print("""
    <-----  Possible options ---- >
    1. Enter :q to quit
    2. Enter :stem token to print the stemmed term.
    3. Enter :index directoryname - to index that particular directory and query in it
        a> :index json (For json files)
        b> :index author (For soundex json files)
        c> :index txt (For text files) -> This is a default if you query :index anything
    4. Enter :vocab to print the first 1000 vocabulary    
    """)


def main():
    disk = input(
        "\t  Choose the option \nEnter 1 to do indexing and write to disk \n\t\t\t or \nEnter other key to load from disk: ")
    directory = input(
        "\n\t  Choose the directory \nEnter 1 to choose Json Documents \n\t\t\t or \nEnter 2 to choose "
        "Json Documents for Soundex algorithm \n\t\t\t or \nEnter any other key to choose Text documents: ")
    if disk != '1':
        corpus_path = Path()
        starttime = time.time()
        # Build the index over the selected directory.
        if directory == '1':
            corpus_path = corpus_path / 'Json Documents'
            corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        elif directory == '2':
            corpus_path = corpus_path / 'Mlb Documents'
            corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        else:
            corpus_path = corpus_path / 'MobyDicks Text Documents'
            corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
        # To initialize title and author name
        for _ in corpus:
            pass
        query_type = input(
            "\n\t  Choose the option \nEnter 1 for Boolean Retrieval \n\t\t\t or \nEnter other key for Ranked Retrieval: ")
        if query_type == '1':
            process_queries(corpus, starttime, directory)
        else:
            ranked_retrieval(corpus)
    else:
        start_program(directory)


if __name__ == "__main__":
    main()
