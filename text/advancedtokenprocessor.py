from .tokenprocessor import TokenProcessor
import re
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
        tokens = re.sub(r"^\W+|\W+$", "", token).lower().replace('"', '').replace("'", '').split("-")
        if len(tokens) > 1:
            tokens.append(''.join(tokens))
        return self.stem_tokens(tokens)
