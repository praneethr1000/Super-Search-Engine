from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index, TermDocumentIndex
from text import BasicTokenProcessor, EnglishTokenStream

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DirectoryCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    vocabulary = set()

    for d in corpus:
        # print(f"Found document {d.title}")
        document_content = EnglishTokenStream(d.get_content())
        for document in document_content:
            token = token_processor.process_token(document)
            vocabulary.add(token)

        # TODO:
        #   Tokenize the document's content by creating an EnglishTokenStream around the document's .content()
        #   Iterate through the token stream, processing each with token_processor's process_token method.
        #   Add the processed token (a "term") to the vocabulary set.

    term_document_index = TermDocumentIndex(vocabulary, len(corpus))
    doc_id = 0
    for d in corpus:
        document_content = EnglishTokenStream(d.get_content())
        for document in document_content:
            term = token_processor.process_token(document)
            term_document_index.add_term(term, doc_id)
        doc_id += 1
    return term_document_index

    # TODO:
    # After the above, next:
    # Create a TermDocumentIndex object, with the vocabular you found, and the len() of the corpus.
    # Iterate through the documents in the corpus:
    #   Tokenize each document's content, again.
    #   Process each token.
    #   Add each processed term to the index with .add_term().


if __name__ == "__main__":
    corpus_path = Path()
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
