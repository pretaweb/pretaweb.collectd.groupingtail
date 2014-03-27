from ..helpers import *
import os
import unittest
from nose.tools import assert_equal, assert_true, assert_false
from mock import MagicMock, patch
from pretaweb.collectd.groupingtail.instruments import NUM32

HERE = os.path.dirname(__file__)
more_small_log_file = os.path.join(HERE, '..', 'logs', 'more_small.txt')
simple_log_file = os.path.join(HERE, '..', 'logs', 'simple.txt')
second_simple_log_file = os.path.join(HERE, '..', 'logs', 'second_simple.txt')
basic_small_log_file = os.path.join(HERE, '..', 'logs', 'basic_small.txt')
group_by = '^\\S+ \\[\\S+ \"[^\"]*\" \"[^\"]*\"[^]]*] (\\S+) '


def int_cast(x):
    return int(x) % NUM32


class TestGroupingTail(object):
    collectd_mock = MagicMock()
    modules = patch.dict('sys.modules', {'collectd': collectd_mock})

    def setup(self):
        self.modules.start()

    def teardown(self):
        self.modules.stop()


class TestConfig(TestGroupingTail):

    @staticmethod
    def test_basic_config():
        """
            Test basic function for grouping tail.
        """
        from pretaweb.collectd.groupingtail.plugin import configure, read
        config = CollectdConfig('root', (), (
            ('File', more_small_log_file, (
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

    @staticmethod
    def test_basic_counter_inc():
        """
            Test basic counter inc function for grouping tail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterInc

        counter_inc = CounterInc('.')
        grouping_tail = GroupingTail(simple_log_file, '^(\d)')
        grouping_tail.add_match('simple', 'counter', counter_inc)
        grouping_tail.update()

        assert_equal(len(counter_inc.data), 4)
        assert_true('3' in counter_inc.data)
        assert_equal(counter_inc.data['3'], 3)
        assert_true('2' in counter_inc.data)
        assert_equal(counter_inc.data['2'], 2)
        assert_true('1' in counter_inc.data)
        assert_equal(counter_inc.data['1'], 1)
        assert_true('8' in counter_inc.data)
        assert_equal(counter_inc.data['8'], 1)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_inc.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.simple')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

    @staticmethod
    def test_basic_counter_sum():
        """
            Test basic counter sum function for grouping tail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterSum

        counter_sum = CounterSum('^(\d)')
        grouping_tail = GroupingTail(simple_log_file, '^(\d)')
        grouping_tail.add_match('simple', 'counter', counter_sum)
        grouping_tail.update()

        assert_equal(len(counter_sum.data), 4)
        assert_true('3' in counter_sum.data)
        assert_equal(counter_sum.data['3'], 9.0)
        assert_true('2' in counter_sum.data)
        assert_equal(counter_sum.data['2'], 4.0)
        assert_true('1' in counter_sum.data)
        assert_equal(counter_sum.data['1'], 1.0)
        assert_true('8' in counter_sum.data)
        assert_equal(counter_sum.data['8'], 8.0)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_sum.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.simple')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

    @staticmethod
    def test_counter_inc():
        """
            Test counter_inc function for grouping tail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterInc

        counter_inc = CounterInc('.')
        grouping_tail = GroupingTail(basic_small_log_file, group_by)
        grouping_tail.add_match('requests', 'counter', counter_inc)
        grouping_tail.update()
        assert_equal(len(counter_inc.data), 1)
        assert_true('domain_com' in counter_inc.data)
        assert_equal(counter_inc.data['domain_com'], 10)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_inc.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.requests')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

    @staticmethod
    def test_counter_sum():
        """
            Test counter_sum function for grouping tail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterSum

        counter_sum = CounterSum('^\\S+ \\[\\S+ \"[^\"]*\" \"[^\"]*\"[^]]*] \\S+ \\S+ .+ HTTP\\S+ [0-9]+ ([0-9]+) ',
                                 value_cast=int_cast)
        grouping_tail = GroupingTail(basic_small_log_file, group_by)
        grouping_tail.add_match('tx', 'counter', counter_sum)
        grouping_tail.update()
        assert_equal(len(counter_sum.data), 1)
        assert_true('domain_com' in counter_sum.data)
        assert_equal(counter_sum.data['domain_com'], 15680)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_sum.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.tx')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

    @staticmethod
    def test_multi_counter_inc():
        """
            Test counter_inc function for grouping tail class on multi domain.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterInc

        counter_inc = CounterInc('.')
        grouping_tail = GroupingTail(more_small_log_file, group_by)
        grouping_tail.add_match('requests', 'counter', counter_inc)
        grouping_tail.update()
        #print counter_inc.data
        assert_equal(len(counter_inc.data), 1)
        assert_true('www_domain_info' in counter_inc.data)
        assert_equal(counter_inc.data['www_domain_info'], 3)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_inc.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.requests')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

    @staticmethod
    def test_multi_counter_sum():
        """
            Test counter_sum function for grouping tail class on multi domain.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterSum

        counter_sum = CounterSum('^\\S+ \\[\\S+ \"[^\"]*\" \"[^\"]*\"[^]]*] \\S+ \\S+ .+ HTTP\\S+ [0-9]+ ([0-9]+) ',
                                 value_cast=int_cast)
        grouping_tail = GroupingTail(more_small_log_file, group_by)
        grouping_tail.add_match('tx', 'counter', counter_sum)
        grouping_tail.update()
        #print counter_sum.data
        assert_equal(len(counter_sum.data), 1)
        assert_true('www_domain_info' in counter_sum.data)
        assert_equal(counter_sum.data['www_domain_info'], 95268)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_sum.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.tx')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)


class TestMultiFiles(TestGroupingTail):

    @staticmethod
    def test_basic_multi_files():
        """
            Test basic tail multi files function for grouping tail class.
        """
        from pretaweb.collectd.groupingtail.groupingtail import GroupingTail
        from pretaweb.collectd.groupingtail.instruments import CounterInc

        counter_inc = CounterInc('.')
        grouping_tail = GroupingTail(simple_log_file, '^(\d)')

        second_counter_inc = CounterInc('.')
        second_grouping_tail = GroupingTail(second_simple_log_file, '^(\d)')

        grouping_tail.add_match('simple', 'counter', counter_inc)
        grouping_tail.update()

        third_counter_inc = CounterInc('.')
        third_grouping_tail = GroupingTail(simple_log_file, '^(\D)')

        second_grouping_tail.add_match('second_simple', 'counter', second_counter_inc)
        second_grouping_tail.update()

        third_grouping_tail.add_match('third_simple', 'counter', third_counter_inc)
        third_grouping_tail.update()

        assert_equal(len(counter_inc.data), 4)
        assert_true('3' in counter_inc.data)
        assert_equal(counter_inc.data['3'], 3)
        assert_true('2' in counter_inc.data)
        assert_equal(counter_inc.data['2'], 2)
        assert_true('1' in counter_inc.data)
        assert_equal(counter_inc.data['1'], 1)
        assert_true('8' in counter_inc.data)
        assert_equal(counter_inc.data['8'], 1)

        assert_equal(len(second_counter_inc.data), 2)
        assert_true('3' in second_counter_inc.data)
        assert_equal(second_counter_inc.data['3'], 4)
        assert_true('2' in second_counter_inc.data)
        assert_equal(second_counter_inc.data['2'], 1)
        assert_false('1' in second_counter_inc.data)

        assert_equal(len(third_counter_inc.data), 2)
        assert_true('w' in third_counter_inc.data)
        assert_equal(third_counter_inc.data['w'], 3)
        assert_true('y' in third_counter_inc.data)
        assert_equal(third_counter_inc.data['y'], 1)
        assert_false('z' in third_counter_inc.data)

        read_metrics = grouping_tail.read_metrics()

        for key, key_value in counter_inc.data.items():
            metric_name, value_type, value = read_metrics.next()
            assert_equal(metric_name, str(key) + '.simple')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

        second_read_metrics = second_grouping_tail.read_metrics()

        for key, key_value in second_counter_inc.data.items():
            metric_name, value_type, value = second_read_metrics.next()
            assert_equal(metric_name, str(key) + '.second_simple')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)

        third_read_metrics = third_grouping_tail.read_metrics()

        for key, key_value in third_counter_inc.data.items():
            metric_name, value_type, value = third_read_metrics.next()
            assert_equal(metric_name, str(key) + '.third_simple')
            assert_equal(value_type, 'counter')
            assert_equal(value, key_value)