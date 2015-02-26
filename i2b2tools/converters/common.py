from lxml import etree

TYPE_name_mapping = {
    "NAME": "NAME",
    "PATIENT": "NAME",
    "DOCTOR": "NAME",
    "USERNAME": "NAME",
    "PROFESSION": "PROFESSION",
    "ROOM": "LOCATION",
    "DEPARTMENT": "LOCATION",
    "HOSPITAL": "LOCATION",
    "ORGANIZATION": "LOCATION",
    "STREET": "LOCATION",
    "CITY": "LOCATION",
    "STATE": "LOCATION",
    "COUNTRY": "LOCATION",
    "ZIP": "LOCATION",
    "LOCATION-OTHER": "LOCATION",
    "AGE": "AGE",
    "DATE": "DATE",
    "PHONE": "CONTACT",
    "FAX": "CONTACT",
    "EMAIL": "CONTACT",
    "URL": "CONTACT",
    "IPADDR": "CONTACT",
    "SSN": "ID",
    "MEDICALRECORD": "ID",
    "HEALTHPLAN": "ID",
    "ACCOUNT": "ID",
    "LICENSE": "ID",
    "VEHICLE": "ID",
    "DEVICE": "ID",
    "BIOID": "ID",
    "IDNUM": "ID",
    "OTHER": "OTHER"
}

def deidi2b2_etree(text=None, cdata=True):
    standoff_etree = etree.Element("deIdi2b2")
    etree.SubElement(standoff_etree, "TEXT")
    etree.SubElement(standoff_etree, "TAGS")

    if text is not None:
        if cdata:
            standoff_etree.find("TEXT").text = etree.CDATA(text)
        else:
            standoff_etree.find("TEXT").text = text

    return standoff_etree
