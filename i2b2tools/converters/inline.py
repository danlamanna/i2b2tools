from i2b2tools.helpers.utils import has_overlapping_phi
from i2b2tools.lib.standoff_annotations import StandoffAnnotation
from i2b2tools.converters.common import *

from lxml import etree

"""Potential Improvements:
- These conversions follow the same pattern over and over, it could
potentially be abstracted.
- LBJ output format is inconsistent, once it changes this could be enhanced.
"""

def standoff_to_inline(sa):
    """This takes a StandoffAnnotation and returns an etree element,
    which can be converted to a string with etree.tostring.

    This doesn't currently working with overlapping PHI.
    """
    def start_of_phi(sa, position):
        for phi in sa.get_phi():
            if phi.get_start() == position:
                return phi

    def end_of_phi(sa, position):
        for phi in sa.get_phi():
            if phi.get_end() == position:
                return phi

    def create_tag(tree, tag, text):
        etree.SubElement(tree, tag).text = text

    def append_string(tree, s):
        """To properly append a string to an XML document, the string
        has to be appended to the last tags tail, or if there isn't a tag
        yet - the trees text property."""
        tags = tree.getchildren()

        if tags:
            tags[-1].tail = s
        else:
            tree.text = s

    assert isinstance(sa, StandoffAnnotation)

    if has_overlapping_phi(sa):
        raise Exception("Conversion behavior is undefined with overlapping PHI")

    tree = etree.Element("ROOT")
    buf = ""

    for (i, character) in enumerate(sa.text):
        """
        If we're at the start of a PHI tag, AND the end of a PHI tag:
        - Create the tag that we're at the end of
        - Set the new buffer to be the current character
        Otherwise if it's just the start of a PHI tag:
        - Append the buffer to the end of the document
        - Set the new buffer to be the current character
        Otherwise if it's just the end of a PHI tag:
        - Create the tag that we're at the end of
        - Set the new buffer to the current character

        For any other case, just add the character to the buffer.
        """
        start = start_of_phi(sa, i)
        end = end_of_phi(sa, i)

        if start and end:
            create_tag(tree, end.TYPE, buf)
        elif start:
            append_string(tree, buf)
        elif end:
            create_tag(tree, end.TYPE, buf)

        if start or end:
            buf = character
        else:
            buf += character

    # Spit out the final characters
    append_string(tree, buf)

    return tree

def inline_to_standoff(inline_xml, mapping=TYPE_name_mapping):
    """This takes and returns a string. It's up to the user to write the
    string to a file and call StandoffAnnotation on it.

    The one catch is the function is uncertain how to take an inline
    tag such as CITY and map is to a tag with a TYPE and name. So the
    user can pass a mapping which is a dictionary of TYPEs mapped to
    names. By default we use TYPE_name_mapping.

    In addition the inline_xml must be wrapped in a root element so
    it is considered valid XML, so if your string is in the form of:
    These are some <some_tag>words</some_tag>.

    It needs to be wrapped like so:
    <some_root_tag>These are some <some_tag>words</some_tag>.</some_root_tag>
    """
    inline = etree.fromstring(inline_xml)

    standoff_etree = etree.Element("deIdi2b2")
    etree.SubElement(standoff_etree, "TEXT")
    etree.SubElement(standoff_etree, "TAGS")

    standoff_text, offset = inline.text, len(inline.text)

    for (i, inline_tag) in enumerate(inline.getchildren()):
        append = inline_tag.text + (inline_tag.tail if inline_tag.tail else "")
        standoff_text += append

        etree.SubElement(standoff_etree.find("TAGS"),
                         mapping.get(inline_tag.tag, inline_tag.tag),
                         id="P%d" % i,
                         start=str(offset),
                         end=str(offset + len(inline_tag.text)),
                         text=str(inline_tag.text),
                         TYPE=inline_tag.tag,
                         comment="")


        offset += len(append)

    standoff_etree.find("TEXT").text = etree.CDATA(standoff_text)

    return etree.tostring(standoff_etree, pretty_print=True)
