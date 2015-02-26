from i2b2tools.lib.standoff_annotations import StandoffAnnotation
from i2b2tools.lib.document_token import Document, TokenSequence
from i2b2tools.helpers.utils import has_overlapping_phi

from itertools import islice

def n_tokens(seq, n):
    """Provides a "sliding window" of n tokens from a token sequence."""
    assert isinstance(seq, TokenSequence)

    return zip(*(islice(seq, i, None) for i in range(n)))

def get_sa_tagged_tokens(sa):
    """Returns a list of tuples containing each token in a token
    sequence of the document, and the PHI tag associated with that
    token, if any.
    This does not support StandoffAnnotation's with overlapping PHI.
    """
    def token_in_phi(token, phi):
        return token.start >= phi.get_start() and token.end <= phi.get_end()

    if not isinstance(sa, StandoffAnnotation):
        raise Exception("Argument passed is not a StandoffAnnotation.")
    elif has_overlapping_phi(sa):
        raise Exception("StandoffAnnotation has overlapping PHI.")

    doc = Document(sa.file_name)
    tagged_tokens = []

    for token in doc.token_sequence:
        associated_phi = None

        for phi in doc.get_phi():
            if token_in_phi(token, phi):
                associated_phi = phi

        tagged_tokens.append((token, associated_phi))

    return tagged_tokens
