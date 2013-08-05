# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import unittest

from hsm import iomonitor
from hsm import actor

import socket

class Monitor(actor.TopState):

    def on_data_incoming(self, socket):
        pass
    def on_data_outgoing(self, socket):
        pass
    def on_data_except(self, socket):
        pass

@actor.initial_state
class MonitorReady(Monitor):
    pass

class TestIOMonitor(unittest.TestCase):

    def setUp(self):
        iomonitor.reset()

    def test_insert(self):
        sock = socket.socket()
        obj = Monitor()
        iomonitor.monitor_readable(sock, obj)
        iomonitor.monitor_readable(sock, obj)
        iomonitor.monitor_readable(sock, obj)
        self.assertTrue(sock in iomonitor.rlist_index.keys())
        self.assertTrue(obj in iomonitor.rlist_index.values())


    def test_remove(self):
        sock01 = socket.socket()
        sock02 = socket.socket()
        sock03 = socket.socket()
        obj01 = Monitor()
        obj02 = Monitor()
        obj03 = Monitor()

        iomonitor.monitor_readable(sock01, obj01)
        iomonitor.monitor_readable(sock02, obj02)
        iomonitor.monitor_readable(sock03, obj03)
        iomonitor.monitor_readable(sock01, obj01)
        iomonitor.monitor_readable(sock02, obj02)
        iomonitor.monitor_readable(sock03, obj03)
        iomonitor.monitor_readable(sock01, obj01)
        iomonitor.monitor_readable(sock02, obj02)
        iomonitor.monitor_readable(sock03, obj03)

        self.assertTrue(iomonitor.rlist_index.__len__() == 3)

    def test_remove(self):
        sock01 = socket.socket()
        sock02 = socket.socket()
        sock03 = socket.socket()
        obj01 = Monitor()
        obj02 = Monitor()
        obj03 = Monitor()

        iomonitor.monitor_readable(sock01, obj01)
        iomonitor.monitor_readable(sock02, obj02)
        iomonitor.monitor_readable(sock03, obj03)

        self.assertTrue(sock01 in iomonitor.rlist_index.keys())
        self.assertTrue(sock02 in iomonitor.rlist_index.keys())
        self.assertTrue(sock03 in iomonitor.rlist_index.keys())

        self.assertTrue(obj01 in iomonitor.rlist_index.values())
        self.assertTrue(obj02 in iomonitor.rlist_index.values())
        self.assertTrue(obj03 in iomonitor.rlist_index.values())

        iomonitor.unmonitor_incoming(sock02)

        self.assertTrue(sock01 in iomonitor.rlist_index.keys())
        self.assertTrue(sock02 not in iomonitor.rlist_index.keys())
        self.assertTrue(sock03 in iomonitor.rlist_index.keys())

        self.assertTrue(obj01 in iomonitor.rlist_index.values())
        self.assertTrue(obj02 not in iomonitor.rlist_index.values())
        self.assertTrue(obj03 in iomonitor.rlist_index.values())

        #Twice
        iomonitor.unmonitor_incoming(sock02)

        self.assertTrue(sock01 in iomonitor.rlist_index.keys())
        self.assertTrue(sock02 not in iomonitor.rlist_index.keys())
        self.assertTrue(sock03 in iomonitor.rlist_index.keys())

        self.assertTrue(obj01 in iomonitor.rlist_index.values())
        self.assertTrue(obj02 not in iomonitor.rlist_index.values())
        self.assertTrue(obj03 in iomonitor.rlist_index.values())

        iomonitor.unmonitor_incoming(sock01)

        self.assertTrue(sock01 not in iomonitor.rlist_index.keys())
        self.assertTrue(sock02 not in iomonitor.rlist_index.keys())
        self.assertTrue(sock03 in iomonitor.rlist_index.keys())

        self.assertTrue(obj01 not in iomonitor.rlist_index.values())
        self.assertTrue(obj02 not in iomonitor.rlist_index.values())
        self.assertTrue(obj03 in iomonitor.rlist_index.values())

        iomonitor.unmonitor_incoming(sock03)

        self.assertTrue(sock01 not in iomonitor.rlist_index.keys())
        self.assertTrue(sock02 not in iomonitor.rlist_index.keys())
        self.assertTrue(sock03 not in iomonitor.rlist_index.keys())

        self.assertTrue(obj01 not in iomonitor.rlist_index.values())
        self.assertTrue(obj02 not in iomonitor.rlist_index.values())
        self.assertTrue(obj03 not in iomonitor.rlist_index.values())

if __name__ == '__main__':
    unittest.main()