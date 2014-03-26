from ..helpers import *
import os

log_file = '/tmp/groupingtail_test.log'
group_by = '^\\S+ (\\S+) '

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

    def test_basic_config(self):
        """
            Test basic function for groupingtail.
        """
        from pretaweb.collectd.groupingtail.plugin import configure, read
        config = CollectdConfig('root', (), (
            ('File', log_file, (
                ('Instance', 'my_stats', ()),
                ('GroupBy', group_by, ()),
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


class TestFunction(TestGroupingTail):

    def test_counter_inc(self):
        """
            Test counter_inc function for groupingtail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterInc

        gt = GroupingTail(log_file, group_by)
        gt.add_match('requests', 'counter', CounterInc('.'))

        for metric_name, value_type, value in gt.read_metrics():
            assert_equal(metric_name, 'metric_name')
            assert_equal(value_type, 'value_type')
            assert_equal(value, 'value')

    def test_counter_sum(self):
        """
            Test counter_sum function for groupingtail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import NUM32, CounterSum

        gt = GroupingTail(log_file, group_by)

        def intcast(x):
            return int(x) % NUM32

        gt.add_match('tx', 'counter', CounterSum('^\\S+ \\S+ ([0-9]+)', value_cast=intcast))

        for metric_name, value_type, value in gt.read_metrics():
            assert_equal(metric_name, 'metric_name')
            assert_equal(value_type, 'value_type')
            assert_equal(value, 'value')
