import hsm

from hsm import actor
from hsm import runtime


# Machine (simple hsm) ############################################

class Machine(actor.TopState):

    def __init__(self):
	pass

    def _enter(self):
	pass

    def _exit(self):
	pass
    
    def error(self):
	self.transition(MachineError)

@actor.initial_state
class Off(Machine):

    def on_switch_on(self):
	self.transition(On)

class On(Machine):

    def on_switch_off(self):
	    self.transition(Off) 
	    
@actor.initial_state
class WaitCommand(On):

    def on_start_server(self):
	    self.transition(WaitConnection) 

class WaitConnection(On):

    def on_stop_server(self):
	    self.transition(WaitCommand)

class MachineError(Machine):

    def _error(self):
	print "Error"

if __name__ == '__main__':

    print "test simple hsm"
    mac = Machine()
    st = mac.get_state()
    assert(Off == st)
    mac.send_switch_on()
    runtime.dispatch_all_msg()
    st = mac.get_state()
    assert(WaitCommand == st)
    mac.send_error()
    runtime.dispatch_all_msg()
    st = mac.get_state()
    assert(MachineError == st)    