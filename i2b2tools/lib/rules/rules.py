from i2b2tools.helpers.tokens import n_tokens
from i2b2tools.helpers.utils import phi_within_range

from lxml import etree
import re

class Rule(object):
    """Each instance of a rule has a specific StandoffAnnotation
    which it references.
    """
    sa = None

    def __init__(self, sa):
        self.sa = sa

    def targets(self):
        return []

    def action(self, target):
        """This is a mutable action, potentially altering the StandoffAnnotation
        object. target is any one of self.targets() unless otherwise determined
        by self.apply.
        """
        pass

    def apply(self):
        """How a rule should act on a target."""
        for target in self.targets():
            self.action(target)

class RegexRule(Rule):
    """This takes a regular expression and what it should be deemed in
    terms of a tag for example, mark all instances of John/john as a
    person:
    RegexRule, ["([Jj]ohn)", "NAME", "PERSON", NameTag]

    The regex needs to conform to match_group, meaning the part of the
    regex that needs to be marked corresponds to a matching group in the
    regex.
    """
    regex = None
    to_name = None
    to_type = None
    tag_class = None
    ignore_case = 0
    match_group = 0

    def __init__(self, sa, regex, to_name, to_type, tag_class, ignore_case=0,
                 match_group=0):
        super(RegexRule, self).__init__(sa)

        self.regex = regex
        self.to_name = to_name
        self.to_type = to_type
        self.tag_class = tag_class
        self.ignore_case = re.IGNORECASE if ignore_case else 0
        self.match_group = match_group

    def targets(self):
        return re.findall(self.regex, self.sa.text, self.ignore_case)

    def action(self, target):
        whole_match = target[0]
        to_mark_as_phi = target[self.match_group]

        start = str(self.sa.text.index(whole_match) +
                    whole_match.index(to_mark_as_phi))
        end = str(int(start) + len(to_mark_as_phi))

        to_delete = []

        for phi in self.sa.get_phi():
            if int(phi.start) >= int(start) and int(phi.end) <= int(end):
                to_delete.append(phi)

        for phi in to_delete:
            self.sa.phi.remove(phi)

        el = etree.Element(self.to_name,
                           attrib={"start": start,
                                   "end": end,
                                   "TYPE": self.to_type,
                                   "comment": "",
                                   "text": self.sa.text[int(start):int(end)]})

        self.sa.phi.append(self.tag_class(el))

class RemoveRegexRule(Rule):
    """
    Example being we have dates such as this:
    <DATE>10/5/2015</DATE>

    But in fact, we only want our PHI to match "10/5", so we can
    trim it using a RemoveRegexRule as follows:
    RemoveRegexRule, ["\d{1,2}\/\d{1,2}(/\d{2,4})"], 0
    """
    def __init__(self, sa, regex, trim_group=None, ignore_case=0):
        self.sa = sa
        self.regex = regex
        self.trim_group = trim_group
        self.ignore_case = ignore_case

    def targets(self):
        return [phi for phi in self.sa.get_phi() \
                if re.match(self.regex, phi.text, self.ignore_case)]

    def action(self, target):
        """The idea of a 'trim group' is that we don't want to remove
        the regex entirely, but it overmatches.

        For example:
        If we considered 04/19 a date, but we actually matched 04/19/2005
        We could create a remove regex rule with the following regex:
        \d{2}/\d{2}(/\d{4}) - and include a trim group of 0, this would
        'trim' the trailing /2005 from our match.

        This assumes the group is at the beginning or end, since we
        don't want to split a PHI into 2 just yet.

        If there is no trim group however, just get rid of the PHI
        entirely.
        """
        if self.trim_group is None:
            self.sa.phi.remove(target)
        else:
            trim_group_text = re.match(self.regex, target.text).groups()
            trim_group_text = trim_group_text[self.trim_group]

            if target.text.startswith(trim_group_text):
                target.start = str(int(target.start) + len(trim_group_text))
            elif target.text.endswith(trim_group_text):
                target.end = str(int(target.end) - len(trim_group_text))

class MergeRule(Rule):
    """This merges multiple PHI into one based on a predicate function.

    A good example is using helpers.predicates._trigram_name_predicate
    to solve an issue such as:
    <NAME>Edgar</NAME> Allan <NAME>Poe</NAME>
    This could be rectified as:
    <NAME>Edgar Allan Poe</NAME>

    Using a merge rule such as:
    MergeRule, [3, "NAME", "POET", NameTag, _trigram_name_predicate]
    """
    n = 1
    name = None
    TYPE = None
    name_tag = None
    merge_predicate = None

    def __init__(self, sa, n, name, TYPE, name_tag, merge_predicate):
        super(MergeRule, self).__init__(sa)

        self.n = n
        self.name = name
        self.TYPE = TYPE
        self.name_tag = name_tag
        self.merge_predicate = merge_predicate

    def targets(self):
        return n_tokens(self.sa.token_sequence, self.n)

    def action(self, target):
        """This acts on a tuple of n tokens, and does nothing if it
        doesn't pass the merge_predicate. It first removes all PHI
        within the range of these n tokens, and then marks the entire
        span of the n tokens as one PHI with name/TYPE/name_tag.
        """
        if not self.merge_predicate(target, self):
            return False

        start, end = target[0].start, target[-1].end

        for phi in phi_within_range(self.sa, start, end):
            self.sa.phi.remove(phi)

        el = etree.Element(self.name,
                           attrib={"start": str(start),
                                   "end": str(end),
                                   "TYPE": self.TYPE,
                                   "comment": "",
                                   "text": self.sa.text[int(start):int(end)]})

        self.sa.phi.append(self.name_tag(el))
