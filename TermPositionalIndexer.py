from pathlib import Path
from documents import DirectoryCorpus
from indexes import Index, PositionalInvertedIndex
from text import BasicTokenProcessor, EnglishTokenStream

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DirectoryCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    positional_inverted_document_index = PositionalInvertedIndex()

    for doc_id, d in enumerate(corpus):
        document_content = EnglishTokenStream(d.get_content())
        for position, document in enumerate(document_content):
            token = token_processor.process_token(document)
            positional_inverted_document_index.add_term(token, doc_id + 1, position + 1)
    return positional_inverted_document_index


if __name__ == "__main__":
    directory = input("Choose the directory. Press \n1.Json Documents \n2. MobyDicks Text Documents: ")
    corpus_path = Path()
    if directory == '1':
        corpus_path = corpus_path / 'Json Documents'
        corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    else:
        corpus_path = corpus_path / 'MobyDicks Text Documents'
        corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)

    # while True:
    #     query = input("\nEnter a term to search or Enter quit to stop: ")
    #     if query.lower() == "quit":
    #         break
    #     found_documents = index.get_postings(query)
    #     if not found_documents:
    #         print("None of the document contains the term searched for!")
    #         continue
    #     for p in index.get_postings(query):
    #         print(f"Document ID {p.doc_id}")
