
import re
import collectd

from groupingtail import GroupingTail
from conftools import getConfFirstValue, getConfChildren


#
# Instruments library and generators
#


from instruments import NUM32, CounterInc, CounterSum

def configure_counterinc (conf):
    regex = getConfFirstValue(conf, 'Regex')
    return CounterInc(regex)

def configure_countersumint (conf):
    regex = getConfFirstValue(conf, "Regex")
    value_cast = value_cast=(lambda x: int(x) % NUM32 )
    return CounterSum(regex, value_cast=value_cast)

INSTRUMENTS = {
        "CounterInc": configure_counterinc,
        "CounterSumInt": configure_countersumint
    }



#
# Configuration
#

files = None

def configure (conf):

    global files
    files = []

    for f in getConfChildren(conf, "File"):

        instance_name = getConfFirstValue(f, 'Instance')
        filepath = f.values[0]
        groupby = getConfFirstValue(f, 'GroupBy')
        maxgroups = int(getConfFirstValue(f, 'MaxGroups', 64))

        gt = GroupingTail(filepath, groupby)
        
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



#
# Getting mesurements
#

def update():
    for f in files:
        f["grouping_tail"].update()

def read ():

    # this might be good in another thread
    update()

    for f in files:
        instance_name = f["instance_name"]
        gt = f["grouping_tail"]

        for metric_name, value_type, value in gt.read_metrics():
            v = collectd.Values(
                    plugin='groupingtail',
                    plugin_instance="%s.%s" % (instance_name, metric_name),
                    type = value_type,
                    values = (value,)
                )
            v.dispatch()




# Register functions with collectd

collectd.register_config(configure)
collectd.register_read(read)
