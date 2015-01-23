import os
import threading
import uuid
import re
from pygtail import Pygtail
import urlparse
import SocketServer
import Queue


class SyslogUDPHandler(SocketServer.BaseRequestHandler):

    def __init__(self, address, handler, queue):
        self.queue = queue
        super(self, SyslogUDPHandler).__init__(address, handler)

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        #print( "%s : " % self.client_address[0], str(data))
        self.queue.put(str(data))

class QueueFile:

    def __init__(self):
        self.queue = Queue.Queue()

    def readlines(self):
        while not self.queue.empty():
            yield self.get()



class GroupingTail (object):

    def __init__(self, filepath, groupby, groupbygroup=None):

        self.groupmatch = re.compile(groupby)

        # write an offset file so that we start somewhat at the end of the file

        # either filepath is a path or a syslogd url
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(filepath)
        if scheme == 'syslog':
            host, port = netloc.split(':')
            self.fin = QueueFile()
            def make_handler(address, handler, server):
                return SyslogUDPHandler(address, handler, self.fin)
            server = SocketServer.UDPServer((host, int(port)), make_handler)

            th = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.5))
            th.daemon = True
            th.start()

        else:

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
