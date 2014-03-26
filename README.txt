.. contents::

Introduction
============

Collectd plugin to tail a log file and group metrics by some value in the log file.

The configuration is a series of ``<File "/path/to/file">...</Flie>`` elements contained
in the plugin definition as follows::

    Import "pretaweb.collectd.groupingtail.plugin"
    <Module "pretaweb.collectd.groupingtail.plugin">
        <File "/path/to/my/log/file">
            # file configuration goes here
        </File>
        <File "/path/to/my/log/file2">
            # file configuration goes here
        </File>
        ...
    </Module>
    
Each ``File`` element takes the log path as the first attribute. Inside the element it contains
the metric ``Instance`` name and a ``GroupBy`` regular expression by which to group the metrics by. The
grouping field is the first regular expresion group match in the expression (that is the first match contained
in parentasies in the expression. For example if the log line contained "127.0.0.1 example.com 1234" and your
expression was ``^\S+ (\S+)`` then the grouping value would be ``example.com``. Please note you need to 
follow the escape pattens for collectd - slashes forinstance need to be escaped.
The File element then contains a series of ``<Match>...</Match>`` elements which defin the metrics to mesure::

    <File "/path/to/my/log/file">
        Instance "my_stats" 
        GroupBy "^\\S+ (\\S+) "
        <Match>
            Instance "requests"
            Regex "."
            DSType "CounterInc"
            Type "counter"
        </Match>
        <Match>
            Instance "tx"
            Regex "^\\S+ \\S+ ([0-9]+)"
            DSType "CounterSumInt"
            Type "counter"
        </Match>
    </File>

The match elements contains the following properties:

- ``Instance`` - this is the metric name to use in collectd
- ``Regex`` - the regular expression to use for the metric
- ``DSType`` - the collectd dataset type - currently supported is ``CounterInc`` and ``CounterSumInt``
- ``Type`` - the data type in collectd
 
For DSTypes which take a value such as CounterSumInt it is the grouped expression inside Regex



 
