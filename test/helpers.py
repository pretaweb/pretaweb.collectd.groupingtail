import os

HERE = os.path.dirname(__file__)


def fixture(name):
    return open(os.path.join(HERE, 'fixtures', name)).read()


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