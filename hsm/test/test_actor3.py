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
#     - ObjNotActiveState 
#     - ObjCheckProblemState * 
#  - ObjMachineErrorState


class ObjTopState(actor.ActorTopState):

    def on_fatal_error(self):
	self.transition(ObjErrorState)
"""
    def _enter(self):
	print "enter %s State" % (self.__class__.__name__, )

    def _exit(self):
	print "exit %s State" % (self.__class__.__name__, )
"""

@actor.initial
class ObjMachineUpState(ObjTopState):
    pass

class ObjMachineDownState(ObjTopState):
    pass

class ObjMachineErrorState(ObjTopState):   

 	print "FatalError"

@actor.initial
class ObjStandbyState(ObjMachineUpState):  

	def on_switch_active(self):
	    self.transition(ObjActiveState)

class ObjActiveState(ObjMachineUpState):  

	def on_switch_standby(self):
	    self.transition(ObjStandbyState)

	def on_problem(self):
	    self.transition(ObjCheckProblemState)
	    msg = self.get_msg
	    if msg[0] == "WARNING":
		self.send_warning(self.get_msg[1])
	    else:
		self.send_error(self.get_msg[1])

class ObjNotActiveState(ObjMachineDownState):   

	def on_problem_resolved(self):
	    self.transition(ObjCheckProblemState)


@actor.initial
class ObjCheckProblemState(ObjMachineDownState):

	def on_error(self):
	    self.transition(ObjNotActiveState)

	def on_warning(self):
	    self.transition(ObjStandbyState)

	def on_repaired(self):
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

"""
    def test_different_parent_transition(self):
	obj = ObjTopState()
	obj.transition(ObjCState)
	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjDState == st)

    def test_ancestor_transition(self):
	obj = ObjTopState()
	obj.transition(ObjTopState)
	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjBState == st)

    def test_msg_send(self):
	obj = ObjTopState()
	obj.send_fatal_error()
	runtime.dispatch_all_msg()
	st = obj.get_state()
	self.assertTrue(ObjErrorState == st)

    def test_fini(self):
	obj = ObjTopState()
	obj.send_fini()
	runtime.dispatch_all_msg()
	st = obj.get_state()
	print st
"""

#obj.send_fini()
#while True:
    #msg = get_msg()
    #if not msg:
	#break
    #dispatch_msg(msg)