.. contents::

Introduction
============

Similar to the collectd Tail plugin but with two enhancements

 - It can be used with a syslog udp stream not just a file.
 - you can group lines based on a regular expression

For example

    <Module "pretaweb.collectd.groupingtail.plugin">
        <File "syslog://127.0.0.1:514">
            Instance "nginx_stats"
            # Unescaped GroupBy which groups by hostname ^\S+ \[\S+ "[^"]*" "[^"]*"[^]]*] (\S+)
            GroupBy "^\\S+ \\[\\S+ \"[^\"]*\" \"[^\"]*\"[^]]*] (\\S+) "
            <Match>
                Instance "requests"
                Regex "."
                DSType "CounterInc"
                Type "counter"
            </Match>
        </File>
    </Module>

In this example the host is matched by (\\S+). The hostname is then used as part of the metric name and instead of counting
the total requests we will measure it per host.