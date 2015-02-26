from i2b2tools.helpers.utils import phi_within_range

# this is mostly to be used as an example predicate
# it works with a MergeRule to say:
# <DATE>1</DATE>2<DATE>3</DATE>
# then merge these 3 tags as one date

# this function specifically determines whether or not the above
# situation *exists*
def _trigram_name_predicate(target, rule):
    """ Target is a tuple of trigrams, rule is a Rule object, which allows access to the sa. """
    token1, token2, token3 = target
    token1 = phi_within_range(rule.sa, token1.start, token1.end)
    token2 = phi_within_range(rule.sa, token2.start, token2.end)
    token3 = phi_within_range(rule.sa, token3.start, token3.end)

    if token1 and not token2 and token3:
        if token1.name == token3.name == rule.name:
            return True

    return False
