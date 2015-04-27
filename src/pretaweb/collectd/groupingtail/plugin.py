
import re
from time import sleep
import collectd

from groupingtail import GroupingTail
from conftools import getConfFirstValue, getConfChildren, read_config



#
# Configuration
#

files = None

def configure(conf):

    global files
    files = read_config(conf)



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
