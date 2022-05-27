from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index, InvertedIndex
from text import BasicTokenProcessor, EnglishTokenStream

"""This basic program builds a inverted index over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DirectoryCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    inverted_document_index = InvertedIndex()

    for doc_id, d in enumerate(corpus):
        document_content = EnglishTokenStream(d.get_content())
        for document in document_content:
            token = token_processor.process_token(document)
            inverted_document_index.add_term(token, doc_id)

    return inverted_document_index


if __name__ == "__main__":
    corpus_path = Path()
    corpus_path = corpus_path / 'MobyDicks Text Documents'
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(d)

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.
    while True:
        query = input("\nEnter a term to search or Enter quit to stop: ")  # hard-coded search for "whale"
        if query.lower() == "quit":
            break
        found_documents = index.get_postings(query)
        if not found_documents:
            print("None of the document contains the term searched for!")
            continue
        for p in index.get_postings(query):
            print(f"Document ID {p.doc_id}")

    # TODO: fix this application so the user is asked for a term to search.
