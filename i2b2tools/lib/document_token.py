from standoff_annotations import StandoffAnnotation, get_predicate_function
from collections import defaultdict
import os
import types
import re
import copy

class Token(object):
    """ Class designed to encapsulate the idea of a token.  This includes
    the token itself,  plus pre and post whitespace,  as well as the start and
    end positions of the token with-in the document that the token was parsed
    out of.  It also includes an 'index' attribute that can be set by external
    functions and classes (see TokenSequence).
    """
    def __init__(self, token, pre_ws, post_ws, index, start, end):
        self.token = token
        self.start = int(start)
        self.end = int(end)
        self.index = int(index)

        # pre whitespace
        self.pre_ws = pre_ws
        # post whitespace
        self.post_ws = post_ws


    def __repr__(self):
        return "<{}: {}, {}, {}, i:{}, s:{}, e:{}>".format(self.__class__.__name__,
                                                           self.pre_ws.__repr__(),
                                                           self.token.__repr__(),
                                                           self.post_ws.__repr__(),
                                                           self.index,
                                                           self.start, self.end)

    def __str__(self):
        return self.token + self.post_ws

    def __len__(self):
        return len(str(self))

    def __hash__(self):
        return hash(self.start, self.end)

    def __eq__(self, other):
        """ Test the equality of two tokens. Based on start and end values.
        """
        if other.start == self.start and other.end == self.end:
            return True

        return False

class TokenSequence(object):
    """ Encapsulates the functionality of a sequence of tokens.  it is designed
    to parse using the tokenizer() classmethod,  but can use any other subclassed
    method as long as it returns a list of Token() objects.
    """
    tokenizer_re = re.compile(r'(\w+)')

    @classmethod
    def tokenizer(cls, text, start=0):

        # This could be a one-liner,  but we'll split it up
        # so its a litle clearer.

        # This generates a list of strings in the form
        # [WHTEPSACE, TOKEN, WHITESPACE, TOKEN ...]
        split_tokens = re.split(cls.tokenizer_re, text)

        # This generates trigrams from the list in the form
        # [(WHITESPACE, TOKEN, WHITESPACE),
        #  (TOKEN, WHITESPACE, TOKEN),
        #  (WHITESPACE, TOKEN, WHITESPACE)
        #  .... ]
        token_trigrams =  zip(*[split_tokens[i:] for i in range(3)])

        # This keeps only odd tuples from token trigrams,  ie:
        # [(WHITESPACE, TOKEN, WHITESPACE),
        #  (WHITESPACE, TOKEN, WHITESPACE),
        #  (WHITESPACE, TOKEN, WHITESPACE)
        #  .... ]
        token_tuples = [t for i,t in enumerate(token_trigrams) if not bool(i & 1)]

        tokens = []
        index = 0

        # Add a dummy token that accounts for the leading whitespace
        # But only if we're starting at the begining of a document
        # If we're dealing with a tag or some other mid-document location
        # skip this part
        if start == 0:
            tokens.append(Token("", "", split_tokens[0], index, 0, 0))
            index += 1

        # Calculate start and end positions of the non-whitespace/punctuation
        # and append the token with its index into the list of tokens.
        for pre, token, post in token_tuples:
            token_start = start + len(pre)
            token_end = token_start + len(token)
            start = token_end
            tokens.append(Token(token, pre, post, index, token_start, token_end))
            index += 1



        return tokens


    def __init__(self, text, tokenizer=None, start=0):


        tokenizer = TokenSequence.tokenizer if tokenizer == None else tokenizer

        if hasattr(text, "__iter__"):
            self.text = ''.join(str(t) for t in text)
            self.tokens = text

        else:
            self.text = text
            self.tokens = tokenizer(self.text, start=start)

        # If start is 0 we assume we're parsing a whole document
        # and not a sub-string of tokens.
        if start == 0:
            assert len(self.text) == sum(len(t) for t in self.tokens), \
                "Tokenizer MUST return a list of strings with character " \
                "length equal to text length"



    def __str__(self):
        return ''.join([str(t).encode("string_escape") for t in self.tokens])


    def __repr__(self):
        return "<{} '{}', s:{}, e:{}>".format(self.__class__.__name__,
                                            str(self) if len(str(self)) < 40 else str(self)[:37] + "...",
                                            self[0].start,
                                            self[-1].end)


    def __len__(self):
        return len(self.tokens)


    def __getitem__(self, index):
        return self.tokens[index]


    def __iter__(self):
        return self.tokens.__iter__()

    def next(self):
        return self.tokens.next()


    def subseq(self, other):
        """Test if we are a subsequence of other"""
        return all([t in other.tokens for t in self.tokens])


    def tokens_before(self, token, N):
        try:
            start_index = self.tokens.index(token)
            return TokenSequence([copy.deepcopy(t) for t in self.tokens[start_index-N:start_index]])
        except ValueError:
            return None

    def tokens_after(self, token, N):
        try:
            end_index = self.tokens.index(token)
            return TokenSequence([copy.deepcopy(t) for t in self.tokens[end_index + 1:end_index + N + 1]])
        except ValueError:
            return None


class Document(StandoffAnnotation):
    def __init__(self, file_name=None, root="root"):
        super(Document, self).__init__(file_name=file_name, root=root)

    @property
    def token_sequence(self):
        if self._tokens == None:
            self._tokens = TokenSequence(self.text, TokenSequence.tokenizer)

        return self._tokens


    def tag_to_token_sequence(self, tag):
        try:
            seq = TokenSequence(tag.text, start=int(tag.start))
            for token in seq:
                try:
                    token.index = self.token_sequence.tokens.index(token)
                except ValueError:
                    token.index = None
            return seq
        except:
            return []


    def _with_token_sequences(self, func):
        return [(tag, self.tag_to_token_sequence(tag)) for tag in func()]

    def tags_with_token_sequences(self):
        return self._with_token_sequences(self.get_tags)

    def phi_with_token_sequences(self):
        return self._with_token_sequences(self.get_phi)
