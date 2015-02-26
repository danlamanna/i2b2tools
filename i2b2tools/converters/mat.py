from i2b2tools.converters import TYPE_name_mapping, deidi2b2_etree

from lxml import etree

def mat_json_to_standoff(mat_json, mapping=TYPE_name_mapping):
    def v2_annotations():
        annotations = []

        # get rid of annotations standoff/inline doesn't support
        mat_json["asets"] = [x for x in mat_json["asets"] \
                             if x["type"] not in internal_types]

        # setup annotations in a sane format
        # (TYPE, start, end)
        for aset in mat_json["asets"]:
            for annot in aset["annots"]:
                annotations.append((aset["type"], annot[0], annot[1]))

        return annotations

    internal_types = ("SEGMENT",
                      "zone",
                      "lex")

    assert isinstance(mat_json, dict)
    assert ("version" in mat_json and \
            "signal" in mat_json and \
            "asets" in mat_json)

    # only supporting version 2 right now
    assert mat_json["version"] == 2

    # create the initial etree
    standoff_etree = deidi2b2_etree(mat_json["signal"])

    # setup annotations
    for (i, annot) in enumerate(v2_annotations()):
        TYPE, start, end = annot

        etree.SubElement(standoff_etree.find("TAGS"),
                         mapping.get(TYPE, TYPE),
                         id="P%d" % i,
                         start=str(start),
                         end=str(end),
                         text=mat_json["signal"][start:end],
                         TYPE=TYPE,
                         comment="")

    return etree.tostring(standoff_etree, pretty_print=True)
