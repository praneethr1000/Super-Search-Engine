from pathlib import Path
from documents import DirectoryCorpus
from indexes import Index, PositionalInvertedIndex
from queries import BooleanQueryParser
from text import AdvancedTokenProcessor, EnglishTokenStream
import time

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DirectoryCorpus) -> PositionalInvertedIndex:
    token_processor = AdvancedTokenProcessor()
    positional_inverted_document_index = PositionalInvertedIndex()

    for d in corpus:
        document_content = EnglishTokenStream(d.get_content())
        for position, document in enumerate(document_content):
            tokens = token_processor.process_token(document)
            for token in tokens:
                positional_inverted_document_index.add_term(token, d.id, position + 1)
    return positional_inverted_document_index


def query_check(first_word: str) -> str:
    if first_word == ':q':
        return "quit"
    elif first_word == ':stem':
        return "stem"
    elif first_word == ':index':
        return "index"
    elif first_word == ':vocab':
        return "vocab"
    else:
        return "not special"


def start_program(directory, action):
    corpus_path = Path()
    starttime = time.time()
    if directory == '1':
        corpus_path = corpus_path / 'Json Documents'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    else:
        corpus_path = corpus_path / 'MobyDicks Text Documents'
        corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)
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
            print(words[1])
            if words[1].lower() == 'json':
                start_program('1', "start")
            else:
                start_program('2', "start")
        elif action_to_perform == "vocab":
            start_program(directory, action_to_perform)
        else:
            parser = BooleanQueryParser()
            token_processor = AdvancedTokenProcessor()
            q = parser.parse_query(query)
            found_documents = q.get_postings(index, token_processor)
            if not found_documents:
                print("None of the document contains the term searched for!")
            else:
                for doc in found_documents:
                    print(f"Document ID {doc.doc_id}")
                print("Number of documents with the term: ", len(found_documents))
                see_document_content = input("Do you want to view a document? Type Yes or No: ")
                if see_document_content.lower() == 'yes':
                    document_id = input("Enter the document id that you want to view: ")
                    print("Content", corpus.get_document(int(document_id)).get_content())


def main():
    directory = input(
        "\t  Choose the directory \nEnter 1 to choose Json Documents \n\t\t\t or \nEnter 2 to choose "
        "Text Documents: ")
    start_program(directory, "start")


main()
