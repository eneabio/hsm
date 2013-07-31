# Copyright (C) 2013 Fabio N. Filasieno
# Licenced under the MIT license
# see LICENCE.txt

from hsm import actor
from hsm import runtime
import unittest

#Test state hierarchy:
# ObjTopState
#  - ObjMachineUpState *
#     - ObjStandbyState *
#     - ObjActiveState
#  - ObjMachineDownState
#     - ObjNotActiveState *
#  - ObjMachineErrorState

class ObjTopState(actor.ActorTopState):

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

@actor.initial
class ObjMachineUpState(ObjTopState):

    def _enter(self):
	print "enter %s State" % (self.get_state_name() )

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

@actor.initial
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

@actor.initial
class ObjNotActiveState(ObjMachineDownState):

    def _enter(self):
	print "enter %s State" % (self.get_state_name(), )

    def _exit(self):
	print "exit %s State" % (self.get_state_name(), )

    def on_problem_resolved(self):
	self.transition(ObjActiveState)

class ActorTest2(unittest.TestCase):

    def test_hfsm_state(self):
	obj = ObjTopState()
	st = obj.get_state()
	self.assertTrue(ObjStandbyState == st)
	obj.send_switch_active()

	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjActiveState == st)

	obj.send_problem("WARNING")
	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjStandbyState == st)

	obj.send_problem_resolved()
	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjActiveState == st)

	obj.send_problem("Error")
	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjNotActiveState == st)