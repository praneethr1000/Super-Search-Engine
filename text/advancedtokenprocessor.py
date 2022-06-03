from .tokenprocessor import TokenProcessor
from nltk.stem import PorterStemmer


class AdvancedTokenProcessor(TokenProcessor):
    """A AdvancedTokenProcessor creates terms from tokens by removing all non-alphanumeric characters
    from the beginning and end of the token, and converting it to all lowercase."""

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        ps = PorterStemmer()

        for index, w in enumerate(tokens):
            tokens[index] = ps.stem(w)
        return tokens

    def process_token(self, token: str) -> list[str]:
        """ Removing all non-alphanumeric characters from the beginning and end of the token """

        while len(token) > 0 and not token[0].isalnum():
            token = token[1:]
        while len(token) > 0 and not token[-1].isalnum():
            token = token[:-1]

        """ Replacing quotes , converting to lower and splitting if hyphen is present """

        tokens = token.lower().replace('"', '').replace("'", '').split("-")

        if len(tokens) > 1:
            tokens.append(''.join(tokens))
        return self.stem_tokens(tokens)
