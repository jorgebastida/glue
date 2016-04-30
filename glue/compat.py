import sys

PY3 = sys.version_info[0] == 3

if PY3:  # pragma: no cover
    text_type = str
    binary_type = bytes

    def itervalues(d):
        return d.values()

    def iterkeys(d):
        return d.keys()

    def iteritems(d):
        return d.items()

else:  # pragma: no cover
    text_type = unicode
    binary_type = str

    def itervalues(d):
        return d.itervalues()

    def iterkeys(d):
        return d.iterkeys()

    def iteritems(d):
        return d.iteritems()
