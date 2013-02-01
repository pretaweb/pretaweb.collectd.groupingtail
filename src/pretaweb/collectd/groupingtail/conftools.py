

_getConfFirstValue_NOVAL = object()
def getConfFirstValue(ob, key, default=_getConfFirstValue_NOVAL):
    for o in ob.children:
        if o.key == key:
            return o.values[0]
    if default == _getConfFirstValue_NOVAL:
        raise KeyError()
    return default

def getConfChildren(ob, key):
    children = []
    for o in ob.children:
        if o.key == key:
            children.append(o)
    return children

