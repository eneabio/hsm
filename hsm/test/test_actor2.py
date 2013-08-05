# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import unittest

from hsm import TopState, initial_state
from hsm import runtime

runtime_actor = runtime


#Test state hierarchy:
# ObjTopState
#  - ObjErrorState
#  - ObjCState
#     - ObjDState *
#     - ObjEState
#  - ObjAState *
#     - ObjBState *

class ObjTopState(TopState):
    def on_fatal_error(self):
        print "FatalError"
        self.transition(ObjErrorState)

    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


class ObjErrorState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


@initial_state
class ObjAState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )

        #def on_update(self):
        #self.transition(ObjRightState)


@initial_state
class ObjBState(ObjAState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )

        #def on_update(self):
        #self.transition(ObjRightState)


class ObjCState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


@initial_state
class ObjDState(ObjCState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


class ObjEState(ObjCState):
    def _enter(self):
        print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
        print "exit %s State" % (self.__class__.__name__, )


class ActorTest2(unittest.TestCase):
    def test_self_transition(self):
        obj = ObjTopState()
        st = obj.get_state()
        self.assertTrue(ObjBState == st)

    def test_transition_to_current_state(self):
        obj = ObjTopState()
        obj.transition(ObjBState)
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjBState == st)

    def test_different_parent_transition(self):
        obj = ObjTopState()
        obj.transition(ObjCState)
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjDState == st)

    def test_ancestor_transition(self):
        obj = ObjTopState()
        obj.transition(ObjTopState)
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjBState == st)

    def test_msg_send(self):
        obj = ObjTopState()
        obj.send_fatal_error()
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjErrorState == st)

    def test_fini(self):
        obj = ObjTopState()
        obj.send_fini()
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        print st