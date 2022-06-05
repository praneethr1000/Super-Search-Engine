from pathlib import Path
from documents import DirectoryCorpus
from indexes import PositionalInvertedIndex, SoundexIndex
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
        if index == "positional inverted indexing":
            terms = []
            for term in document_content:
                terms.append(token_processor.process_token(term))
            len_document = len(terms)
            for i in range(len_document-1):
                term1 = terms[i]
                term2 = ''.join(terms[i+1])
                document_index.add_term_biword(''.join(term1)+" "+term2, d.id)
                for token in term1:
                    document_index.add_term(token, d.id, i + 1)
            if len_document >= 1:
                final_term = terms[-1]
                for token in final_term:
                    document_index.add_term(token, d.id, len_document)

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


def query_check(first_word: str) -> str:
    if first_word == ':q':
        return "quit"
    elif first_word == ':stem':
        return "stem"
    elif first_word == ':index':
        return "index"
    elif first_word == ':vocab':
        return "vocab"
    elif first_word == ':author':
        return "author"
    else:
        return "not special"


def start_program(directory, action):
    corpus_path = Path()
    starttime = time.time()
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

    if action == "vocab":
        vocabulary = index.get_vocabulary()
        for vocab in range(1000):
            print(vocabulary[vocab])
        print("Total number of vocabulary terms: ", len(vocabulary))

    process_queries(index, directory, corpus, starttime)


def process_queries(index, directory, corpus, starttime):
    endtime = time.time()
    print('Time taken to load documents is: ', endtime - starttime)
    while True:
        query = input("\nEnter a term to search: ")
        words = query.split()
        first_word = words[0].lower()
        action_to_perform = query_check(first_word)
        if action_to_perform == "quit":
            print("Thank you!")
            break
        elif action_to_perform == "stem":
            token_processor = AdvancedTokenProcessor()
            print(*token_processor.stem_tokens([words[1]]))
        elif action_to_perform == "index":
            if words[1].lower() == 'json':
                start_program('1', "start")
            elif words[1].lower() == 'author':
                start_program('2', "start")
            else:
                start_program('3', "start")
        elif action_to_perform == "vocab":
            start_program(directory, action_to_perform)
        else:
            parser = BooleanQueryParser()
            token_processor = AdvancedTokenProcessor()
            if action_to_perform == "author":
                token_processor = BasicTokenProcessor()
                query = token_processor.process_token(query.split()[1])
                found_documents = index.get_postings(query + " author")
            else:
                q = parser.parse_query(query)
                found_documents = q.get_postings(index, token_processor)
            if not found_documents:
                print("None of the document contains the term searched for!")
            else:
                for doc in found_documents:
                    if action_to_perform == "author" or corpus.get_document(
                            int(doc.doc_id)).author != "No info about author":
                        print(
                            f"{str(doc.doc_id) + '.' + corpus.get_document(int(doc.doc_id)).title + ' by ' + corpus.get_document(int(doc.doc_id)).author}")
                    else:
                        print(f"{str(doc.doc_id) + '.' + corpus.get_document(int(doc.doc_id)).title}")
                print("\nNumber of documents with the term: ", len(found_documents))
                see_document_content = input("\nDo you want to view a document? Type Yes or No: ")
                if see_document_content.lower() == 'yes':
                    document_id = input("\nEnter the document id that you want to view: ")
                    print(corpus.get_document(int(document_id)).get_content())


def main():
    directory = input(
        "\t  Choose the directory \nEnter 1 to choose Json Documents \n\t\t\t or \nEnter 2 to choose "
        "Json Documents for Soundex algorithm \n\t\t\t or \nEnter any other key to choose Text documents: ")
    start_program(directory, "start")


main()
