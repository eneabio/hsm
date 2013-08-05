# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

__author__ = 'Fabio N. Filasieno'

import unittest

from hsm import *


class MainLoopTalker(TopState):
    pass


@initial_state
class MainLoopTalkerReady(MainLoopTalker):
    def on_hello(self):
        print "hello"


class TestLogger(unittest.TestCase):
    def test_post_quit(self):
        runtime.send_quit()
        sig = runtime.peek_sig()
        self.assertEquals("quit", sig)
        is_empty = runtime.is_msg_queue_empty()
        self.assertFalse(is_empty)
        runtime.clear_msg_queue()
        is_empty = runtime.is_msg_queue_empty()
        self.assertTrue(is_empty)

    def test_dialogue(self):
        talker = MainLoopTalker()

        class MainLoop(object):

            def __init__(self):
                self.counter = 0

            def __call__(self, ):
                if self.counter > 3:
                    runtime.send_quit()
                else:
                    talker.send_hello()
                    self.counter += 1


        loop = MainLoop()
        runtime.run(loop)
        self.assertEquals(loop.counter, 4)