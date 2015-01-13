.. contents::

Introduction
============

The groupingtail collectd plugin is very similar to the built in `collectd tail plugin`
execept that instead of reporting on single predefined stats, it can break down stats
by grouping them based on values in the log itself. For example, if a value in the log
is a hostname, then this plugin can report on metrics for each hostname sepretley without
having to predefine the hostnames.
In addition it can take its input from syslog udp streams not just files.

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
    
Each ``File`` element takes the log path as the first attribute. The log can also be a url
in the form of syslog://host:port.
Inside the element are the following
configuration items:

- ``Instance`` - this is the metric name to use in collectd
- ``GroupBy`` - Expression to extract the grouping value in each logline. The is a regular
  expression and the first group match becomes the value used. For example if the log line
  contained ``127.0.0.1 example.com 1234`` and your
  expression was ``^\S+ (\S+)`` then the grouping value would be ``example.com``. (Please note
  that collectd configuration syntax requires strings to be escaped - eg ``\`` is represented by ``\\``)
- Series of ``<Match>..</Match>`` elements - These define the metrics you want to measure

Example file definition ::

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

The match elements contains the following configuration items:

- ``Instance`` - this is the metric name to use in collectd
- ``Regex`` - the regular expression to use for the metric. If the ``DSType`` below requries a value
  it will be the first group match in the expression
- ``DSType`` - the collectd dataset type - currently supported is ``CounterInc`` and ``CounterSumInt``
- ``Type`` - the data type in collectd


Instance Names and Grouping Retention
=====================================
 
The resulting metric Instance name is constructed with the following syntac::

  FileInstanceName.GroupValue.MatchInstanceName
 
Groupingtail should return values if they are collected within a collectd cycle. Grouping tail keeps
a list of recently used group values (currenly hard coded to a maximum 64 group values) So if no logline
is captured then then an appropriately value is returned for that group for each match metric.

_... `collectd tail plugin`:https://collectd.org/wiki/index.php/Plugin:Tail