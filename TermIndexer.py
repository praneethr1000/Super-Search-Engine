from pathlib import Path
from documents import DirectoryCorpus
from indexes import PositionalInvertedIndex, SoundexIndex
from indexes.diskindexwriter import DiskIndexWriter
from queries import BooleanQueryParser
from text import AdvancedTokenProcessor, EnglishTokenStream, BasicTokenProcessor
import time


def index_corpus(corpus: DirectoryCorpus, index: str):
    token_processor = AdvancedTokenProcessor()
    if index == "positional inverted indexing":
        document_index = PositionalInvertedIndex()
    else:
        document_index = SoundexIndex()

    for d in corpus:
        document_content = EnglishTokenStream(d.get_content())
        # Performs both positional inverted indexing and biword indexing
        if index == "positional inverted indexing":
            terms = []
            for term in document_content:
                terms.append(token_processor.process_token(term))
            len_document = len(terms)
            for i in range(len_document - 1):
                term1 = terms[i]
                term2 = ''.join(terms[i + 1])
                document_index.add_term_biword(''.join(term1) + " " + term2, d.id)
                for token in term1:
                    document_index.add_term(token, d.id, i + 1)
            if len_document >= 1:
                final_term = terms[-1]
                for token in final_term:
                    document_index.add_term(token, d.id, len_document)
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
    return document_index


def start_program(directory):
    corpus_path = Path()
    starttime = time.time()
    # Build the index over the selected directory.
    if directory == '1':
        corpus_path = corpus_path / 'Json Documents'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        index = index_corpus(corpus, "positional inverted indexing")
    elif directory == '2':
        corpus_path = corpus_path / 'Mlb Documents'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        index = index_corpus(corpus, "soundex indexing")
    else:
        corpus_path = corpus_path / 'MobyDicks Text Documents'
        corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
        index = index_corpus(corpus, "positional inverted indexing")

    process_queries(index, corpus, starttime)


def process_queries(index, corpus, starttime):
    endtime = time.time()
    print('\nTime taken to load documents is: ', round(endtime - starttime), 'seconds')
    disk_writer = DiskIndexWriter()
    disk_writer.writeIndex(index, "D:\\LongBeach\\Sem2-Summer\\SearchEngineProject\\index\\postings.bin")
    return
    while True:
        display_options()
        query = input("\nEnter a term to search: ")
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
            vocabulary = index.get_vocabulary()
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
            normal_query_parser(first_word, query, index, corpus)


def normal_query_parser(first_word, query, index, corpus):
    parser = BooleanQueryParser()
    token_processor = AdvancedTokenProcessor()
    if first_word == ':author':
        # Checks if it needs basic or advanced token processing based on the Soundex algorithm
        token_processor = BasicTokenProcessor()
        query = token_processor.process_token(query.split()[1])
        found_documents = index.get_postings(query + " author")
    else:
        q = parser.parse_query(query)
        found_documents = q.get_postings(index, token_processor)

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
    directory = input(
        "\t  Choose the directory \nEnter 1 to choose Json Documents \n\t\t\t or \nEnter 2 to choose "
        "Json Documents for Soundex algorithm \n\t\t\t or \nEnter any other key to choose Text documents: ")
    start_program(directory)


if __name__ == "__main__":
    main()
