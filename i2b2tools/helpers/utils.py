from i2b2tools.lib.standoff_annotations import StandoffAnnotation

from lxml import etree
import os

def is_valid_sa_file(filename):
    """Determines if a given file would constitute a valid StandoffAnnotation.
    It will return false if the file doesn't exist, or if it contains invalid
    XML.
    """
    try:
        with open(filename, "r") as infile:
            root = etree.fromstring(infile.read())
            children = [el.tag for el in root.getchildren()]

        return (root.tag == "deIdi2b2" and
                "TEXT" in children and
                "TAGS" in children)

    # handles the cases of a non-readable file, or an invalid xml file
    except (IOError, etree.XMLSyntaxError):
        return False

def get_sa_from_dir(dirname):
    """Returns a dictionary in the format of:
    {"id": <StandoffAnnotation>}

    This is determined by finding all filenames within dirname that pass
    is_valid_sa_file.
    """
    sas = []

    for filename in os.listdir(dirname):
        filename = os.path.join(dirname, filename)

        if is_valid_sa_file(filename):
            sas.append(StandoffAnnotation(filename))

    return dict(zip([sa.id for sa in sas], sas))

def has_overlapping_phi(sa):
    """Determines if a given StandoffAnnotation has any PHI that overlap."""
    if not isinstance(sa, StandoffAnnotation):
        raise Exception("Argument passed is not a StandoffAnnotation.")

    phi = sorted(sa.get_phi(), key=lambda tag: tag.get_start())

    # no phi -> no overlapping phi
    if not phi:
        return False

    prev = phi[0]

    for tag in phi[1:]:
        if prev.get_end() > tag.get_start():
            return True
        else:
            prev = tag

    return False

def phi_at_offset(sa, offset):
    """Returns a list of PHI that are present at a given offset in a
    StandoffAnnotation.
    """
    return [phi for phi in sa.get_phi() \
            if offset >= phi.get_start() and offset <= phi.get_end()]

def phi_within_range(sa, start, end):
    """Finds all PHI within a given range of offsets in the
    StandoffAnnotation.
    """
    def point_in_range(point):
        return point >= start and point <= end

    return [phi for phi in sa.get_phi() \
            if point_in_range(phi.get_start()) or point_in_range(phi.get_end())]
