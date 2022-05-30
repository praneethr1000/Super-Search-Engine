from pathlib import Path
from documents import DirectoryCorpus
from indexes import Index, PositionalInvertedIndex
from text import AdvancedTokenProcessor, EnglishTokenStream
import time

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DirectoryCorpus) -> PositionalInvertedIndex:
    token_processor = AdvancedTokenProcessor()
    positional_inverted_document_index = PositionalInvertedIndex()

    for doc_id, d in enumerate(corpus):
        document_content = EnglishTokenStream(d.get_content())
        for position, document in enumerate(document_content):
            tokens = token_processor.process_token(document)
            for token in tokens:
                positional_inverted_document_index.add_term(token, doc_id + 1, position + 1)
    return positional_inverted_document_index


def query_check(first_word: str) -> str:
    if first_word[0] == 'q':
        return "quit"
    elif first_word == 'stem':
        return "stem"
    elif first_word == 'index':
        return "directory"
    elif first_word == 'vocab':
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
    endtime = time.time()
    print('Time taken to load documents is: ', endtime - starttime)

    # Build the index over this directory.
    index = index_corpus(corpus)
    if action == "vocab":
        vocabulary = index.get_vocabulary()
        for vocab in range(1000):
            print(vocab)
        print("Total number of vocabulary terms: ", len(vocabulary))
    process_queries(index, directory, corpus)


def process_queries(index, directory, corpus):
    while True:
        query = input("\nEnter a term to search: ")
        words = query.split()
        first_word = words[0].lower()
        action_to_perform = query_check(first_word)
        if action_to_perform == "quit":
            print("Thank you!")
        elif action_to_perform == "stem":
            token_processor = AdvancedTokenProcessor()
            print(*token_processor.stem_tokens([words[1]]))
        elif action_to_perform == "index":
            main()
        elif action_to_perform == "vocab":
            start_program(directory, action_to_perform)
        else:
            term = words[0]
            found_documents = index.get_postings(term)
            if not found_documents:
                print("None of the document contains the term searched for!")
            else:
                for p in index.get_postings(term):
                    print(f"Document ID {p.doc_id}")
                print("Number of documents with the term: ", len(found_documents))
                see_document_content = input("Do you want to view a document? Type Yes or No: ")
                if see_document_content.lower() == 'yes':
                    document_id = input("Enter the document id that you want to view: ")
                    corpus.get_document(document_id)


def main():
    directory = input(
        "\t  Choose the directory \nEnter 1 to choose Json Documents \n\t\t\t or \nEnter 2 to choose "
        "Text Documents: ")
    start_program(directory, "start")


main()
