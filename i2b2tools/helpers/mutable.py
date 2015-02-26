from i2b2tools.lib.standoff_annotations import StandoffAnnotation

def sa_filter_by_phi_attrs(sa, attrs):
    def _filter(phi):
        for (k, v) in attrs.iteritems():
            try:
                # the attribute is incorrect, fails filter
                if phi.__dict__[k] != v:
                    return False
            except KeyError:
                # the attribute doesn't exist, so it fails filter
                return False

        # all attributes (which could be 0, passed) so it passes the filter
        return True

    return [phi for phi in sa.get_phi() if _filter(phi)]

def remap_sa_attributes(sa, from_attrs, to_attrs):
    """This is a mutable function, so it will in fact call
    StandoffAnnotation.save which will attempt to overwrite the file on
    disk.

    So if somehow PHI that had a name of DATE were actually supposed to
    have a name of PHONE, you could perform this operation to a
    StandoffAnnotation:
    remap_sa_attributes(sa, {"name": "DATE"}, {"name": "PHONE"})
    """
    if not isinstance(sa, StandoffAnnotation):
        raise Exception("Argument passed is not a StandoffAnnotation.")

    for phi in sa_filter_by_phi_attrs(sa, from_attrs):
        for (key, value) in to_attrs.iteritems():
            phi.__dict__[key] = value

    sa.save()
