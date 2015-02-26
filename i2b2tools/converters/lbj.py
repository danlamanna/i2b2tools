from i2b2tools.helpers.utils import has_overlapping_phi
from i2b2tools.lib.standoff_annotations import StandoffAnnotation
from i2b2tools.converters import TYPE_name_mapping

from lxml import etree
import re

lbj_type_mapping = {
    "PER": "NAME",
    "LOC": "LOCATION-OTHER",
    "ORG": "ORGANIZATION",
    "MISC": "OTHER"
}

TYPE_lbj_name_mapping = {
    "NAME": "PER",
    "PATIENT": "PER",
    "DOCTOR": "PER",
    "USERNAME": "PER",
    "ROOM": "LOC",
    "DEPARTMENT": "LOC",
    "HOSPITAL": "LOC",
    "STREET": "LOC",
    "CITY": "LOC",
    "STATE": "LOC",
    "COUNTRY": "LOC",
    "ZIP": "LOC",
    "LOCATION-OTHER": "LOC",
    "ORGANIZATION": "ORG"
}

def lbj_to_standoff_annotation(lbj_input,
                               lbj_type_mapping=lbj_type_mapping,
                               mapping=TYPE_name_mapping):
    """
    Note: The format in which LBJ outputs documents is not uniform in
    repsect to whitespace and punctuation, so if lbj_input was
    created by LBJ (as opposed to converting SA -> LBJ) this has to
    recreate the tokens as best it can.
    This was addressed on the mailing list here:
    http://lists.cs.uiuc.edu/pipermail/illinois-ml-nlp-users/2014-June/000307.html
    """
    lbj_tags_re = re.compile(r"\[(%s)\s(.+?)\s{2}\]" %
                             "|".join(lbj_type_mapping.keys()))

    standoff_etree = etree.Element("deIdi2b2")
    etree.SubElement(standoff_etree, "TEXT")
    etree.SubElement(standoff_etree, "TAGS")

    tags = re.findall(lbj_tags_re, lbj_input)
    sa_text = re.sub(lbj_tags_re, "\\2 ", lbj_input)

    search_offset = 0

    standoff_etree.find("TEXT").text = etree.CDATA(sa_text)

    for (i, tag) in enumerate(tags):
        tag_type, tag_text = tag
        TYPE = lbj_type_mapping[tag_type]
        name = mapping.get(TYPE, TYPE)

        search_offset = sa_text.find(tag_text, search_offset)

        etree.SubElement(standoff_etree.find("TAGS"),
                         name,
                         id="P%d" % i,
                         start=str(search_offset),
                         end=str(search_offset + len(tag_text)),
                         text=str(tag_text),
                         TYPE=TYPE,
                         comment="")

    return etree.tostring(standoff_etree, pretty_print=True)

def standoff_to_lbj(sa, TYPE_name_mapping=TYPE_lbj_name_mapping):
    def start_of_phi(sa, position):
        for phi in sa.get_phi():
            if phi.get_start() == position:
                return phi

    def end_of_phi(sa, position):
        for phi in sa.get_phi():
            if phi.get_end() == position:
                return phi

    assert isinstance(sa, StandoffAnnotation)

    if has_overlapping_phi(sa):
        raise Exception("Conversion behavior is undefined with overlapping PHI")

    text = ""

    for (i, character) in enumerate(sa.text):
        start = start_of_phi(sa, i)
        end = end_of_phi(sa, i)

        if start:
            lbj_type = TYPE_name_mapping.get(start.TYPE, "MISC")

        if start and end:
            text += "  ][%s %s" % (lbj_type, character)
        elif start:
            text += "[%s %s" % (lbj_type, character)
        elif end:
            text += "  ]%s" % character
        else:
            text += character

    return text
