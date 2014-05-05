import re
from datetime import datetime

NUM32 = 2 ** 32

class Instrument (object):
    
    def __init__ (self, regex, maxgroups=64, value_cast=float):
        
        self.test = re.compile(regex)
        self.maxgroups = maxgroups
        self.value_cast = value_cast

        data = None
        groups = None
        self.reset()

    def reset(self):
        """Empty bucket and start again"""
        self.data = {}
        self.groups = {}

    def touch_group (self, groupname):
        self.groups[groupname] = datetime.now()

    def trim_groups (self):
        """Trim groups which haven't been touched"""
        items = self.groups.items()
        items.sort()
        self.groups = dict(items[:self.maxgroups])

    def normalise (self):
        """Create newdata with only the members of self.groups and wrap around large integers"""
        newdata = {}
        for groupname in self.groups.keys():
            newdata[groupname] = self.value_cast(self.data[groupname])
        self.data = newdata

    def read(self):
        """Return the current results of the bucket"""
        self.trim_groups()
        self.normalise()
        return self.data.items()

    def append_data (self, groupname, line, mo):
        """do actual data analysis"""
        raise NotImplementedError()

    def write (self, groupname, line):
        """analise log line"""

        mo = self.test.match(line)
        if mo is not None:
            try:
                self.append_data(groupname, line, mo)
            except ValueError:
                pass
            except:
                # the instrument failed.
                self.reset()
            else:
                self.touch_group(groupname)


class Guage (Instrument):
    def read(self):
        values = super(Guage, self).read()
        self.reset()
        return values


class CounterInc (Instrument):

    def __init__ (self, *args, **kwargs):
        kwargs["value_cast"] = (lambda x: int(x) % NUM32)
        super (CounterInc, self).__init__ (*args, **kwargs)

    def append_data (self, groupname, line, mo):
        self.data[groupname] = self.data.get(groupname, 0) + 1


class CounterSum (Instrument):
    def append_data (self, groupname, line, mo):
        minimum = self.value_cast(0)
        value = self.value_cast(mo.groups()[0])
        self.data[groupname] = self.data.get(groupname, minimum) + value



class Max (Guage):
    def append_data(self, groupname, line, mo):
        value = self.value_cast(mo.groups()[0])
        current = self.data.get(groupname, None)
        if value > current or current is None:
            self.data[groupname] = value

        