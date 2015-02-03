from pretaweb.collectd.groupingtail.groupingtail import GroupingTail

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


#
# Instruments library and generators
#


from instruments import NUM32, CounterInc, CounterSum


def configure_counterinc (conf):
    regex = getConfFirstValue(conf, 'Regex')
    return CounterInc(regex)

def configure_countersumint (conf):
    regex = getConfFirstValue(conf, "Regex")
    groupname = getConfFirstValue(conf, "GroupName", None)
    value_cast = value_cast=(lambda x: int(x) % NUM32 )
    return CounterSum(regex, value_cast=value_cast, groupname=groupname)

INSTRUMENTS = {
        "CounterInc": configure_counterinc,
        "CounterSumInt": configure_countersumint
    }



def read_config(conf):

    files = []

    for f in getConfChildren(conf, "File"):

        instance_name = getConfFirstValue(f, 'Instance')
        filepath = f.values[0]
        groupby = getConfFirstValue(f, 'GroupBy')
        groupbygroup = getConfFirstValue(f, 'GroupName', None)
        maxgroups = int(getConfFirstValue(f, 'MaxGroups', 64))

        gt = GroupingTail(filepath, groupby, groupbygroup)

        files.append(dict(
                instance_name=instance_name,
                grouping_tail=gt
            ))

        for m in getConfChildren(f, 'Match'):

            minstance_name = getConfFirstValue(m, "Instance")
            valuetype = getConfFirstValue(m, "Type")

            # dstype determins the instrument used
            dstype = getConfFirstValue(m, "DSType")
            instrument = INSTRUMENTS[dstype](m)

            gt.add_match (minstance_name, valuetype, instrument)
    return files
