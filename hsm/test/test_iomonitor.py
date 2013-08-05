# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import unittest
import socket

from hsm import runtime
from hsm import initial_state, TopState


class Monitor(TopState):
    def on_data_incoming(self, socket):
        pass

    def on_data_outgoing(self, socket):
        pass

    def on_data_except(self, socket):
        pass


@initial_state
class MonitorReady(Monitor):
    pass


class TestIOMonitor(unittest.TestCase):
    def setUp(self):
        runtime.reset()

    def test_insert(self):
        sock = socket.socket()
        obj = Monitor()
        runtime.monitor_readable(sock, obj)
        runtime.monitor_readable(sock, obj)
        runtime.monitor_readable(sock, obj)
        self.assertTrue(sock in runtime._read_list_index.keys())
        self.assertTrue(obj in runtime._read_list_index.values())


    def test_remove(self):
        sock01 = socket.socket()
        sock02 = socket.socket()
        sock03 = socket.socket()
        obj01 = Monitor()
        obj02 = Monitor()
        obj03 = Monitor()

        runtime.monitor_readable(sock01, obj01)
        runtime.monitor_readable(sock02, obj02)
        runtime.monitor_readable(sock03, obj03)
        runtime.monitor_readable(sock01, obj01)
        runtime.monitor_readable(sock02, obj02)
        runtime.monitor_readable(sock03, obj03)
        runtime.monitor_readable(sock01, obj01)
        runtime.monitor_readable(sock02, obj02)
        runtime.monitor_readable(sock03, obj03)

        self.assertTrue(runtime.rlist_index.__len__() == 3)

    def test_remove(self):
        sock01 = socket.socket()
        sock02 = socket.socket()
        sock03 = socket.socket()
        obj01 = Monitor()
        obj02 = Monitor()
        obj03 = Monitor()

        runtime.monitor_readable(sock01, obj01)
        runtime.monitor_readable(sock02, obj02)
        runtime.monitor_readable(sock03, obj03)

        self.assertTrue(sock01 in runtime._read_list_index.keys())
        self.assertTrue(sock02 in runtime._read_list_index.keys())
        self.assertTrue(sock03 in runtime._read_list_index.keys())

        self.assertTrue(obj01 in runtime._read_list_index.values())
        self.assertTrue(obj02 in runtime._read_list_index.values())
        self.assertTrue(obj03 in runtime._read_list_index.values())

        runtime.unmonitor_readable(sock02)

        self.assertTrue(sock01 in runtime._read_list_index.keys())
        self.assertTrue(sock02 not in runtime._read_list_index.keys())
        self.assertTrue(sock03 in runtime._read_list_index.keys())

        self.assertTrue(obj01 in runtime._read_list_index.values())
        self.assertTrue(obj02 not in runtime._read_list_index.values())
        self.assertTrue(obj03 in runtime._read_list_index.values())

        #Twice
        runtime.unmonitor_readable(sock02)

        self.assertTrue(sock01 in runtime._read_list_index.keys())
        self.assertTrue(sock02 not in runtime._read_list_index.keys())
        self.assertTrue(sock03 in runtime._read_list_index.keys())

        self.assertTrue(obj01 in runtime._read_list_index.values())
        self.assertTrue(obj02 not in runtime._read_list_index.values())
        self.assertTrue(obj03 in runtime._read_list_index.values())

        runtime.unmonitor_readable(sock01)

        self.assertTrue(sock01 not in runtime._read_list_index.keys())
        self.assertTrue(sock02 not in runtime._read_list_index.keys())
        self.assertTrue(sock03 in runtime._read_list_index.keys())

        self.assertTrue(obj01 not in runtime._read_list_index.values())
        self.assertTrue(obj02 not in runtime._read_list_index.values())
        self.assertTrue(obj03 in runtime._read_list_index.values())

        runtime.unmonitor_readable(sock03)

        self.assertTrue(sock01 not in runtime._read_list_index.keys())
        self.assertTrue(sock02 not in runtime._read_list_index.keys())
        self.assertTrue(sock03 not in runtime._read_list_index.keys())

        self.assertTrue(obj01 not in runtime._read_list_index.values())
        self.assertTrue(obj02 not in runtime._read_list_index.values())
        self.assertTrue(obj03 not in runtime._read_list_index.values())


if __name__ == '__main__':
    unittest.main()
