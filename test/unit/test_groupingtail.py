from ..helpers import *
import os

log_file = '/tmp/groupingtail_test.log'


class TestGroupingTail(object):
    def setup(self):
        self.collectd = MagicMock()
        self.modules = patch.dict('sys.modules', {'collectd': self.collectd})
        self.modules.start()

        # create tmp log file
        if os.path.isfile(log_file):
            os.remove(log_file)

        with open(log_file, 'w') as f:
            for i in range(10):
                f.write(str(i) + '\n')

    def teardown(self):
        #if os.path.isfile(log_file):
        #    os.remove(log_file)
        self.modules.stop()


class TestConfig(TestGroupingTail):

    def test_basic(self):
        """
            Test basic function for groupingtail.
        """
        from pretaweb.collectd.groupingtail.plugin import configure, read
        config = CollectdConfig('root', (), (
            ('File', log_file, (
                ('Instance', 'my_stats', ()),
                ('GroupBy', '^\\S+ (\\S+) ', ()),
                ('Match', (), (
                    ('Instance', 'requests', ()),
                    ('Regex', '.', ()),
                    ('DSType', 'CounterInc', ()),
                    ('Type', 'counter', ()),
                )),
                ('Match', (), (
                    ('Instance', 'tx', ()),
                    ('Regex', '^\\S+ \\S+ ([0-9]+)', ()),
                    ('DSType', 'CounterSumInt', ()),
                    ('Type', 'counter', ()),
                )),
            )),
        ))

        configure(config)
        read()

        #assert_equal(files, [])
