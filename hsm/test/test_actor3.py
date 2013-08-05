# coding=utf-8
# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

import unittest
import traceback

from hsm import TopState, initial_state, error_state
from hsm import runtime as runtime_actor

#Test state hierarchy:
# ObjTopState
#  - ObjMachineUpState *
#     - ObjStandbyState *
#     - ObjActiveState
#  - ObjMachineDownState
#     - ObjNotActiveState *
#  - ObjMachineErrorState


class ObjTopState(TopState):
    def __init__(self):
        super(TopState, self).__init__()
        self._error = None

    def on_raise(self, ex_msg):
        raise Exception(ex_msg)

    def on_fatal_error(self):
        self.transition(ObjErrorState)

    def on_problem(self, problem_type):
        if problem_type == "WARNING":
            self.transition(ObjStandbyState)
        else:
            self.transition(ObjNotActiveState)

    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )


@error_state
class ObjErrorState(ObjTopState):
    def on_except(self, (exc_type, exc_value, exc_traceback)):
        self._error = exc_value
        tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for trace in tb:
            self._log.trace(trace.remove)


@initial_state
class ObjMachineUpState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )


class ObjMachineDownState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )

    def on_problem_resolved(self):
        self.transition(ObjActiveState)


class ObjMachineErrorState(ObjTopState):
    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )


@initial_state
class ObjStandbyState(ObjMachineUpState):
    def on_switch_active(self):
        self.transition(ObjActiveState)

    def on_problem_resolved(self):
        self.transition(ObjActiveState)

    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )


class ObjActiveState(ObjMachineUpState):
    def on_switch_standby(self):
        self.transition(ObjStandbyState)

    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )


@initial_state
class ObjNotActiveState(ObjMachineDownState):
    def _enter(self):
        print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
        print "exit %s State" % (self.get_state_name(), )

    def on_problem_resolved(self):
        self.transition(ObjActiveState)


class ActorTest2(unittest.TestCase):
    def test_base(self):
        obj = ObjTopState()
        st = obj.get_state()
        self.assertTrue(ObjStandbyState == st)
        obj.send_switch_active()

        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjActiveState == st)

        obj.send_problem("WARNING")
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjStandbyState == st)

        obj.send_problem_resolved()
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjActiveState == st)

        obj.send_problem("Error")
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjNotActiveState == st)

        obj.send_raise("raise error")
        runtime_actor.dispatch_all_msg()
        st = obj.get_state()
        self.assertTrue(ObjErrorState == st)
        self.assertTrue(obj._error.message == "raise error")

