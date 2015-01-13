
# small commandline version for debugging. Takes a .json file with the config

import optparse
import json
from time import sleep
from pretaweb.collectd.groupingtail.conftools import read_config


class CollectdConfig(object):
    """
    Quacks like collectd Config object.
    """
    def __init__(self, key, values, children):
        self.key = key
        self.values = (values,)
        self.children = [
            CollectdConfig(children_key, children_values, children_children)
            for children_key, children_values, children_children in children
        ]

def main():
    p = optparse.OptionParser()
    p.add_option('--config', '-c', default="groupingtail.json")
    options, arguments = p.parse_args()
    with open(options.config) as config_file:
        config = json.load(config_file)

    config = CollectdConfig('root', (), config)

    files = read_config(config)
    while True:
        sleep(5)
        #update
        for f in files:
            f["grouping_tail"].update()

        for f in files:
            instance_name = f["instance_name"]
            gt = f["grouping_tail"]

            for metric_name, value_type, value in gt.read_metrics():
                print "%s.%s: %s=%s" % (instance_name, metric_name, value_type, value)


if __name__ == '__main__':
    main()


