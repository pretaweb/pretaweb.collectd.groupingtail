import os
import uuid
import re
from pygtail import Pygtail


class GroupingTail (object):

    def __init__(self, filepath, groupby, groupbygroup=None):

        self.groupmatch = re.compile(groupby)

        # write an offset file so that we start somewhat at the end of the file
       
        self.offsetpath = "/tmp/" + str(uuid.uuid4())
        #print self.offsetpath
        try:
            inode = os.stat(filepath).st_ino
            offset = os.path.getsize(filepath) - 1024
            #print inode
            #print offset
        except OSError:
            pass
        else:
            if offset > 0:
                #print 'write offset'
                foffset = open(self.offsetpath, "w")
                foffset.write ("%s\n%s" % (inode, offset))
                foffset.close()

        self.fin = Pygtail(filepath, offset_file=self.offsetpath, copytruncate=True)
        #self.fin.readlines()

        self.match_definitions = []
        self.groupbygroup = groupbygroup

    def update(self):
        for line in self.fin.readlines():
            #print 'line: %s' % line
            groupname = None
            mo = self.groupmatch.match(line)
            if mo is not None:
                if self.groupbygroup is None and mo.groups():
                    groupname = mo.groups()[0]
                else:
                    res = res.groupdict()
                    groupname = res.get(self.groupbygroup)
            if groupname is not None:
                groupname = groupname.replace(".", "_").replace("-", "_")
                for match in self.match_definitions:
                    instrument = match["instrument"]
                    instrument.write(groupname, line)

    def add_match(self,  instance_name, valuetype, instrument):
        self.match_definitions.append(dict(
            instance_name=instance_name,
            valuetype=valuetype,
            instrument=instrument
        ))

    def read_metrics(self):
        for match in self.match_definitions:
            instance_name = match["instance_name"]
            instrument = match["instrument"]
            valuetype = match["valuetype"]

            for groupname, value in instrument.read():
                metric_name = "%s.%s" % (groupname, instance_name)
                yield (metric_name, valuetype, value)
