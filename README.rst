.. contents::

Introduction
============

Collectd plugin to tail a log file and group metrics by some value in the log file. It tries to 
closly mirror the tail plugin already in collectd

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
    
Each ``File`` element takes the log path as the first attribute. Inside the element are the following
configuration items:

- ``Instance`` - this is the metric name to use in collectd
- ``GroupBy`` - Expression to extract the grouping value in each logline. The is a regular
  expression and the first group match becomes the value used. For example if the log line
  contained ``127.0.0.1 example.com 1234`` and your
  expression was ``^\S+ (\S+)`` then the grouping value would be ``example.com``. (Please note
  that collectd configuration syntax requires strings to be escaped - eg ``\`` is represented by ``\\``)
- Series of ``<Match>..</Match>`` elements - These define the metrics you want to mesure

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


 
