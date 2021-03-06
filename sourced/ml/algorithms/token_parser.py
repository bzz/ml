import re

import Stemmer


class TokenParser:
    """
    Common utilities for splitting and stemming tokens.
    """
    NAME_BREAKUP_RE = re.compile(r"[^a-zA-Z]+")  #: Regexp to split source code identifiers.
    STEM_THRESHOLD = 6  #: We do not stem splitted parts shorter than or equal to this size.
    MAX_TOKEN_LENGTH = 256  #: We cut identifiers longer than this value.
    MIN_SPLIT_LENGTH = 3  #: We do not split source code identifiers shorter than this value.

    def __init__(self, stem_threshold=STEM_THRESHOLD, max_token_length=MAX_TOKEN_LENGTH,
                 min_split_length=MIN_SPLIT_LENGTH):
        self._stemmer = Stemmer.Stemmer("english")
        self._stemmer.maxCacheSize = 0
        self._stem_threshold = stem_threshold
        self._max_token_length = max_token_length
        self._min_split_length = min_split_length

    @property
    def stem_threshold(self):
        return self._stem_threshold

    @stem_threshold.setter
    def stem_threshold(self, value):
        if not isinstance(value, int):
            raise TypeError("stem_threshold must be an integer - got %s" % type(value))
        if value < 1:
            raise ValueError("stem_threshold must be greater than 0 - got %d" % value)
        self._stem_threshold = value

    @property
    def max_token_length(self):
        return self._max_token_length

    @max_token_length.setter
    def max_token_length(self, value):
        if not isinstance(value, int):
            raise TypeError("max_token_length must be an integer - got %s" % type(value))
        if value < 1:
            raise ValueError("max_token_length must be greater than 0 - got %d" % value)
        self._max_token_length = value

    @property
    def min_split_length(self):
        return self._min_split_length

    @min_split_length.setter
    def min_split_length(self, value):
        if not isinstance(value, int):
            raise TypeError("min_split_length must be an integer - got %s" % type(value))
        if value < 1:
            raise ValueError("min_split_length must be greater than 0 - got %d" % value)
        self._min_split_length = value

    def __call__(self, token):
        return self.process_token(token)

    def process_token(self, token):
        for word in self.split(token):
            yield self.stem(word)

    def stem(self, word):
        if len(word) <= self.stem_threshold:
            return word
        return self._stemmer.stemWord(word)

    def split(self, token):
        token = token.strip()[:self.max_token_length]
        prev_p = [""]

        def ret(name):
            r = name.lower()
            if len(name) >= self.min_split_length:
                yield r
                if prev_p[0]:
                    yield prev_p[0] + r
                    prev_p[0] = ""
            else:
                prev_p[0] = r

        for part in self.NAME_BREAKUP_RE.split(token):
            if not part:
                continue
            prev = part[0]
            pos = 0
            for i in range(1, len(part)):
                this = part[i]
                if prev.islower() and this.isupper():
                    yield from ret(part[pos:i])
                    pos = i
                elif prev.isupper() and this.islower():
                    if 0 < i - 1 - pos <= 3:
                        yield from ret(part[pos:i - 1])
                        pos = i - 1
                    elif i - 1 > pos:
                        yield from ret(part[pos:i])
                        pos = i
                prev = this
            last = part[pos:]
            if last:
                yield from ret(last)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_stemmer"]
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self._stemmer = Stemmer.Stemmer("english")


class NoopTokenParser:
    """
    One can use this class if he or she does not want to do any parsing.
    """

    def process_token(self, token):
        yield token

    def __call__(self, token):
        return self.process_token(token)
