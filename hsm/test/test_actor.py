from actor import ActorTopState, initial
from runtime import *

#Test state hierarchy:
# ObjTopState
#  - ObjErrorState
#  - ObjLeftState
#     - ObjLeftChildState *
#     - ObjLeftChildState2 *
#  - ObjRightState *
#     - ObjRightChildState *
#

class ObjTopState(ActorTopState):
	
	def __init__(self, ctx):
		self._ctx = ctx 

	def on_fatal_error(self):
		print "FatalError"
		self.transition(ObjErrorState)

class ObjErrorState(ObjTopState):

	def _enter(self):
		print "entered Error State"

@initial
class ObjLeftState(ObjTopState):

	def _enter(self):
		print "Enter Left State"

	def _exit(self):
		print "Exit Left State"

	def on_update(self):
		self.transition(ObjRightState)

@initial
class ObjLeftChildState(ObjLeftState):

	def _enter(self):
		print str(str(self._ctx))
		print "Enter Left Child State"

	def _exit(self):
		print "Exit Left Child State"

	def on_update(self):
		self.transition(ObjRightState)
	
class ObjLeftChildState2(ObjLeftState):
	pass	

class ObjRightState(ObjTopState):

	def on_update(self):
		self._transition(ObjLeftState)

	def on_sample(self):
		print "Sample received"

@initial
class ObjRightChildState(ObjRightState):

	def on_update(self):
		self.transition(ObjLeftState)


obj = ObjTopState({"x":10})
obj.transition(ObjLeftChildState)
obj.transition(ObjLeftChildState2)
obj.transition(ObjTopState)

obj.send_fatal_rrror()
obj.send_fini()

while True:
	msg = get_msg()
	if not msg:
		break
	dispatch_msg(msg)