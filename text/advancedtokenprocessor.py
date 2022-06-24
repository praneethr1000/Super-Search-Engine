from .tokenprocessor import TokenProcessor
from porter2stemmer import Porter2Stemmer


class AdvancedTokenProcessor(TokenProcessor):
    """A AdvancedTokenProcessor creates terms from tokens by removing all non-alphanumeric characters
    from the beginning and end of the token, and converting it to all lowercase."""

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        ps = Porter2Stemmer()

        for index, w in enumerate(tokens):
            tokens[index] = ps.stem(w)
        return tokens

    def token_formater(self, token: str) -> str:
        """ Removing all non-alphanumeric characters from the beginning and end of the token """

        while len(token) > 0 and not token[0].isalnum():
            token = token[1:]
        while len(token) > 0 and not token[-1].isalnum():
            token = token[:-1]

        """ Replacing quotes , converting to lower and splitting if hyphen is present """
        term = token.lower().replace('"', '').replace("'", '')
        return term

    def process_token(self, token: str) -> list[str]:
        # Process token with hyphen split
        term = self.token_formater(token)
        tokens = term.split("-")
        output = self.stem_tokens(tokens)
        return output

    def process_token_without_hyphen(self, token: str) -> list[str]:
        # Process token without hyphen split
        term = self.token_formater(token)
        tokens = term.split(" ")
        return self.stem_tokens(tokens)
